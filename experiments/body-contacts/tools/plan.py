# К2's scenes as places, and the places as Kimodo's constraints (a copy of К1's tools/plan.py, its scenes replaced).
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


import somaskin as SS


def placed_against(P, normal, plane, parts):
    """the pose moved along `normal` (a unit vector over the floor, out of the thing) so that the skin of `parts` just
    touches the plane {x: x·normal = plane}: the way a back is put on a wall (Kimodo's space, SOMA's skin)"""
    v = SS.skin(Rot.concatenate(P.G), P.p)
    reach = (v[SS.of(parts)] @ normal).min()               # the farthest the parts reach towards the thing
    P.p = P.p + normal * (plane - reach)
    return P


def wall():
    """The woman walks 2 m up to a wall, turns round and leans back on it; stays; then rises off it and walks away.
    The wall is written in our scene: its face 2.6 m ahead, across the way. Kimodo is given, at two frames, the whole
    pose of its own lean (wall-free: it leaned back by itself, on nothing) turned to face away from the wall and moved
    so that SOMA's back skin is on the wall's face (in Kimodo's space): the place of the back is the place of that pose."""
    k = K_WOMAN
    face = 2.6                                   # the wall's face, our world (z); the wall goes on behind it
    src = RAW('wall-free')
    P = placed(src, 120, [0.0, face / k - 0.3], np.pi)      # facing back (−z), its back towards the wall
    # our woman's back reaches 0.5 cm further than SOMA's scaled (the first take, wall-lean-try1, held 0.4–0.7 cm into
    # the wall): the pose is put that much off the face
    P = placed_against(P, np.array([0, 0, -1.0]), -(face - 0.006) / k, ['spine', 'pelvis', 'head', 'clavicle'])
    # the first take, held at 165 and 209 only, leaned 5 cm into the wall at 90–140 and slid out by 160: the lean is
    # held from the moment the back comes to the wall (frame 95 there)
    frames = [95, 150, 209]
    c = K.constraint('fullbody', frames, [P.as_ps()] * len(frames))
    print('wall: pelvis', np.round(P.p[0], 3), 'feet', np.round((P.p[K.IDX['LeftFoot']] + P.p[K.IDX['RightFoot']]) / 2, 3))
    return {'constraints': [c], 'seconds': [7], 'frames': frames,
            'world': {'wall': {'face': face}, 'pelvis': r4(P.p[0] * k)},
            'kimodo': {'wall_face': round(face / k, 4), 'pelvis': r4(P.p[0])}}

def slim(c, ends):
    """a hand or foot constraint written short: Kimodo reads of its pose only the pelvis and the chain down to the hand
    or foot (and what hangs from it: the fingers, the toes), so the other joints' turns are sent as 0 (it is the same
    constraint, only shorter to send)"""
    from pose import subtree
    keep = set()
    for e in ends:
        j = K.IDX[e]; keep |= set(subtree(j))
        while j >= 0: keep.add(j); j = K.PARENT[j]
    c['local_joints_rot'] = [[r if j in keep else [0, 0, 0] for j, r in enumerate(fr)] for fr in c['local_joints_rot']]
    return c


STAIRS = dict(rise=0.14, tread=0.22, start=0.15, steps=10, width=1.0, rail_x=-0.42, rail_h=0.80, rail_r=0.025, landing=0.9)


def stairs_geometry(st=STAIRS):
    """our world: step i (1…n) is [start + (i−1)·tread, start + i·tread] deep, its top at i·rise; the rail's axis over
    the line of the step fronts, rail_h above it, on the person's right (−x)"""
    h, d, z0, n = st['rise'], st['tread'], st['start'], st['steps']
    rail_y = lambda z: st['rail_h'] + h + (z - z0) * h / d
    a = [st['rail_x'], rail_y(z0 - 0.25), z0 - 0.25]; b = [st['rail_x'], rail_y(z0 + (n - 1) * d), z0 + (n - 1) * d]
    steps = [{'i': i, 'z': [z0 + (i - 1) * d, z0 + i * d], 'top': i * h} for i in range(1, n + 1)]
    steps[-1].update(z=[steps[-1]['z'][0], steps[-1]['z'][0] + st['landing']], landing=True)
    return {'steps': steps,
            'rail': {'a': r4(a), 'b': r4(b), 'r': st['rail_r']}, 'measures': st}


def stairs():
    """The woman climbs ten steps (ours: 14 cm high, 22 cm deep) with her right hand sliding up the rail. Written in
    our scene: each foot's step, and the rail. Kimodo climbed stairs by itself (stairs-free: on nothing, its feet
    rising ~15 cm a step); here its feet are given, at the middle of each stance it made, on our steps: the pose of
    that frame moved (up and ahead) so the foot stands on its step, sent as Kimodo's foot constraint. Between the
    stances, at five frames, the right hand on the rail: the same frame's pose, moved as the stances around it, its
    right arm turned so the palm lies on the rail a little ahead of the shoulder, the hand turned palm down along the
    slope — sent as Kimodo's right-hand constraint."""
    k = K_WOMAN; g = stairs_geometry()
    src = RAW('stairs-free')
    # each foot as people put it on a step: its toes 1.5 cm short of the next riser, the heel over the edge behind if
    # the foot is longer than the tread (SOMA's foot, heel to toe, is 25 cm in Kimodo's metres; the tread 24.6), the
    # sole on the step's top — read off SOMA's skin of that very pose. (The first take placed the ankle 7 cm behind the
    # step's front edge: the toes went 14 cm into the next riser. The second, toes 1.5 cm short in Kimodo's space: on
    # our woman, whose feet are longer than SOMA's scaled, they still went 3–4 cm into the riser: so 5 cm short in our
    # world.) On the top landing, the whole foot on it; and at the last frame both feet there, standing: Kimodo's own
    # standing pose (stairs-free, frame 2) put on the landing (the second take, given nothing there, went on lifting its
    # feet as if there were more steps).
    toes_short = 0.05
    stances = [('L', 30, 1), ('R', 45, 2), ('L', 61, 3), ('R', 76, 4), ('L', 92, 5), ('R', 105, 6), ('L', 122, 7),
               ('R', 140, 8), ('L', 155, 9), ('R', 170, 10)]      # foot, frame (mid-stance in stairs-free), step
    moves, cons = [], {'L': [], 'R': []}
    for side, f, i in stances:
        s = g['steps'][i - 1]
        ps = K.pose(src, f); v = SS.skin(ps['G'], ps['p'])[SS.of(['foot', 'toe'], side)]
        front = s['z'][0] / k + 0.28 if s.get('landing') else s['z'][1] / k - toes_short / k
        mv = np.array([0.0, s['top'] / k - v[:, 1].min(), front - v[:, 2].max()])
        ps['p'] = ps['p'] + mv
        moves.append((f, mv)); cons[side].append((f, ps))
    land = g['steps'][-1]
    ps = K.pose(src, 2); v = SS.skin(ps['G'], ps['p'])[SS.of(['foot', 'toe'])]
    mv = np.array([0.0, land['top'] / k - v[:, 1].min(), land['z'][0] / k + 0.36 - v[:, 2].max()])
    ps['p'] = ps['p'] + mv
    out = []
    for side, kind in (('L', 'left-foot'), ('R', 'right-foot')):
        out.append(slim(K.constraint(kind, [f for f, _ in cons[side]], [P for _, P in cons[side]]), [('Left' if side == 'L' else 'Right') + 'Foot']))
    out.append(slim(K.constraint('end-effector', [179], [ps], ['LeftFoot', 'RightFoot']), ['LeftFoot', 'RightFoot']))
    # the hand on the rail
    fs = np.array([f for f, _ in moves]); mvs = np.array([m for _, m in moves])
    move_at = lambda f: np.array([np.interp(f, fs, mvs[:, c]) for c in range(3)])
    rail = g['rail']; a, b = np.array(rail['a']) / k, np.array(rail['b']) / k
    slope = np.arctan2(b[1] - a[1], b[2] - a[2])
    turn0 = hand_turn_from(RAW('table-free'), 115, 'R')                 # palm down, fingers ahead
    # its fingers turned to lie along the rail, a little across it (towards the body's left: over the rail's top)
    fwd = K.NEUTRAL[K.IDX['RightHandMiddle1']] - K.NEUTRAL[K.IDX['RightHand']]
    f0 = turn0.apply(fwd / np.linalg.norm(fwd)); want = (b - a) / np.linalg.norm(b - a) + [0.4, 0, 0]
    want /= np.linalg.norm(want); ax = np.cross(f0, want)
    turn = Rot.from_rotvec(ax / np.linalg.norm(ax) * np.arctan2(np.linalg.norm(ax), f0 @ want)) * turn0
    palm_lift = 0.022 / k
    hands, report = [], []
    for f in range(30, 171, 15):          # every half second (the first take, every second, left the rail by 20 cm between)
        ps = K.pose(src, f); ps['p'] = ps['p'] + move_at(f); P = Pose(ps)
        z = P.p[K.IDX['RightArm'], 2] + 0.12
        u = (z - a[2]) / (b[2] - a[2]); x = a + (b - a) * u
        target = x + [0, rail['r'] / k + palm_lift, 0]
        miss = P.reach('R', target, turn)
        hands.append((f, P.as_ps())); report.append((f, round(miss, 4)))
    out.append(slim(K.constraint('right-hand', [f for f, _ in hands], [P for _, P in hands]), ['RightHand']))
    print('stairs: hand misses', report, 'slope', round(float(np.degrees(slope)), 1))
    return {'constraints': out, 'seconds': [6], 'stances': stances, 'hand_frames': [f for f, _ in hands],
            'world': g, 'kimodo': {'moves': [[int(f), r4(m)] for f, m in moves]}}

BED = dict(edge=2.2, depth=0.95, length=2.0, centre_x=0.0, top=0.48, frame_h=0.3, pillow=0.0)


def bed_sit():
    """The woman walks up to a bed that stands across her way (its near long side 2.2 m ahead, the mattress top 48 cm
    high), turns round and sits on its edge. Kimodo is given, at two frames, a seated pose of its own (chair-free:
    it sat down by itself) turned to face away from the bed, its buttocks' skin on the mattress top, the pelvis 14 cm
    in from the edge — as a constraint of both feet (which holds the pelvis's place, height and heading, and the feet
    on the floor where that pose has them)."""
    k = K_WOMAN; b = BED
    sit = RAW('chair-free')
    P = placed(sit, 175, [b['centre_x'] / k, (b['edge'] + 0.14) / k], np.pi)
    P = placed_against(P, np.array([0, 1.0, 0]), b['top'] / k, ['pelvis', 'thigh'])
    frames = [150, 179]
    c = slim(K.constraint('end-effector', frames, [P.as_ps()] * 2, ['LeftFoot', 'RightFoot']), ['LeftFoot', 'RightFoot'])
    print('bed_sit: pelvis', np.round(P.p[0], 3))
    return {'constraints': [c], 'seconds': [6], 'frames': frames, 'world': {'bed': b, 'pelvis': r4(P.p[0] * k)},
            'kimodo': {'pelvis': r4(P.p[0])}}

def after_origin(name, frames=5):
    """where a motion made with `after: {name, frames}` will have its origin, in that one's space: the middle of the
    two hip joints at its frame n − frames (read off two takes: wall-off's startsAt (0.0046, 2.6679) against wall-lean's
    hip joints' middle (0.0105, 2.6695) at its frame 205; table-walk's in К1 likewise; the pelvis joint itself is 5 cm
    off). The new motion's space is the earlier one's moved there, not turned."""
    m = RAW(name); n = m['n']; p = m['p'][n - frames]
    h = (p[K.IDX['LeftLeg']] + p[K.IDX['RightLeg']]) / 2
    return np.array([h[0], 0.0, h[2]])


def bed_lie():
    """Going on from bed-sit: she lies down on her back along the bed, the head towards its head end (+x). Kimodo is
    given, at two frames, the whole pose of its own lying (lie-free: it lay down flat on the floor by itself, arms
    over the head and legs apart; bed-free's "lying" was a sun lounger's recline with the feet on the floor) turned so
    the body lies along the bed, its back's skin on the mattress top (SOMA's skin, Kimodo's space)."""
    k = K_WOMAN; b = BED
    src = RAW('lie-free'); f = 150
    ps = K.pose(src, f)
    d = ps['p'][K.IDX['Head']] - ps['p'][0]; ang = np.arctan2(d[0], d[2])           # head's way over the floor
    r = Rot.from_rotvec([0, np.pi / 2 - ang, 0])                                       # turned to point along +x
    P = Pose(dict(G=r * ps['G'], p=r.apply(ps['p'] - ps['p'][0] * [1, 0, 1])))
    # the pelvis over the bed's middle line, 25 cm to the foot end from the bed's middle
    P.p = P.p + np.array([(b['centre_x'] - 0.08) / k, 0, (b['edge'] + b['depth'] / 2) / k])
    P = placed_against(P, np.array([0, 1.0, 0]), b['top'] / k, ['pelvis', 'spine'])
    v = SS.skin(Rot.concatenate(P.G), P.p)
    head = v[SS.of(['head'])]; heels = v[SS.of(['foot', 'toe'])]
    pillow_h = (head[:, 1].min() - b['top'] / k) * k
    print('bed_lie: pelvis', np.round(P.p[0], 3), 'head lowest over mattress (ours)', round(float(pillow_h), 3),
          'head x', np.round(head[:, 0].min() * k, 3), np.round(head[:, 0].max() * k, 3), 'heels over mattress',
          round(float((heels[:, 1].min() - b['top'] / k) * k), 3), 'body x', np.round(v[:, 0].min() * k, 2), np.round(v[:, 0].max() * k, 2))
    o = after_origin('bed-sit')
    ps2 = P.as_ps(); ps2['p'] = ps2['p'] - o
    frames = [130, 179]
    c = K.constraint('fullbody', frames, [ps2] * 2)
    return {'constraints': [c], 'seconds': [6], 'frames': frames, 'after': {'motion': 'bed-sit', 'frames': 5, 'origin': r4(o)},
            'world': {'pillow': {'h': round(float(pillow_h), 3), 'from_x': round(float(head[:, 0].min() * k), 3)}},
            'kimodo': {'pelvis': r4(P.p[0])}}

DESK = dict(seat=0.42, top=0.72, chair_x=-0.5, chair_z=0.35, thick=0.035)


def desk():
    """The woman stands at a table with a chair beside her (to her right), steps in front of the chair, sits on it and
    puts her forearms on the table top. Written in our scene: the chair's seat 42 cm high, the table top 72 cm. Kimodo
    sat down at a table by itself with its forearms on it (desk-free, frame 160): that pose, turned to face the table
    and put with its buttocks' skin on our seat over the chair's middle, is given as a constraint of both hands (it
    holds the hands, their turn and the pelvis); the table's edge is set where that pose's forearms begin (3 cm in front
    of the elbows' skin), its top where they lie — the pose's forearms lie 30 cm over its seat, so a 42 cm seat gives
    the 72 cm top."""
    k = K_WOMAN; d = DESK
    src = RAW('desk-free')
    P = placed(src, 160, [d['chair_x'] / k, d['chair_z'] / k], 0.0)
    P = placed_against(P, np.array([0, 1.0, 0]), d['seat'] / k, ['pelvis', 'thigh'])
    v = SS.skin(Rot.concatenate(P.G), P.p) * k
    fa = v[SS.of(['foreArm', 'hand'])]
    top = float(fa[:, 1].min()); edge = float(fa[:, 2].min()) - 0.03
    frames = [120, 179]
    c = slim(K.constraint('end-effector', frames, [P.as_ps()] * 2, ['LeftHand', 'RightHand']), ['LeftHand', 'RightHand'])
    print('desk: forearms lie at', round(top, 3), 'edge', round(edge, 3), 'pelvis', np.round(P.p[0] * k, 3))
    return {'constraints': [c], 'seconds': [6], 'frames': frames,
            'world': {**d, 'top_measured': round(top, 3), 'edge': round(edge, 3)}, 'kimodo': {'pelvis': r4(P.p[0])}}

if __name__ == '__main__':
    name = sys.argv[1].replace("-", "_")
    out = globals()[name]()
    os.makedirs(os.path.join(ITEM, 'plans'), exist_ok=True)
    json.dump(out, open(os.path.join(ITEM, 'plans', name + '.json'), 'w'))
    print('constraints', len(json.dumps(out['constraints'])), 'chars')

