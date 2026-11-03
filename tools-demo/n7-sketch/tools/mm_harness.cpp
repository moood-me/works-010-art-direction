// Drives Monster Mash's modelling core from code instead of the mouse.
// It repeats, step by step, what the app does when a person draws outlines and switches to the 3D view:
//  - each part is a stroke (polyline) drawn into an outline image with the app's own painter (thickness 3),
//    the gap between its end and start closed with a "Neumann" line as the app does on mouse release,
//    and filled into a region image the same way (MainWindow::handleMouseReleaseEventImageMode, DRAW_OUTLINE);
//  - layers are ordered back to front as given (as with drawing over / under in the app);
//  - performReconstruction() inflates and stitches the parts (the app's switch to the geometry mode);
//  - the ARAP-L deformation engine runs until it settles, as the app's paint loop does;
//  - optional animation: control points are placed on the mesh as with a left click in the animate mode
//    (Def3D::addControlPointOnFace, front view, identity projection) and moved frame by frame, the engine
//    run a few iterations per frame, as the app's playback does.
// Writes rest.obj, parts.txt (part id per vertex: 2*layer + back side) and, with an animation, f0000.obj ...
//
// usage: mm_harness <shape.txt> <outdir> [anim.txt]
// shape.txt:  size W H | inflation A | smooth S | part NAME [inflation] | p x y (one line per stroke point) | end
// anim.txt:   iters K | cp x y | frame  followed by one "d dx dy" line per control point (offset from its start)
#include <igl/writeOBJ.h>
#include <image/imageUtils.h>

#include <fstream>
#include <iostream>
#include <sstream>

#include "commonStructs.h"
#include "mypainter.h"
#include "reconstruction.h"

using namespace std;
using namespace Eigen;

static void writeMesh(const string &fn, const MatrixXd &V, const MatrixXi &F) {
  igl::writeOBJ(fn, V, F);
}

int main(int argc, char **argv) {
  if (argc < 3) {
    cerr << "usage: mm_harness shape.txt outdir [anim.txt]" << endl;
    return 1;
  }
  SDL_Init(0);
  ifstream in(argv[1]);
  const string outDir = argv[2];
  int W = 1000, H = 1000;
  RecData recData;
  DefData defData;
  CPData cpData;
  ImgData imgData;
  const float thickness = 3;  // MainWindow::defaultThickness

  string tok, name;
  vector<Vector2i> pts;
  double partInfl = -1;
  vector<string> names;
  auto finishPart = [&]() {
    Imguc Io(W, H, 1);
    Io.fill(255);
    {
      MyPainter painter(Io);
      painter.setColor(0, 0, 0, 255);
      for (size_t i = 1; i < pts.size(); i++)
        painter.drawLine(pts[i - 1](0), pts[i - 1](1), pts[i](0), pts[i](1), thickness);
    }
    // close the drawn shape (as the app does on mouse release)
    Imguc tmp;
    tmp.initImage(Io);
    tmp.fill(255);
    {
      MyPainter painter(tmp);
      painter.setColor(NEUMANN_OUTLINE_PIXEL_COLOR, NEUMANN_OUTLINE_PIXEL_COLOR,
                       NEUMANN_OUTLINE_PIXEL_COLOR, 255);
      painter.drawLine(pts.front()(0), pts.front()(1), pts.back()(0), pts.back()(1), thickness);
    }
    fora(y, 0, H) fora(x, 0, W) if (Io(x, y, 0) == 255) Io(x, y, 0) = tmp(x, y, 0);
    Imguc Ir = Io;
    floodFill(Ir, 0, 0, 255, 128);
    fora(y, 0, H) fora(x, 0, W) Ir(x, y, 0) = Ir(x, y, 0) == 128 ? 0 : 255;
    imgData.outlineImgs.push_back(Io);
    imgData.regionImgs.push_back(Ir);
    const int regId = imgData.regionImgs.size() - 1;
    imgData.layers.push_back(regId);
    if (partInfl > 0) recData.regionInflationAmount[regId] = partInfl;
    names.push_back(name);
    pts.clear();
    partInfl = -1;
  };
  string line;
  while (getline(in, line)) {
    istringstream ls(line);
    if (!(ls >> tok)) continue;
    if (tok == "size") ls >> W >> H;
    else if (tok == "inflation") ls >> recData.defaultInflationAmount;
    else if (tok == "smooth") ls >> recData.smoothFactor;
    else if (tok == "part") { ls >> name; if (!(ls >> partInfl)) partInfl = -1; }
    else if (tok == "p") { double x, y; ls >> x >> y; pts.push_back(Vector2i(lround(x), lround(y))); }
    else if (tok == "end") finishPart();
  }
  cerr << "parts: " << imgData.layers.size() << endl;
  imgData.layers.size();
  // the region/outline images, merged, for looking at what was drawn
  {
    Imguc M(W, H, 1);
    M.fill(255);
    for (auto &I : imgData.outlineImgs) fora(y, 0, H) fora(x, 0, W) if (I(x, y, 0) != 255) M(x, y, 0) = I(x, y, 0);
    M.savePNG(outDir + "/outlines.png");
  }

  if (!performReconstruction(recData, defData, cpData, imgData)) {
    cerr << "reconstruction failed" << endl;
    return 2;
  }
  // settle, as the app's paint loop does (repaints while the change is >= 0.01)
  Def3D &def = defData.def;
  Mesh3D &mesh = defData.mesh;
  int it = 0;
  for (; it < 400; it++) {
    double d = defData.defEng.deform(def, mesh);
    if (d < 0.01) break;
  }
  cerr << "settled after " << it << " iterations, " << mesh.VCurr.rows() << " vertices" << endl;
  writeMesh(outDir + "/rest.obj", mesh.VCurr, mesh.F);
  {
    ofstream pf(outDir + "/parts.txt");
    VectorXi pid = VectorXi::Constant(mesh.VCurr.rows(), -1);
    forlist(p, defData.verticesOfParts) for (int v : defData.verticesOfParts[p]) pid(v) = p;
    pf << "# names:";
    for (auto &n : names) pf << " " << n;
    pf << "\n";
    fora(i, 0, pid.size()) pf << pid(i) << "\n";
  }

  if (argc > 3) {
    ifstream an(argv[3]);
    vector<int> cps;
    vector<Vector3d> start;
    int iters = 4, frame = 0;
    vector<Vector2d> offs;
    auto runFrame = [&]() {
      forlist(i, cps) def.getCP(cps[i]).pos = start[i] + Vector3d(offs[i](0), offs[i](1), 0);
      fora(k, 0, iters) defData.defEng.deform(def, mesh);
      char fn[64];
      snprintf(fn, sizeof fn, "/f%04d.obj", frame++);
      writeMesh(outDir + fn, mesh.VCurr, mesh.F);
      offs.clear();
    };
    while (getline(an, line)) {
      istringstream ls(line);
      if (!(ls >> tok)) continue;
      if (tok == "iters") ls >> iters;
      else if (tok == "cp") {
        double x, y;
        ls >> x >> y;
        int idx = -1;
        def.addControlPointOnFace(mesh.VCurr, mesh.F, x, y, 20, false, false, idx);
        if (idx == -1) { cerr << "no surface under cp " << x << " " << y << endl; return 3; }
        cps.push_back(idx);
        start.push_back(def.getCP(idx).pos);
      } else if (tok == "frame") {
        if (!offs.empty()) runFrame();
      } else if (tok == "d") {
        double dx, dy;
        ls >> dx >> dy;
        offs.push_back(Vector2d(dx, dy));
      }
    }
    if (!offs.empty()) runFrame();
    cerr << "frames: " << frame << endl;
  }
  return 0;
}
