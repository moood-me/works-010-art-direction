// Parts over the parts they start from — a head's form, features, expressions and pieces over its base's and its
// preset's (src/engine.js headOf), a character's clothes over its base's and its outfits' (src/cloth/clothes.js): each
// of `own` by its id (`id(part)`), in order —
//   {kind: "off", id | name}   takes theirs away (refused if there is none)
//   {id, …keys} (no kind)      changes only the keys it gives, then the part is checked whole (schema); with none of
//                              that id it is refused, unless parts have no kind (expressions: `kindless`), when it is new
//   a whole part               takes the place of theirs, or comes after them
import { validate } from './schema.js';

export function overParts(base, own, id, schema, what, kindless = false) {
  const out = base.slice();
  for (const o of own) {
    const k = out.findIndex(x => id(x) === id(o));
    if (o.kind === 'off') { if (k < 0) throw new Error(`${what} "${id(o)}" to take away: there is none`); out.splice(k, 1); continue; }
    if (!o.kind && k >= 0) { out[k] = { ...out[k], ...o }; if (schema) validate(out[k], schema, `${what} ${id(o)}`); continue; }
    if (!o.kind && !kindless) throw new Error(`${what} "${id(o)}" to change: there is none`);
    if (k >= 0) out[k] = o; else out.push(o);
  }
  return out;
}
