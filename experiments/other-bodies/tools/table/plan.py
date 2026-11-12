# The scenes as places, and the places as Kimodo's constraints.
#   python3 tools/plan.py <scene>   → plans/<scene>.json: {constraints (as make_motion takes them), world: the places
#                                     in the scene for the page, kimodo: the same in Kimodo's space, notes}
#
# How a place in the scene becomes Kimodo's coordinates:
#  1. The scene is in metres of our world, the person (an engine body) starting at the origin facing +z.
#  2. Kimodo's person is SOMA, of other size: the engine carries its path scaled by k = our hip height / SOMA's
#     (engine/src/retarget.js). So a place x in our world is x / k in Kimodo's space (the floor stays at 0).
#  3. The hand constraint is a whole pose (tools/kimodo.py): its pelvis where the person should stand or sit, facing
#     where they should face, the palms on their places with the hand turned as Kimodo turns a hand lying on
#     something (tools/pose.py). Kimodo keeps the palms and the pelvis there at the given frames and makes everything
#     else — the walk up, the lean, the elbows, the head — itself.
#  4. On our body the same turns leave the palm a few centimetres off (other arm lengths, shoulders): the page's
#     correction (contact-figure.js) brings it the rest of the way, weighed in and out around the touch.
import json, os, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot
import kimodo as K
from pose import Pose, placed, hand_turn_from, heading_of

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(os.path.dirname(HERE))
def RAW(n):
    """a made motion: one kept here (motions/<n>.json) or a source only (motions/raw/<n>.json)"""
    p = os.path.join(ITEM, 'motions', n + '.json')
    return K.read_raw(p if os.path.exists(p) else os.path.join(ITEM, 'motions', 'raw', n + '.json'))
r4 = lambda a: np.round(np.asarray(a, float), 4).tolist()


def lean_forward(P, angle):
    """the input pose bent forward at the waist (only so its arms reach: Kimodo is given just the hands and pelvis)"""
    ax = Rot.from_rotvec([0, heading_of(P.G), 0]).apply([1, 0, 0])
    P.turn(K.IDX['Spine1'], Rot.from_rotvec(ax * angle))


# Other bodies (К1's table repeated): each body's measures (tools/table/bodies.mjs prints them), the table's height.
# What К1 had for one body (the woman) is said here per body:
#  - k: hip height against SOMA's;
#  - the palms' spread: К1's ±0.19 m for the woman's shoulders (0.289 m), scaled by the shoulders;
#  - where the pelvis stands: К1's 0.27 m from the edge is the woman's front (0.14 m before the pelvis, at rest,
#    between hips and shoulders, arms left out) and 0.13 m more; the 0.13 m is scaled by k, the front is the body's
#    own (a belly stands further off);
#  - palm_lift (the palm's middle over the skin under it): К1's 0.022 m, scaled by k.
# The walk is К1's own (table-walk, Kimodo's space); the lean goes on from it as К1's did, so the lean's pelvis is
# where К1's was in Kimodo's space (2.154 m; the walk stopped at 2.094) and the table stands where this body arrives:
# the table moves with the body, not the body to the table (a game with the table fixed orders its own walk).
BODIES = {
    # character id: (body id, k, front, shoulder width)
    'woman':   ('moood-woman', 0.896, 0.140, 0.289),
    'child':   ('moood-child', 0.707, 0.105, 0.235),
    'oldman':  ('moood-oldman', 0.972, 0.210, 0.352),
    'elf':     ('anny-C-elf', 1.408, 0.167, 0.338),
}
PELVIS_K = 2.1540          # К1's lean pelvis in Kimodo's space (plans/table.json of К1: 1.93 / 0.896)


def table(who='woman', top=0.74, depth=0.7, width=1.2):
    body, k, front, shw = BODIES[who]
    d = front + 0.13 * k / 0.896
    pelvis_world = [0.0, PELVIS_K * k]
    edge = pelvis_world[1] + d
    spread = 0.19 * shw / 0.289
    palm_lift = 0.022 * k / 0.896
    palms = {'L': [spread, top + palm_lift, edge + 0.14 * k / 0.896], 'R': [-spread, top + palm_lift, edge + 0.14 * k / 0.896]}
    pk = {s: np.array(v) / k for s, v in palms.items()}
    src = RAW('table-free')                  # Kimodo's hands lying on a table (it sat at it): their turn
    turns = {s: hand_turn_from(src, 115, s) for s in 'LR'}
    stand = RAW('table-free2')               # Kimodo standing (it walked up and stood)
    P = placed(stand, 150, np.array(pelvis_world) / k, 0.0, dy=-0.02)
    for a in np.radians(np.arange(0, 90, 2)):
        Q = Pose(P.as_ps()); lean_forward(Q, a)
        miss = [Q.reach(s, pk[s], turns[s]) for s in 'LR']
        if max(miss) < 0.003: break
    bent = round(float(np.degrees(a)))
    print(who, top, ': input pose bent', bent, 'deg; palms off by', np.round(miss, 4), 'pelvis', np.round(Q.p[0], 3), 'palms', {s: r4(v) for s, v in pk.items()})
    frames = [149, 179]
    c = K.constraint('end-effector', frames, [Q.as_ps()] * len(frames), ['LeftHand', 'RightHand'])
    return {'constraints': [c], 'seconds': [6], 'frames': frames, 'who': who, 'body': body, 'k': k, 'bent_deg': bent,
            'input_miss_m': r4(miss),
            'world': {'table': {'top': top, 'edge': r4(edge), 'depth': depth, 'width': width}, 'palms': {s: r4(v) for s, v in palms.items()}, 'pelvis': r4(pelvis_world)},
            'kimodo': {'palms': {s: r4(v) for s, v in pk.items()}, 'pelvis': r4(Q.p[0])}}


def lean(who, top=0.74):
    """the lean, made to go on from К1's walk (after: its last 5 frames); its places less the studio's startsAt of
    that `after` (the same for any lean after table-walk with 5 frames: (−0.0237, 2.0937), read off К1's take)"""
    out = table(who, top)
    o = np.array([-0.0237, 0.0, 2.0937])
    c = out['constraints'][0]
    c['root_positions'] = [r4(np.asarray(r) - o) for r in c['root_positions']]
    c['frame_indices'] = [89, 119]
    out.update(seconds=[4], frames=c['frame_indices'], after={'motion': 'table-walk', 'frames': 5, 'origin': r4(o)})
    return out


if __name__ == '__main__':
    who, top = sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 0.74
    name = sys.argv[3] if len(sys.argv) > 3 else f'lean-{who}'
    out = lean(who, top)
    os.makedirs(os.path.join(ITEM, 'plans'), exist_ok=True)
    json.dump(out, open(os.path.join(ITEM, 'plans', name + '.json'), 'w'))
    print(name, 'constraints', len(json.dumps(out['constraints'])), 'chars')
