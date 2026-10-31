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
