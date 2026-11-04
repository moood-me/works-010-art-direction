// The air hair and clothes move in: a wind preset (presets/wind-*.json, group wind: {speed, dir, gust, turbulence}) as a
// flow at each point and moment, the same for every simulation of a figure (src/hair/sim.js, src/cloth/sim.js).
// the wind at a point: a steady flow (o.speed along o.dir) going through gusts — two waves travelling along the wind,
// slow and quick, the strength o.gust —, a slow swing of each part's own (its seed: a lock's, a garment's), a turbulence round it
// (o.turbulence: its share of the speed across the wind and up), and the flow's small lift
export function windAt(o, x, y, z, t, seed, out) {
  const s = o.speed, d = o.dir, along = x * d[0] + z * d[2], g = o.gust ?? 1, tu = o.turbulence ?? 1;
  const gust = 0.62 + g * (0.3 * Math.sin(t * 1.3 - along * 1.7) * Math.sin(t * 0.47 + 1.3) + 0.22 * Math.sin(t * 3.1 - along * 4 + seed) * Math.sin(t * 0.9 + seed * 0.7));
  const k = s * gust * (0.85 + 0.3 * Math.sin(seed * 5.1 + t * 0.6));
  out[0] = d[0] * k + tu * 0.32 * s * Math.sin(t * 2.3 + y * 7 + seed * 1.7) * Math.sin(t * 0.8 + seed);
  out[1] = d[1] * k + tu * 0.22 * s * Math.sin(t * 2.9 + x * 6 + seed * 2.3) + 0.08 * s;
  out[2] = d[2] * k + tu * 0.32 * s * Math.cos(t * 2.1 + z * 7 + seed * 3.1) * Math.sin(t * 0.7 + seed * 1.3);
  return out;
}
