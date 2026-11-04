// Reading a pack — the engine's plain data file (tools/pack.py writes it): a JSON header, and beside it a binary file
// of little-endian arrays the header lists ({dtype, shape, offset}). In a browser by fetch; in node by `read`
// (check/node-read.mjs). `hash` is the pack's content hash (src/hash.js: the header's canonical JSON and the bytes).
import { hashOf } from './hash.js';

const KINDS = { float32: Float32Array, float64: Float64Array, uint32: Uint32Array, int32: Int32Array, uint16: Uint16Array, int16: Int16Array, uint8: Uint8Array };

export async function loadPack(url, read = defaultRead) {
  const header = JSON.parse(new TextDecoder().decode(await read(url)));
  const buf = await read(new URL(header.bin, url));
  const arrays = {};
  for (const [key, m] of Object.entries(header.arrays)) {
    const Kind = KINDS[m.dtype];
    if (!Kind) throw new Error(`${url}: ${key} has an unknown type ${m.dtype}`);
    const n = m.shape.reduce((a, b) => a * b, 1);
    if (m.offset + n * Kind.BYTES_PER_ELEMENT > buf.byteLength) throw new Error(`${url}: ${key} runs past the end of ${header.bin}`);
    arrays[key] = new Kind(buf.slice(m.offset, m.offset + n * Kind.BYTES_PER_ELEMENT));
  }
  return { header, arrays, hash: hashOf([header, buf]) };
}

// a pack's two files from a header and its arrays ({key: {array (typed), shape?}}, in the order given): {json (text),
// bin (bytes)} — each array starts at a multiple of 4 bytes, as tools/pack.py writes them
export function packOf(header, arrays, bin) {
  const meta = {}, chunks = []; let at = 0;
  for (const [key, { array: a, shape = [a.length] }] of Object.entries(arrays)) {
    const dtype = Object.keys(KINDS).find(k => a instanceof KINDS[k]); if (!dtype) throw new Error(`${key}: not a pack type`);
    const bytes = new Uint8Array(a.buffer, a.byteOffset, a.byteLength), pad = (4 - bytes.length % 4) % 4;
    meta[key] = { dtype, shape, offset: at }; chunks.push(bytes, new Uint8Array(pad)); at += bytes.length + pad;
  }
  const out = new Uint8Array(at); let o = 0; for (const c of chunks) { out.set(c, o); o += c.length; }
  return { json: JSON.stringify({ ...header, bin, arrays: meta }, null, 1) + '\n', bin: out };
}

export async function defaultRead(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.arrayBuffer();
}
export const readJSON = async (url, read = defaultRead) => JSON.parse(new TextDecoder().decode(await read(url)));
