// How heads are built, versioned by common sense as the engine's formats are: each part's version goes up when what
// it makes changes on purpose (not for a refactoring that leaves its results as they were). What is stored because it
// is slow to make (a wrap: data/wraps/) is keyed by its version, so a result of older code is never read for newer;
// the numbers check keeps these versions beside each head's numbers and names the part whose version changed when a
// head moved (check/numbers.mjs).
//   wrap         src/head/wrap.js: Anny's head laid onto a designed form
//   picture      src/head/features.js faceUV, src/head/paint.js: where each vertex is in the face's picture, the mask,
//                the drawing itself
//   expressions  src/head/expressions.js: the expressions' morphs
//   pieces       src/head/pieces.js: noses, hair, headwear and how they follow the skin
//   hair         src/hair/build.js, styles.js: В1's hairstyles as built in their design space (stored: data/hair/)
export const HEAD_BUILD = { wrap: 2, picture: 2, expressions: 2, pieces: 3, hair: 5 };
