// The coat's skirt kept off the legs: it is skinned to lag the step (a share of the hips), so a leg swung forward
// would come through it; after skinning every vertex of the skirt is moved out of the legs' capsules (thigh and shin,
// the trousers' radii and a margin from the pack), softly, so the cloth lies over the knee instead of being cut by it.
export function skirtOverLegs(pos, range, P, sk, legs) {
  const [r0, r1, r2] = legs.r, s = legs.soft, caps = [];
  for (const sd of ['Left', 'Right']) {
    const a = sk.index[sd + 'Leg'] * 3, b = sk.index[sd + 'Shin'] * 3, c = sk.index[sd + 'Foot'] * 3;
    caps.push([P[a], P[a + 1], P[a + 2], P[b], P[b + 1], P[b + 2], r0, r1], [P[b], P[b + 1], P[b + 2], P[c], P[c + 1], P[c + 2], r1, r2]);
  }
  for (let i = range[0]; i < range[1]; i++) {
    let x = pos[i * 3], y = pos[i * 3 + 1], z = pos[i * 3 + 2];
    for (const [ax, ay, az, bx, by, bz, ra, rb] of caps) {
      const dx = bx - ax, dy = by - ay, dz = bz - az, L2 = dx * dx + dy * dy + dz * dz;
      const t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy + (z - az) * dz) / L2));
      const cx = ax + dx * t, cy = ay + dy * t, cz = az + dz * t, R = ra + (rb - ra) * t;
      const ox = x - cx, oy = y - cy, oz = z - cz, d = Math.hypot(ox, oy, oz);
      if (d >= R + s || d < 1e-6) continue;
      const d2 = d <= R - s ? R : d + (R + s - d) ** 2 / (4 * s), k = d2 / d;
      x = cx + ox * k; y = cy + oy * k; z = cz + oz * k;
    }
    pos[i * 3] = x; pos[i * 3 + 1] = y; pos[i * 3 + 2] = z;
  }
}
