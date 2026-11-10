// Reading a pack — the engine's plain data file (tools/pack.py writes it): a JSON header, and beside it a binary file
// of little-endian arrays the header lists ({dtype, shape, offset}). In a browser by fetch; in node by `readFile`.

const KINDS = { float32: Float32Array, uint16: Uint16Array, uint8: Uint8Array, int16: Int16Array, uint32: Uint32Array };

export async function loadPack(url, read = defaultRead) {
  const header = JSON.parse(new TextDecoder().decode(await read(url)));
  const buf = await read(new URL(header.bin, url));
  const arrays = {};
  for (const [key, m] of Object.entries(header.arrays)) {
    const Kind = KINDS[m.dtype];
    if (!Kind) throw new Error(`${url}: ${key} has an unknown type ${m.dtype}`);
    const n = m.shape.reduce((a, b) => a * b, 1);
    arrays[key] = new Kind(buf.slice(m.offset, m.offset + n * Kind.BYTES_PER_ELEMENT));
  }
  return { header, arrays };
}

export async function defaultRead(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.arrayBuffer();
}
export const readJSON = async (url, read = defaultRead) => JSON.parse(new TextDecoder().decode(await read(url)));
