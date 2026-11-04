"""Blender: film GarmentCode sewing and draping a garment: the cloth points saved by gc_run.py --dump (cm) on the
box mesh's triangles, with the body. blender -b -P render.py-style args:
  -- OUTDIR BODY.obj SKIN BOXMESH.obj FRAMESDIR HEX1/HEX2 [--every N]"""
import bpy, sys, math, glob, os, numpy as np
argv = sys.argv[sys.argv.index('--') + 1:]
outdir, body, skin, box, frames, col = argv[:6]
every = int(argv[argv.index('--every') + 1]) if '--every' in argv else 1
here = os.path.dirname(os.path.abspath(__file__))
# set the scene up as render.py does (one garment: the box mesh), without rendering
sys.argv = ['x', '--', os.path.join(outdir, 'dummy.png'), body, skin, box, col, '--yaw', '20', '--samples', '16', '--size', '480', '720']
src = open(os.path.join(here, 'render.py')).read().replace('bpy.ops.render.render(write_still=True)', '')
exec(compile(src, 'render.py', 'exec'))
cloth = [o for o in bpy.data.objects if o.type == 'MESH' and 'boxmesh' in o.name][0]
files = sorted(glob.glob(os.path.join(frames, '*.npy')))[::every]
me = cloth.data
for k, f in enumerate(files):
    P = np.load(f).astype(np.float64)              # cm, y up (as GarmentCode); the import turned y-up to z-up
    co = np.c_[P[:, 0], -P[:, 2], P[:, 1]]
    me.vertices.foreach_set('co', co.ravel())
    me.update()
    sc.render.filepath = os.path.join(outdir, f'f{k:04d}.png')
    bpy.ops.render.render(write_still=True)
