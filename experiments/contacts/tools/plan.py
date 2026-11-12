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

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(HERE)
def RAW(n):
    """a made motion: one kept here (motions/<n>.json) or a source only (motions/raw/<n>.json)"""
    p = os.path.join(ITEM, 'motions', n + '.json')
    return K.read_raw(p if os.path.exists(p) else os.path.join(ITEM, 'motions', 'raw', n + '.json'))
K_WOMAN, K_MAN = 0.896, 1.015      # hip height against SOMA's (engine bodies moood-woman, moood-man)
r4 = lambda a: np.round(np.asarray(a, float), 4).tolist()


def lean_forward(P, angle):
    """the input pose bent forward at the waist (only so its arms reach: Kimodo is given just the hands and pelvis)"""
    ax = Rot.from_rotvec([0, heading_of(P.G), 0]).apply([1, 0, 0])
    P.turn(K.IDX['Spine1'], Rot.from_rotvec(ax * angle))


def table():
    k = K_WOMAN
    # the scene (our world): a table 0.74 m high, its near edge 2.2 m ahead; the palms 14 cm in from the edge
    top, edge, depth, width = 0.74, 2.2, 0.7, 1.2
    palm_lift = 0.022            # the palm's middle (between wrist and knuckles) over the skin under it, our body
    palms = {'L': [0.19, top + palm_lift, edge + 0.14], 'R': [-0.19, top + palm_lift, edge + 0.14]}
    pelvis_world = [0.0, edge - 0.27]
    # in Kimodo's space
    pk = {s: np.array(v) / k for s, v in palms.items()}
    src = RAW('table-free')                  # Kimodo's hands lying on a table (it sat at it): their turn
    turns = {s: hand_turn_from(src, 115, s) for s in 'LR'}
    stand = RAW('table-free2')               # Kimodo standing (it walked up and stood)
    P = placed(stand, 150, np.array(pelvis_world) / k, 0.0, dy=-0.02)
    for a in np.radians(np.arange(0, 60, 2)):
        Q = Pose(P.as_ps()); lean_forward(Q, a)
        miss = [Q.reach(s, pk[s], turns[s]) for s in 'LR']
        if max(miss) < 0.003: break
    print('table: input pose bent', round(float(np.degrees(a))), 'deg; palms off by', np.round(miss, 4))
    frames = [149, 179]          # a second before the end the hands are there, and at the last frame still there
    c = K.constraint('end-effector', frames, [Q.as_ps()] * len(frames), ['LeftHand', 'RightHand'])
    return {'constraints': [c], 'seconds': [6], 'frames': frames,
            'world': {'table': {'top': top, 'edge': edge, 'depth': depth, 'width': width}, 'palms': palms, 'pelvis': pelvis_world},
            'kimodo': {'palms': {s: r4(v) for s, v in pk.items()}, 'pelvis': r4(Q.p[0])}}


def armchair():
    k = K_WOMAN
    # the scene: an armchair 2.3 m ahead, facing the person (its front towards −z); seat 0.42 m, armrests 0.62 m high,
    # 0.52 m apart inside, 0.10 m wide, 0.60 m deep; the palms on the armrests' middle lines, 12 cm in front of centre
    at, seat, arm, inner, aw, depth, back, width = [0.0, 2.3], 0.42, 0.62, 0.52, 0.10, 0.60, 0.92, 0.72
    palm_lift = 0.022
    x = inner / 2 + aw / 2
    # sitting in it, facing −z, one's left hand is at −x
    palms = {'L': [-x, arm + palm_lift, at[1] - 0.16], 'R': [x, arm + palm_lift, at[1] - 0.16]}
    # where the pelvis sits, from our body seated (measured on the page in the first take): the pelvis joint 18.5 cm
    # over the lowest skin under it (1 cm let into the cushion), the back 25 cm behind it, leaning on the backrest
    # (its front 18 cm behind the chair's centre). The first take, with the pelvis 11 cm over the seat and 2 cm
    # behind the centre, sat 8 cm into the seat and 6–8 cm into the backrest.
    pelvis_world = [at[0], at[1] - 0.07]
    pelvis_y_world = seat + 0.175
    pk = {s: np.array(v) / k for s, v in palms.items()}
    heading = np.pi
    src = RAW('table-free')
    turns = {s: hand_turn_from(src, 115, s, heading) for s in 'LR'}
    sit = RAW('chair-free')                  # Kimodo sitting down by itself (on something, hands on the lap)
    pelvis_y = pelvis_y_world / k
    P0 = placed(sit, 175, np.array(pelvis_world) / k, heading)
    P = placed(sit, 175, np.array(pelvis_world) / k, heading, dy=pelvis_y - P0.p[0, 1])
    miss = [P.reach(s, pk[s], turns[s]) for s in 'LR']
    print('armchair: palms off by', np.round(miss, 4), 'pelvis', np.round(P.p[0], 3))
    frames = [134, 209]          # sitting with the hands on the armrests from 4.5 s, still so at the end (7 s)
    c = K.constraint('end-effector', frames, [P.as_ps()] * len(frames), ['LeftHand', 'RightHand'])
    return {'constraints': [c], 'seconds': [7], 'frames': frames,
            'world': {'armchair': {'at': [at[0], 0, at[1]], 'heading': heading, 'seat': seat, 'arm': arm, 'width': width,
                                   'armWidth': aw, 'depth': depth, 'back': back}, 'palms': palms, 'pelvis': pelvis_world},
            'kimodo': {'palms': {s: r4(v) for s, v in pk.items()}, 'pelvis': r4(P.p[0])}}


def table_lean():
    """the table again, as a chain: Kimodo walks up and stops (table-walk, its pelvis led to 2.05 m by root2d), then a
    lean made to go on from it (after: its last 5 frames) with the hands on the table. A motion made with `after`
    begins at the earlier one's frame n−5, its pelvis there over its origin, its heading kept: so its places are the
    earlier one's less its origin there. That origin is the studio's `startsAt` — not exactly the earlier one's pelvis
    at frame n−5 (the first take, made with that guess, came 5 cm off: its startsAt was (−0.024, 2.094) while the
    walk's pelvis then was at (−0.037, 2.045)). It depends only on the earlier motion and `frames`, so it is read off
    the first take made with this `after` and the constraint is written again in it."""
    out = table()
    o = np.array([-0.0237, 0.0, 2.0937])         # startsAt of table-walk + after 5 (motion(key) of the first take)
    c = out['constraints'][0]
    c['root_positions'] = [r4(np.asarray(r) - o) for r in c['root_positions']]
    c['frame_indices'] = [89, 119]
    out.update(seconds=[4], frames=c['frame_indices'], after={'motion': 'table-walk', 'frames': 5, 'origin': r4(o)})
    return out


if __name__ == '__main__':
    name = sys.argv[1].replace("-", "_")
    out = globals()[name]()
    os.makedirs(os.path.join(ITEM, 'plans'), exist_ok=True)
    json.dump(out, open(os.path.join(ITEM, 'plans', name + '.json'), 'w'))
    print('constraints', len(json.dumps(out['constraints'])), 'chars')

