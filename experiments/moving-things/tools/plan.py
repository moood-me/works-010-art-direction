# Things that move with the hand: the scenes as places, and the places as Kimodo's constraints.
#   python3 tools/plan.py <scene>   → plans/<scene>.json: {constraints (as make_motion takes them), world: the scene
#                                     and the places for the page, kimodo: the same in Kimodo's space}
# Copied from К1 (experiments/contacts/tools/plan.py) and changed: the way a place becomes a constraint is the same
# (read that file's head and К1's notes.md): metres of our world / k = Kimodo's metres; a hand constraint is a whole
# pose — a pose of Kimodo's own (taken from a free take), its pelvis where the person should be, its arm turned by
# plain two-bone IK so the palm is on its place with the hand turned as Kimodo turned it in the free take.
# New here: a moving thing gives several places over time — a door's handle along its arc as it opens, a cup where
# it stands and where it is put back, a box's two sides where it lies and where it is put — each one a constrained
# frame with its own pose of the body.
import json, os, sys, numpy as np
from scipy.spatial.transform import Rotation as Rot
import kimodo as K
from pose import Pose, placed, hand_turn_from, heading_of

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(HERE)
def RAW(n):
    p = os.path.join(ITEM, 'motions', n + '.json')
    return K.read_raw(p if os.path.exists(p) else os.path.join(ITEM, 'motions', 'raw', n + '.json'))
K_WOMAN, K_MAN = 0.896, 1.015      # hip height against SOMA's (engine bodies moood-woman, moood-man)
r4 = lambda a: np.round(np.asarray(a, float), 4).tolist()


def arc(hinge, r, a):
    """a point at radius r about a vertical hinge, at angle a (0: along −x from the hinge, growing towards +z)"""
    return np.array([hinge[0] - r * np.cos(a), 0.0, hinge[1] + r * np.sin(a)])


def _door(D, cx, keys, end_frames, seconds, origin=(0.0, 0.0), pelvis_x=-0.15, back=0.02, hook=False):
    """A woman comes to a door in a wall, takes its handle with her right hand, pushes the door open (it swings away
    from her, its hinge on her left) and walks through, letting the handle go at the last key.
    D: the wall's plane (z); cx: the door's middle (x); keys: (frame, degrees open, pelvis z from D); origin: where
    the motion's origin is in the scene (Kimodo's metres; for one made with `after`, its startsAt).
    hook: the hand on top of the lever, its fingers hanging down behind it (between the lever and the leaf) — as a
    hand holds a lever, with straight fingers; else (the first takes) the palm in front of the lever, Kimodo's turn."""
    k = K_WOMAN; o = np.array([origin[0], 0.0, origin[1]])
    width, height, thick = 0.86, 2.0, 0.04
    hx = cx + width / 2
    handle_y, handle_in, handle_out = 0.98, 0.07, (0.07 if hook else 0.06)
    src = RAW('door-free')
    F = 30                                # its hand on the handle (it pulled the door; only the hand turn and the body are taken)
    turn0 = hand_turn_from(src, F, 'R')
    if hook:
        # the palm's middle 3 cm over the middle of the lever; the hand turned from Kimodo's so its fingers point down and
        # a little towards the door, the palm facing down and back onto the lever (Kimodo's fingers are nearly straight)
        palm_rest = np.array([hx - width + handle_in + 0.05, handle_y + 0.03, D - thick / 2 - handle_out + 0.011])
        turn0 = hand_to(turn0, 'R', [0, -0.87, 0.5], [0, -0.5, -0.87])
    else:
        # the palm's middle over the lever (the lever runs from the free edge towards the hinge, 6 cm off the leaf), `back`
        # in front of it
        palm_rest = np.array([hx - width + handle_in + 0.06, handle_y + 0.025, D - thick / 2 - handle_out - back])
    r = float(np.hypot(palm_rest[0] - hx, palm_rest[2] - D)); a0 = float(np.arctan2(palm_rest[2] - D, -(palm_rest[0] - hx)))
    poses, targets = [], []
    for f, deg, pz in keys:
        a = a0 + np.radians(deg)
        t = arc([hx, D], r, a); t[1] = palm_rest[1]
        turn = Rot.from_rotvec([0, np.radians(deg), 0]) * turn0     # the hand turns with the handle
        P = placed(src, F, np.array([cx + pelvis_x, D + pz]) / k - o[[0, 2]], 0.0)
        miss = P.reach('R', t / k - o, turn)
        print(f'door: frame {f}, open {deg}°, palm off by {miss:.4f}, pelvis {np.round((P.p[0] + o) * k, 3)}, target {np.round(t, 3)}')
        poses.append(P.as_ps()); targets.append(t)
    c = K.constraint('end-effector', [f for f, _, _ in keys], poses, ['RightHand'])
    endc = {'type': 'root2d', 'frame_indices': end_frames,
            'smooth_root_2d': [r4(np.array([cx + pelvis_x, D + 1.4 + 0.05 * i]) / k - o[[0, 2]]) for i in range(len(end_frames))]}
    return {'constraints': [c, endc], 'seconds': [seconds], 'frames': [f for f, _, _ in keys],
            'world': {'door': {'D': D, 'hinge': [hx, D], 'width': width, 'height': height, 'thick': thick,
                               'handle': {'y': handle_y, 'in': handle_in, 'out': handle_out}},
                      'palm': {'rest': r4(palm_rest), 'r': r, 'a0': a0, 'y': float(palm_rest[1])}, 'targets': [r4(t) for t in targets]},
            'kimodo': {'targets': [r4(t / k - o) for t in targets], 'pelvis': [r4(p['p'][0]) for p in poses], 'origin': r4(o)}}


def door_1():
    """the first take: one motion — the walk up, the handle, the push, the walk through. Kimodo walked the 2 m with
    the right arm stretched out for the handle, and the door let go at 50° stood in her way (she walked into it)"""
    return _door(2.4, 0.0, [(75, 0.0, -0.50), (85, 0.0, -0.46), (100, 25.0, -0.16), (115, 50.0, 0.12)], [175, 179], 6)


def door_2():
    """as door() below, the hand as Kimodo turned it, its palm in front of the lever: its fingers, held out nearly
    straight, went through the leaf (Kimodo has no grip)"""
    walk_end = np.array([-0.0237, 2.0937])
    D = round(float(walk_end[1] * K_WOMAN) + 0.5, 3); cx = round(float(walk_end[0] * K_WOMAN) + 0.15, 3)
    out = _door(D, cx, [(20, 0.0, -0.50), (30, 0.0, -0.46), (45, 25.0, -0.16), (60, 50.0, 0.12), (75, 70.0, 0.33)],
                [130, 134], 4.5, origin=walk_end)
    out['after'] = {'motion': 'table-walk', 'frames': 5, 'origin': r4([walk_end[0], 0, walk_end[1]])}
    return out


def door():
    """a chain: the walk up and stop is К1's table-walk (made already: Kimodo walks and stops 1.88 m on); the door is a
    second motion made to go on from it (after: its last 5 frames). The door stands 0.5 m before where she stops, its
    middle 15 cm to her left; the handle is let go at 70°, when the door is out of her way"""
    walk_end = np.array([-0.0237, 2.0937])     # table-walk's startsAt for after 5 (К1, motions/asks.json)
    D = round(float(walk_end[1] * K_WOMAN) + 0.5, 3); cx = round(float(walk_end[0] * K_WOMAN) + 0.15, 3)
    out = _door(D, cx, [(20, 0.0, -0.50), (30, 0.0, -0.46), (45, 25.0, -0.16), (60, 50.0, 0.12), (75, 70.0, 0.33)],
                [130, 134], 4.5, origin=walk_end, hook=True)
    out['after'] = {'motion': 'table-walk', 'frames': 5, 'origin': r4([walk_end[0], 0, walk_end[1]])}
    return out


def lean_forward(P, angle):
    """the input pose bent forward at the waist (only so its arms reach: Kimodo is given just the hands and pelvis)"""
    ax = Rot.from_rotvec([0, heading_of(P.G), 0]).apply([1, 0, 0])
    P.turn(K.IDX['Spine1'], Rot.from_rotvec(ax * angle))


def palm_normal(p, side):
    """the way the palm faces (out of it), from the joints: the wrist and the knuckles of the index and little finger"""
    s = 'Left' if side == 'L' else 'Right'
    a, i, k = p[K.IDX[s + 'Hand']], p[K.IDX[s + 'HandIndex1']], p[K.IDX[s + 'HandPinky1']]
    n = np.cross(i - a, k - a); n /= np.linalg.norm(n)
    return n if side == 'R' else -n


def facing(turn, side, want):
    """a hand's turn changed by the smallest turn that makes its palm face `want` (a world direction)"""
    P = placed(RAW('door-free'), 30, [0, 0], 0.0)
    s = 'Left' if side == 'L' else 'Right'
    P.turn(K.IDX[s + 'Hand'], turn * P.G[K.IDX[s + 'Hand']].inv())
    n = palm_normal(P.p, side); w = np.asarray(want, float) / np.linalg.norm(want)
    ax = np.cross(n, w); ang = np.arctan2(np.linalg.norm(ax), np.dot(n, w))
    return Rot.from_rotvec(ax / np.linalg.norm(ax) * ang) * turn


def fingers_to(turn, side, want):
    """a hand's turn changed by the smallest turn that points its fingers (wrist → knuckles) along `want`"""
    P = placed(RAW('door-free'), 30, [0, 0], 0.0)
    s = 'Left' if side == 'L' else 'Right'
    P.turn(K.IDX[s + 'Hand'], turn * P.G[K.IDX[s + 'Hand']].inv())
    f = (P.p[K.IDX[s + 'HandIndex1']] + P.p[K.IDX[s + 'HandPinky1']]) / 2 - P.p[K.IDX[s + 'Hand']]
    f /= np.linalg.norm(f); w = np.asarray(want, float) / np.linalg.norm(want)
    ax = np.cross(f, w); ang = np.arctan2(np.linalg.norm(ax), np.dot(f, w))
    return Rot.from_rotvec(ax / np.linalg.norm(ax) * ang) * turn


def hand_to(turn, side, fingers, normal):
    """a hand's turn changed so its fingers point along `fingers` and its palm faces `normal` (made at right angles)"""
    P = placed(RAW('door-free'), 30, [0, 0], 0.0)
    s = 'Left' if side == 'L' else 'Right'
    P.turn(K.IDX[s + 'Hand'], turn * P.G[K.IDX[s + 'Hand']].inv())
    f = (P.p[K.IDX[s + 'HandIndex1']] + P.p[K.IDX[s + 'HandPinky1']]) / 2 - P.p[K.IDX[s + 'Hand']]
    n = palm_normal(P.p, side)
    def basis(a, b):
        a = np.asarray(a, float) / np.linalg.norm(a); b = np.asarray(b, float) - np.dot(b, a) * a; b /= np.linalg.norm(b)
        return np.stack([a, b, np.cross(a, b)], 1)
    return Rot.from_matrix(basis(fingers, normal) @ basis(f, n).T) * turn


def standing_reach(src, f, pelvis_xz, palms, turns, k, o):
    """a standing pose of Kimodo's own with its pelvis at pelvis_xz (our metres), bent forward at the waist as little
    as lets both given palms reach their places (our metres) with the given hand turns; in Kimodo's space less o"""
    P = placed(src, f, np.array(pelvis_xz) / k - o[[0, 2]], 0.0, dy=-0.02)
    for a in np.radians(np.arange(0, 70, 2)):
        Q = Pose(P.as_ps()); lean_forward(Q, a)
        miss = [Q.reach(s, np.asarray(palms[s]) / k - o, turns[s]) for s in palms]
        if max(miss) < 0.003: break
    return Q, float(np.degrees(a)), miss


def cup_1():
    return cup(with_drink=None)


def cup_2():
    """(made with the drink pose of cup-1's frame 100 moved onto a standing pose; see cup())"""
    raise NotImplementedError('cup-2 was planned by an earlier version of cup(); its plan is plans/cup-2.json')


def cup(with_drink=(90, 110)):
    """A woman walks up to a table (К1's table-walk: she stops 0.32 m before its edge), takes a cup standing on it
    with her right hand, drinks from it and puts it back where it stood. The cup is held from the side, the palm
    facing it (Kimodo's own hand turn from the free take, turned so the palm faces left, towards the cup)."""
    k = K_WOMAN
    walk_end = np.array([-0.0237, 2.0937]); o = np.array([walk_end[0], 0, walk_end[1]])
    top, edge, depth, width = 0.74, 2.2, 0.7, 1.2
    pelvis = [float(walk_end[0] * k), float(walk_end[1] * k)]
    cup_r, cup_h = 0.04, 0.095
    cup_at = np.array([-0.17, top, edge + 0.13])              # the middle of its bottom
    palm = cup_at + [-(cup_r + 0.022), cup_h * 0.5, 0.0]       # the palm's middle on its right side, half way up
    turn = facing(hand_turn_from(RAW('cup-free'), 125, 'R'), 'R', [1, 0, 0])
    keys = [30, 38, 170, 180]                                   # taken (and lifted from 38 on), put back by 170, let go after 180
    Q, bent, miss = standing_reach(RAW('table-free2'), 150, pelvis, {'R': palm}, {'R': turn}, k, o)
    print('cup: bent', bent, 'deg; palm off by', np.round(miss, 4), 'pelvis', np.round((Q.p[0] + o) * k, 3))
    poses = {f: Q.as_ps() for f in keys}
    drink = None
    if with_drink:
        # drinking standing: the first take (cup-1) drank, but half sitting on nothing (Kimodo's data has people drinking
        # from cups seated at tables); the second (cup-2) stood, its hand put by the first take's hand-to-head
        # relation: the cup came up beside the face, not to the mouth. So the drink is written as the cup's place: the
        # cup tilted 40° towards the face, its rim at the lips (the eyes' middle, 7.5 cm down, 2 cm ahead), the hand on
        # its right side as when it was taken (the same turn, tilted with the cup); the body upright, as she stood
        # when her walk ended (table-walk's last frame)
        S = placed(RAW('table-walk'), 119, np.array(pelvis) / k - o[[0, 2]], 0.0)       # upright: where her walk ended
        eyes = (S.p[K.IDX['LeftEye']] + S.p[K.IDX['RightEye']]) / 2
        lips = eyes + np.array([0, -0.075, 0.02]) / k
        tilt = Rot.from_rotvec([np.radians(-40), 0, 0])
        up = tilt.apply([0, 1, 0]); fwd = tilt.apply([0, 0, 1])
        centre = lips - up * (cup_h / 2) / k + fwd * cup_r / k       # the cup's middle (half way up its axis)
        want = centre - np.array([cup_r + 0.022, 0, 0]) / k            # the palm on its right side
        dturn = tilt * turn
        dm = S.reach('R', want, dturn)
        print('cup: drink palm off by', round(dm, 4), 'at', np.round((want + o) * k, 3), 'lips', np.round((lips + o) * k, 3))
        for f in with_drink: poses[f] = S.as_ps()
        drink = r4((want + o) * k)
    fr = sorted(poses)
    c = K.constraint('end-effector', fr, [poses[f] for f in fr], ['RightHand'])
    return {'constraints': [c], 'seconds': [7], 'frames': keys, 'drink_frames': list(with_drink or []),
            'after': {'motion': 'table-walk', 'frames': 5, 'origin': r4(o)},
            'world': {'table': {'top': top, 'edge': edge, 'depth': depth, 'width': width}, 'cup': {'at': r4(cup_at), 'r': cup_r, 'h': cup_h},
                      'palm': r4(palm), 'pelvis': pelvis, 'drink': drink},
            'kimodo': {'palm': r4(palm / k - o), 'pelvis': r4(Q.p[0])}}


def box_1():
    """the first take: the pelvis where the free take's was when it put the box down (33 cm behind the box's middle):
    standing so close, his thighs went under the table's edge and his belly touched the box"""
    return box(back=0.0)


def box(back=0.12):
    """A man squats, takes a box from the floor in both hands (its sides between his palms), carries it 3 m and puts it
    on a table. The free take (box-free) did all of this by itself; here its own poses are moved to the places of the
    scene and its palms put on the box's sides — where the box lies and where it is put — and its pelvis there."""
    k = K_MAN
    src = RAW('box-free')
    w, h, d = 0.40, 0.30, 0.30              # the box: width (between the palms), height, depth
    grip_y, half = 0.17, w / 2 + 0.03       # the palms' middles 17 cm over the box's bottom, 3 cm off its sides
    box_at = np.array([0.0, 0.0, 0.50])     # the box's bottom's middle, on the floor
    top, edge, tdepth, twidth = 0.80, 3.25, 0.6, 1.0
    put_at = np.array([0.0, top, edge + 0.22])
    plans = {}
    for name, at, f, pf in (('take', box_at, 45, [45, 55]), ('put', put_at, 255, [245, 258])):
        palms = {'L': at + [half, grip_y, 0], 'R': at + [-half, grip_y, 0]}
        turns = {s_: hand_turn_from(src, f, s_) for s_ in 'LR'}
        pel = src['p'][f][0] * k                             # Kimodo's own pelvis there, in our metres
        if name == 'put': pel[2] -= back                     # a step farther from the table (see box_1)
        P0 = placed(src, f, np.array([0.0, pel[2]]) / k, 0.0)
        for a in np.radians(np.arange(0, 40, 2)):          # bent forward at the waist as little as lets the palms reach
            P = Pose(P0.as_ps()); lean_forward(P, a)
            miss = [P.reach(s_, palms[s_] / k, turns[s_]) for s_ in 'LR']
            if max(miss) < 0.003: break
        print(f'box {name}: bent {np.degrees(a):.0f}°, palms off by {np.round(miss, 4)}, pelvis {np.round(P.p[0] * k, 3)}')
        plans[name] = (pf, P.as_ps(), palms)
    fr = plans['take'][0] + plans['put'][0]
    c = K.constraint('end-effector', fr, [plans['take'][1]] * 2 + [plans['put'][1]] * 2, ['LeftHand', 'RightHand'])
    return {'constraints': [c], 'seconds': [3, 4, 3], 'frames': fr,
            'world': {'box': {'at': r4(box_at), 'size': [w, h, d], 'put': r4(put_at), 'grip_y': grip_y, 'half': half},
                      'table': {'top': top, 'edge': edge, 'depth': tdepth, 'width': twidth},
                      'palms': {n: {s_: r4(v) for s_, v in plans[n][2].items()} for n in plans}}}


if __name__ == '__main__':
    name = sys.argv[1].replace('-', '_')
    out = globals()[name]()
    json.dump(out, open(os.path.join(ITEM, 'plans', name + '.json'), 'w'))
    print('constraints', len(json.dumps(out['constraints'])), 'chars')
