# Indie heroes

A constructor of heroes from simple forms on a skeleton of SOMA joints (without fingers), built from a few measures
(pelvis height, leg, torso and arm length, head size).
- a hero is a list of forms (ball, ellipsoid, drop, cone, capsule, rounded box, torus, horn along a curve, subtraction
  and intersection), each tied to a bone; "body" forms join smoothly, things (mask, helmet, horns, hat, weapon, eyes)
  are separate pieces with their own bone; colour zones from the nearest form;
- a form lying on two bones splits its weight at the joint, so knees and elbows bend without a break; poses are
  rotations of the same joints, the pelvis lowers so feet stay on the floor;
- 18 original heroes. Kimodo motion was not tried on them.
Pictures: [docs/pictures/indie](../../docs/pictures/indie/).

**Second version:** a "colour and outline" look (three-tone fill, a dark line around each big form) beside the clay
one; faces redrawn per feeling — calm, glad, surprised, angry, sad, sleepy, winking — with blush and brows; poses with
a line of action, each with its own feeling, plus "dozing"; held things on their own joint in the hand, kept upright;
robot and stone guard as separate hard blocks; six new heroes (candle, raven courier, snail knight, cactus wanderer,
little octopus, little witch) — 24 in all.

**Kimodo motions:** ten motions made in the studio (walk, wave, happy jump, sit hugging knees, run, idle, dance, bow,
sneak, angry stomp); `conv.py` turns the studio's per-joint world rotations into rotations relative to SOMA's rest
pose (`motions/*.json`); `poseFromMotion` retargets them — each joint turned as SOMA's, bones first re-aimed where the
hero's rest differs, pelvis raised by leg length, feet set on the floor, arms kept off the body and pushed out of the
big head; limbs amplified ×1.3; the face follows the motion. GIFs in `docs/pictures/indie/motion`.
