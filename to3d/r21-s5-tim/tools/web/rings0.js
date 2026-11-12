// geo.lerp_rings: a stack of rings (y, w, d, cx, cz) read at height y, linearly between rings
export function ringTable0(rings) {
  const R = rings.map(r => [r[0], r[1], r[2], r[3] || 0, r[4] || 0]);
  return y => {
    if (y <= R[0][0]) return R[0].slice(1);
    for (let i = 0; i < R.length - 1; i++) {
      const a = R[i], b = R[i + 1];
      if (a[0] <= y && y <= b[0]) { const t = (y - a[0]) / ((b[0] - a[0]) || 1); return [1, 2, 3, 4].map(k => a[k] + (b[k] - a[k]) * t); }
    }
    return R[R.length - 1].slice(1);
  };
}
