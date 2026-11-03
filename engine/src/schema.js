// Checking a description against its schema: every key known, every value of its type and in its range — an unknown
// key or value is refused with where it is, never ignored (a typo would otherwise silently fall back to a default).
// A schema is plain data:
//   {type: 'object', props: {key: schema}, required: [keys]}      other keys refused
//   {type: 'map', values: schema, keys?: [allowed]}                any (or the allowed) keys, each value by `values`
//   {type: 'string', enum?: [...], pattern?: RegExp}   {type: 'number' | 'integer', min?, max?}   {type: 'boolean'}
//   {type: 'array', items: schema, min?, max?}         {type: 'null'}   {const: value}
//   {anyOf: [schemas]}                                 {type: 'union', key: 'kind', cases: {name: object schema}}
export function validate(value, schema, where = '') {
  const at = where || '(top)', fail = m => { throw new Error(`${at}: ${m}`); };
  if (schema.anyOf) {
    const errs = [];
    for (const s of schema.anyOf) { try { validate(value, s, where); return; } catch (e) { errs.push(e.message); } }
    fail(`none of the allowed forms fits — ${errs.join('; or ')}`);
  }
  if ('const' in schema) { if (value !== schema.const) fail(`must be ${JSON.stringify(schema.const)}, is ${JSON.stringify(value)}`); return; }
  const t = schema.type;
  if (t === 'null') { if (value !== null) fail(`must be null`); return; }
  if (t === 'boolean') { if (typeof value !== 'boolean') fail(`must be true or false`); return; }
  if (t === 'string') {
    if (typeof value !== 'string') fail(`must be a string`);
    if (schema.enum && !schema.enum.includes(value)) fail(`"${value}" is not one of ${schema.enum.map(v => `"${v}"`).join(', ')}`);
    if (schema.pattern && !schema.pattern.test(value)) fail(`"${value}" is not of the form ${schema.pattern}`);
    return;
  }
  if (t === 'number' || t === 'integer') {
    if (typeof value !== 'number' || !Number.isFinite(value)) fail(`must be a number`);
    if (t === 'integer' && !Number.isInteger(value)) fail(`must be a whole number`);
    if (schema.min != null && value < schema.min) fail(`${value} is below ${schema.min}`);
    if (schema.max != null && value > schema.max) fail(`${value} is above ${schema.max}`);
    return;
  }
  if (t === 'array') {
    if (!Array.isArray(value)) fail(`must be a list`);
    if (schema.min != null && value.length < schema.min) fail(`needs at least ${schema.min} items`);
    if (schema.max != null && value.length > schema.max) fail(`takes at most ${schema.max} items`);
    value.forEach((v, i) => validate(v, schema.items, `${where}[${i}]`));
    return;
  }
  if (t === 'object' || t === 'map' || t === 'union') {
    if (!value || typeof value !== 'object' || Array.isArray(value)) fail(`must be an object`);
    if (t === 'union') {
      const kind = value[schema.key];
      if (!(kind in schema.cases)) fail(`${schema.key} "${kind}" is not one of ${Object.keys(schema.cases).map(v => `"${v}"`).join(', ')}`);
      return validate(value, schema.cases[kind], where);
    }
    if (t === 'map') {
      for (const [k, v] of Object.entries(value)) {
        if (schema.keys && !schema.keys.includes(k)) fail(`unknown key "${k}" (known: ${schema.keys.join(', ')})`);
        validate(v, schema.values, where ? `${where}.${k}` : k);
      }
      return;
    }
    for (const k of Object.keys(value)) if (!(k in schema.props)) fail(`unknown key "${k}" (known: ${Object.keys(schema.props).join(', ')})`);
    for (const k of schema.required || []) if (!(k in value)) fail(`"${k}" is missing`);
    for (const [k, s] of Object.entries(schema.props)) if (k in value) validate(value[k], s, where ? `${where}.${k}` : k);
    return;
  }
  throw new Error(`a schema without a type at ${at}`);
}
