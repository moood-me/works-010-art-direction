// reading the engine's files from disk in node (the browser reads them by fetch)
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
export const read = async url => { const b = await readFile(fileURLToPath(url)); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength); };
