# The problem

## What is wrong now

Pavel, looking at renders of published moood games (The Canterville Ghost, The Fall of the House of Usher, Cinema
Paradiso, The Lady with the Dog):

- **It is not the level of a game people would pay for.** Picture this graphics on a PlayStation, or behind a
  $20 subscription — it doesn't hold.
- **Almost every detail repels.** Some details came out well, about 15% of them; the rest doesn't.
- **People move terribly and look frightening** — "like invalids".
- **Style is incoherent and scattered,** and doesn't match the mood of the scene.
- **Nobody wants to step into these pictures.** There is nothing to dream in.

What we saw in the renders, once we stopped praising them:

- **Different worlds in one frame.** A 3D interior with computed light, a toy doll, a realistic `body`, flat textures
  — side by side. Alfredo in the projection booth is the most "computer" object in a soft drawn room.
- **Everything is medium.** People take a quarter to half of the frame, the rest is filled with interior. Nothing is
  huge, nothing is tiny, there is no emptiness — so nothing is felt.
- **Many colours, brown murk, nothing is the main thing.**
- **Depth from 3D geometry** (ceilings, corridors, rows of seats) — it gives away "a game engine".
- **People at mid-shot with visible necks, joints and hands in poor poses,** standing without contact with the floor.
  Faces are empty; crowds are blocky and repeated.
- **Life is put into whole-body skeletal motion** — the hardest thing, and it looks worst. Real captured motion on
  dolls made of tubes reads as eerie.
- **Text and interface live apart from the world.**

## What Claude Design did

[pictures/hope/](pictures/hope/): the forest, the lake, the rain, the title "hope".

Simple scenes, but held in one style, minimal, indie, with one mood through everything — and motion: micro-motion,
animation, breathing. "I can't even put into words what it did. Maybe it worked some magic in details I don't
consciously notice, but I feel them. I want to step into this picture. I want to dream in it."

In the title: very big and very small on one axis, emptiness — screaming emptiness.

## It is not the engine

works-009-hope ports these scenes to engine 3 almost one to one
([title rendered by the engine](pictures/hope/title-engine-3.webp)). The engine had a few real gaps (the sky glow
it promised but didn't draw, a mirror limited to 512 px, ripples that couldn't be slowed, fonts in widgets) and a few
requests that were fitting one original. Neither is why the old games look as they do.

## What is missing

Conscious work of a designer. Games will be different — this way and that — but now they all fall apart, made at
random, "patched together from what was at hand". The difference between a dinner thrown together at home in three
minutes and a plate served in a restaurant: presentation, composition, every detail weighed, nothing there by chance.

Not rules — rules would be "from what was at hand" again, only by checklist. A decision before the work (what feeling,
what is the main thing, why this colour, this size, this emptiness) and an honest look after it, as a viewer, many
times over, until the frame holds.

The goal: beautiful games on engine 3 — at least one, to begin with.
