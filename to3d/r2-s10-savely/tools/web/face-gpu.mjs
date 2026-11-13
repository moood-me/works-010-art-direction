// Савелий Петрович's live face: the face's form moved by a few numbers, on top of the skinned body.
// The measures come from face.json (assemble.py):
// eye centres, the ball's radius, the mouth line, the jaw's pivot, in the drawing's units (y down, z toward the
// viewer), and which of the body's vertices are the head, the irises, the moustache and the face's ink marks.
// This is the fast page's face (face.mjs beside it is the face as it was, for the renders and view.html): the same
// fields, worked out in the vertex shader from each vertex's rest place; the page's shader turns the displacement
// with the head and adds it to the skinned place, as face.mjs's apply() did. The processor only sets the numbers.
//
// params (all 0 at rest):
//   up, low  — the upper / lower lid turned over the ball (degrees; up > 0 closes down, low > 0 closes up)
//   jaw      — the jaw opened (degrees, about a pivot below the ear)
//   smile    — the mouth's corners up and back (+) or down (−), the moustache's ends with them
//   wide     — the corners pulled out (an «и»), pucker — drawn in and forward (an «о», «у»)
//   brow     — the brow skin lifted (+) or lowered (−); inner — the inner ends more (sad +, angry −)
//   lookX, lookY — the irises turned (degrees: right on screen in the front view +, down +)
//   iris     — the iris scale (1: as is; < 1 smaller: surprise)
// Each piece is moved by fields over space, so neighbouring pieces (the lip, the moustache over it, a brow mark on
// the brow) move alike. The result is a displacement in the head's rest frame; the page's shader turns it with the head.

// the face's fields in the shader: faceMove(the vertex's rest place) → its displacement (metres, the head's rest
// frame); faceTurn — the head's turn now
const GLSL = d => {
  const f = x => Number(x).toPrecision(9), v = a => `vec3(${a.map(f).join(', ')})`;
  return `
uniform float faceQ[${PARAMS.length}];       // the params, in PARAMS' order
uniform mat3 faceTurn;
attribute vec3 faceKind;
const vec3 EYE_L = ${v(d.eyes[0])}, EYE_R = ${v(d.eyes[1])}, JAW = ${v(d.jaw)};
const float K = ${f(d.K)}, FLOOR = ${f(d.floor)}, RB = ${f(d.rb)}, MY = ${f(d.mouthY)};
void faceRotX(inout vec3 p, vec3 c, float deg, float w) {
  float a = radians(deg) * w, co = cos(a), si = sin(a), y = p.y - c.y, z = p.z - c.z;
  p.y = c.y + y * co + z * si; p.z = c.z - y * si + z * co;
}
void faceRotY(inout vec3 p, vec3 c, float deg) {
  float a = radians(deg), co = cos(a), si = sin(a), x = p.x - c.x, z = p.z - c.z;
  p.x = c.x + x * co + z * si; p.z = c.z - x * si + z * co;
}
float faceGauss(vec3 p, vec3 c, vec3 s) { vec3 e = (p - c) / s; return exp(-dot(e, e)); }
// the lids of one eye: the skin near the ball turns over it, above the eye by up, below by low
void faceLids(inout vec3 p, vec3 c, float up, float low) {
  float w = (1.0 - smoothstep(RB + 2.0, RB + 6.5, distance(p, c))) * smoothstep(-2.0, 3.0, p.z - c.z);
  if (w > 0.0) { if (p.y < c.y) faceRotX(p, c, up, w); else faceRotX(p, c, -low, w); }
}
vec3 faceMove(vec3 at) {
  float ${PARAMS.map((k, n) => `${k} = faceQ[${n}]`).join(', ')};
  // the piece: the head's skin and its marks, the moustache, an iris (left 1, right 2)
  bool head = faceKind.x > 0.5, stache = faceKind.y > 0.5; float eye = faceKind.z;
  vec3 p0 = vec3(at.x / K, FLOOR - at.y / K, at.z / K), p = p0;       // the drawing's units, y down
  if (head) {
    faceLids(p, EYE_L, up, low); faceLids(p, EYE_R, up, low);
    if (jaw != 0.0) {
      float wj = smoothstep(MY - 1.0, MY + 4.0, p.y) * (1.0 - smoothstep(125.0, 150.0, p.y)) * smoothstep(-20.0, 10.0, p.z);
      if (wj > 0.0) faceRotX(p, JAW, jaw, wj);
    }
  }
  if (head || stache) {
    for (int k = 0; k < 2; k++) {
      float side = k == 0 ? 1.0 : -1.0, g = faceGauss(p, vec3(side * 15.0, MY - 1.0, 72.0), vec3(9.0, 7.0, 12.0));
      if (g < 1e-4) continue;
      p += g * vec3(side * (2.0 * max(smile, 0.0) + 3.0 * wide - 3.5 * pucker), -4.5 * smile, -2.0 * abs(smile) - wide + 2.0 * pucker);
    }
    p.z += 2.2 * pucker * faceGauss(p, vec3(0.0, MY, 74.0), vec3(11.0, 7.0, 10.0));
    if (stache) p.y -= 0.08 * jaw * smoothstep(60.0, 85.0, p.y);      // the upper lip lifts the moustache a little
  }
  if (head) for (int k = 0; k < 2; k++) {
    float side = k == 0 ? 1.0 : -1.0;
    p.y -= faceGauss(p, vec3(side * 32.0, 6.0, 70.0), vec3(11.0, 8.0, 30.0)) * brow;
    p.y -= faceGauss(p, vec3(side * 16.0, 6.0, 70.0), vec3(11.0, 8.0, 30.0)) * (brow + inner);
  }
  if (eye > 0.5) {
    vec3 c = eye < 1.5 ? EYE_L : EYE_R;
    faceRotX(p, c, -lookY, 1.0); faceRotY(p, c, lookX);
    p.xy = c.xy + (p.xy - c.xy) * iris;
  }
  return vec3(p.x - p0.x, p0.y - p.y, p.z - p0.z) * K;
}`;
};

export class Face {
  // body: an engine body; data: face.json
  constructor(body, data) {
    // per vertex, which piece it is of (GLSL above)
    this.kind = new Float32Array(body.N * 3);
    const put = (name, [a, b]) => {
      const head = name === 'head' || name === 'mark' ? 1 : 0, stache = name.startsWith('stache') ? 1 : 0;
      const eye = name.startsWith('iris') ? (name.endsWith('L') ? 1 : 2) : 0;
      for (let i = a; i < b; i++) {
        this.kind.set([head, stache, eye], i * 3);
      }
    };
    for (const [name, r] of Object.entries(data.pieces)) put(name, r);
    for (const r of data.marks) put('mark', r);
    this.q = new Float32Array(PARAMS.length); this.turn = new Float32Array(9);
    this.uniforms = { faceQ: { value: this.q }, faceTurn: { value: this.turn } };
    this.glsl = GLSL(data);
  }

  // the face's attributes onto the skin's geometry
  attributes(THREE, geometry) {
    geometry.setAttribute('faceKind', new THREE.BufferAttribute(this.kind, 3));
    return geometry;
  }

  // the face for these params, on a head turned as
  // M says (3×4 rows, skinner.matrix(pose, Head))
  set(q, M) {
    PARAMS.forEach((k, n) => { this.q[n] = (q[k] ?? (k === 'iris' ? 1 : 0)); });
    this.turn.set([M[0], M[4], M[8], M[1], M[5], M[9], M[2], M[6], M[10]]);      // by columns
  }
}

// the five expressions of the drawing's sheet, as params
export const EXPRESSIONS = {
  calm: {},
  joy: { up: 34, low: 14, jaw: 7, smile: 1.0, brow: 2.5 },
  surprise: { up: -14, low: -8, jaw: 6, brow: 7, iris: 0.82 },
  sad: { up: 16, smile: -1.0, brow: 1.5, inner: 4, lookY: 7 },
  anger: { up: 12, low: 6, jaw: 5, smile: -0.8, brow: -4, inner: -5 },
};
export const PARAMS = ['up', 'low', 'jaw', 'smile', 'wide', 'pucker', 'brow', 'inner', 'lookX', 'lookY', 'iris'];

// a mix of expressions: {joy: 0.6, surprise: 0.4} → params
export function mix(weights) {
  const out = {};
  for (const k of PARAMS) out[k] = k === 'iris' ? 1 : 0;
  let tot = 0; for (const w of Object.values(weights)) tot += w;
  for (const [name, w] of Object.entries(weights)) {
    const e = EXPRESSIONS[name];
    for (const k of PARAMS) out[k] += ((k === 'iris' ? (e.iris ?? 1) - 1 : (e[k] || 0))) * w / Math.max(tot, 1);
  }
  return out;
}
