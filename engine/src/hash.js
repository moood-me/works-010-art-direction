// Content hashes: what pins a body or a motion in a character, a chain or a check, so a change of the data under
// them is refused instead of silently changing them. SHA-256 written out here (crypto.subtle is missing on pages
// not served from a secure origin, e.g. the repository served on a LAN address), over a canonical form: JSON with
// its keys sorted (so whitespace, key order or line endings of a file don't count), then the binary arrays.
//   hashOf([json, bytes, …]) → 64 hex digits;  pinned('moood-woman@3f2a…') → {id, hash}
const K = new Uint32Array([
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01,
  0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
  0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
  0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08,
  0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
  0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]);

export function sha256(bytes) {
  const n = bytes.length, total = Math.ceil((n + 9) / 64) * 64, m = new Uint8Array(total);
  m.set(bytes); m[n] = 0x80;
  const dv = new DataView(m.buffer), bits = n * 8;
  dv.setUint32(total - 8, Math.floor(bits / 2 ** 32)); dv.setUint32(total - 4, bits >>> 0);
  const H = new Uint32Array([0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]);
  const W = new Uint32Array(64), r = (x, k) => (x >>> k) | (x << (32 - k));
  for (let o = 0; o < total; o += 64) {
    for (let i = 0; i < 16; i++) W[i] = dv.getUint32(o + i * 4);
    for (let i = 16; i < 64; i++) {
      const a = W[i - 15], b = W[i - 2];
      W[i] = W[i - 16] + (r(a, 7) ^ r(a, 18) ^ (a >>> 3)) + W[i - 7] + (r(b, 17) ^ r(b, 19) ^ (b >>> 10));
    }
    let [a, b, c, d, e, f, g, h] = H;
    for (let i = 0; i < 64; i++) {
      const t1 = (h + (r(e, 6) ^ r(e, 11) ^ r(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + W[i]) >>> 0;
      const t2 = ((r(a, 2) ^ r(a, 13) ^ r(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) >>> 0;
      h = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = b; b = a; a = (t1 + t2) >>> 0;
    }
    H[0] += a; H[1] += b; H[2] += c; H[3] += d; H[4] += e; H[5] += f; H[6] += g; H[7] += h;
  }
  return Array.from(H, x => x.toString(16).padStart(8, '0')).join('');
}

// JSON with its keys sorted, no spaces: the same data gives the same text
export function canonical(v) {
  if (Array.isArray(v)) return '[' + v.map(canonical).join(',') + ']';
  if (v && typeof v === 'object') return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + canonical(v[k])).join(',') + '}';
  return JSON.stringify(v);
}

// a hash of parts: objects (canonical JSON), strings, or bytes (ArrayBuffer / typed arrays)
export function hashOf(parts) {
  const enc = new TextEncoder(), chunks = parts.map(p => p instanceof ArrayBuffer ? new Uint8Array(p)
    : ArrayBuffer.isView(p) ? new Uint8Array(p.buffer, p.byteOffset, p.byteLength) : enc.encode(typeof p === 'string' ? p : canonical(p)));
  const all = new Uint8Array(chunks.reduce((s, c) => s + c.length + 8, 0));
  let o = 0;
  for (const c of chunks) { new DataView(all.buffer).setUint32(o, c.length); o += 8; all.set(c, o); o += c.length; }  // length-prefixed
  return sha256(all);
}

// "id@hash" (the hash's first digits, at least 12) → {id, hash}; a plain "id" → {id, hash: null}
export const PIN_DIGITS = 16;
export function pinned(ref) {
  const m = /^([A-Za-z0-9_.-]+)(?:@([0-9a-f]{12,64}))?$/.exec(ref);
  if (!m) throw new Error(`"${ref}" is not an id or id@hash`);
  return { id: m[1], hash: m[2] ?? null };
}
export function checkPin(ref, what, hash) {
  const { hash: want } = pinned(ref);
  if (want && !hash.startsWith(want)) throw new Error(`${what} ${ref}: its content is now ${hash.slice(0, PIN_DIGITS)} — it changed under what pinned it (look at the difference, then pin it anew: engine/tools/characters.mjs pin)`);
}
export const pinOf = (id, hash) => `${id}@${hash.slice(0, PIN_DIGITS)}`;
