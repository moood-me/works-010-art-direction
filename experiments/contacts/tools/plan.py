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


def table(k=K_WOMAN, stand_back=0.27, spread=0.19, palm_in=0.14, palm_lift=0.022, max_bend=88):
    """The table: the places for one body. Every number is the woman's (moood-woman); for another body each is
    chosen again, as follows (in our world's metres):
      k           the body's hip height / SOMA's (engine/src/retarget.js): its places are divided by it for Kimodo.
                  One number for the whole body: see notes.md "Where the way stops working".
      stand_back  how far the pelvis stands before the table's edge while leaning. Chosen by eye for the woman: her
                  front clear of the edge, her arms reaching the palms with Kimodo's standing pose unbent (bend 0°).
                  For another body: its front (how far its belly or chest is ahead of its pelvis) plus 10–15 cm.
      spread      each palm's distance from the middle: a little wider than the shoulder joints (hers 0.145 each
                  side; 0.19 taken). For another body, scale by its shoulder width.
      palm_in     how far in from the edge the palms' middles lie.
      palm_lift   how high the palm's middle is over the skin under it — only for Kimodo's target height; the page
                  measures the real one each frame (contact-figure.js `under`), so it need not be exact; scale by k.
      max_bend    the input pose is bent forward at the waist (2° steps) until both palms reach; if they don't by
                  this angle, the plan stops with an error (it used to give up silently at 58°)."""
    # the scene (our world): a table 0.74 m high, its near edge 2.2 m ahead
    top, edge, depth, width = 0.74, 2.2, 0.7, 1.2
    palms = {'L': [spread, top + palm_lift, edge + palm_in], 'R': [-spread, top + palm_lift, edge + palm_in]}
    pelvis_world = [0.0, edge - stand_back]
    # in Kimodo's space
    pk = {s: np.array(v) / k for s, v in palms.items()}
    src = RAW('table-free')                  # Kimodo's hands lying on a table (it sat at it): their turn
    turns = {s: hand_turn_from(src, 115, s) for s in 'LR'}
    stand = RAW('table-free2')               # Kimodo standing (it walked up and stood)
    P = placed(stand, 150, np.array(pelvis_world) / k, 0.0, dy=-0.02)
    for a in np.radians(np.arange(0, max_bend + 1, 2)):
        Q = Pose(P.as_ps()); lean_forward(Q, a)
        miss = [Q.reach(s, pk[s], turns[s]) for s in 'LR']
        if max(miss) < 0.003: break
    else:
        raise SystemExit(f'table: the palms do not reach even with the pose bent {max_bend}°: off by {np.round(miss, 3)} m '
                         '(Kimodo metres). Stand the pelvis nearer (stand_back) or lower, or the table is out of this body\'s reach.')
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


def shoulder(stand=0.45):
    """A (the man) walks up to B (the woman, standing in her own Kimodo motion, facing him) and puts his right hand
    on her left shoulder. B's shoulder is a point of her skin (tools/other.mjs: where it is every frame, as the page
    plays her); A's palm is asked onto it — over it by the palm's own thickness — at the touch and at the end."""
    k = K_MAN
    other = json.load(open(os.path.join(ITEM, 'plans', 'shoulder-other.json')))
    palm_lift = 0.025
    frames = [119, 179]          # the hand on the shoulder from 4 s, still there at the end (6 s)
    targets = [np.array(other['at'][f]) + [0, palm_lift, 0] for f in frames]
    src = RAW('shoulder-free')               # Kimodo stretching the right arm forward, palm down, by itself
    turn = hand_turn_from(src, 30, 'R')
    poses = []
    for tw in targets:
        tk = tw / k
        # standing `stand` (Kimodo's metres) short of the point, facing it, 12 cm to its left (his right hand reaches
        # it). The first take stood 60 cm short: the arm came out straight and level, like a bar, and our man's arm
        # (2 cm shorter than SOMA's scaled) could not reach the last 2–4 cm
        P = placed(src, 30, [tk[0] + 0.12, tk[2] - stand], 0.0)
        miss = P.reach('R', tk, turn)
        poses.append(P.as_ps())
        print('shoulder: palm off by', round(miss, 4), 'pelvis', np.round(P.p[0], 3), 'target', np.round(tk, 3))
    c = K.constraint('end-effector', frames, poses, ['RightHand'])
    return {'constraints': [c], 'seconds': [6], 'frames': frames,
            'world': {'other': {k2: other[k2] for k2 in ('who', 'motion', 'place', 'vertex')}, 'palm_lift': palm_lift,
                      'targets': [r4(t) for t in targets]},
            'kimodo': {'targets': [r4(t / k) for t in targets], 'pelvis': [r4(p['p'][0]) for p in poses]}}

def armchair_knees(mode='feet'):
    """the armchair again, the knees together (Pavel: she sat with the knees wide apart). The pose sent is the same
    as `armchair` with its thighs turned in at the hips (about the forward axis) until the knees are 20 cm apart, the
    hip joints' own width; then either its feet are held too (mode 'feet': an end-effector constraint on both hands
    and both feet), or the whole pose (mode 'fullbody': every joint's place, so the knees as well)."""
    out = armchair()
    c0 = out['constraints'][0]
    # the pose again (as armchair() made it)
    k = K_WOMAN; w = out['world']; heading = np.pi
    sit = RAW('chair-free'); src = RAW('table-free')
    turns = {s: hand_turn_from(src, 115, s, heading) for s in 'LR'}
    P0 = placed(sit, 175, np.array(w['pelvis']) / k, heading)
    P = placed(sit, 175, np.array(w['pelvis']) / k, heading, dy=(w['armchair']['seat'] + 0.175) / k - P0.p[0, 1])
    fwd = Rot.from_rotvec([0, heading, 0]).apply([0, 0, 1])
    I = K.IDX; mid = P.p[0]
    floor_y = {s: sit['p'][175, I[s + 'Foot'], 1] for s in ('Left', 'Right')}   # Kimodo's own seated ankles
    foot_turn = {s: P.G[I[s + 'Foot']] for s in ('Left', 'Right')}                  # the feet keep Kimodo's turn
    for s, sgn in (('Left', 1), ('Right', -1)):
        hip, knee = I[s + 'Leg'], I[s + 'Shin']
        side = np.cross([0, 1, 0], fwd)                  # the person's left
        want = 0.10                                      # the knee 10 cm from the middle
        best = None
        for a in np.radians(np.arange(-40, 40.5, 0.5)):
            Q = Pose(P.as_ps()); Q.turn(hip, Rot.from_rotvec([0, a, 0]))
            off = np.dot(Q.p[knee] - mid, side) * (1 if s == 'Left' else -1)
            if best is None or abs(off - want) < best[0]: best = (abs(off - want), a)
        P.turn(hip, Rot.from_rotvec([0, best[1], 0]))
        print(s, 'thigh turned', round(float(np.degrees(best[1])), 1), 'deg')
    # the pelvis is higher than in Kimodo's own sitting (our seat): each thigh pitched down and its shin turned at the
    # knee so that the ankle is as high over the floor as in Kimodo's own sitting, 4 cm in front of the knee
    side = np.cross([0, 1, 0], fwd)
    for s in ('Left', 'Right'):
        hip, kn, foot = I[s + 'Leg'], I[s + 'Shin'], I[s + 'Foot']
        best = None
        for a in np.radians(np.arange(-30, 30.5, 1)):
            for b in np.radians(np.arange(-40, 40.5, 1)):
                Q = Pose(P.as_ps()); Q.turn(hip, Rot.from_rotvec(side * a)); Q.turn(kn, Rot.from_rotvec(side * b))
                ahead = np.dot(Q.p[foot] - Q.p[kn], fwd)
                d = abs(Q.p[foot, 1] - floor_y[s]) + abs(ahead - 0.04)
                if best is None or d < best[0]: best = (d, a, b)
        P.turn(hip, Rot.from_rotvec(side * best[1])); P.turn(kn, Rot.from_rotvec(side * best[2]))
        print(s, 'thigh pitched', round(float(np.degrees(best[1]))), 'shin', round(float(np.degrees(best[2]))), 'deg; off', round(best[0], 3))
    for s in ('Left', 'Right'): P.turn(I[s + 'Foot'], foot_turn[s] * P.G[I[s + 'Foot']].inv())
    for s in 'LR': P.reach(s, np.array(w['palms'][s]) / k, turns[s])
    I2 = lambda n: np.round(P.p[I[n]], 3)
    print('knees', I2('LeftShin'), I2('RightShin'), 'feet', I2('LeftFoot'), I2('RightFoot'))
    frames = out['frames']
    if mode == 'feet':
        c = K.constraint('end-effector', frames, [P.as_ps()] * len(frames), ['LeftHand', 'RightHand', 'LeftFoot', 'RightFoot'])
    else:
        c = K.constraint('fullbody', frames, [P.as_ps()] * len(frames))
    out['constraints'] = [c]; out['mode'] = mode
    out['kimodo']['knees'] = [r4(P.p[I['LeftShin']]), r4(P.p[I['RightShin']])]
    return out


def armchair_knees_full():
    return armchair_knees('fullbody')

def shoulder2(heading_deg=60.0, ahead=0.36, aside=0.12, hand_deg=25.0):
    """the shoulder again, as the agent of the two-people task got it natural (the coordinator's note, 2026-11-12):
    he stands near her but to the side — off her left shoulder, not in front of her face, about half a metre from
    her — facing her (heading 60°), the point on the top of her shoulder over the arm's joint (away from the neck),
    his palm on it 36 cm ahead of his pelvis and 12 cm to his right, so the elbow bends and hangs; the hand's
    fingers point over her shoulder towards her back (25° from +z, not along his own forward, which points at her
    neck). His look at her is asked in the prompt."""
    k = K_MAN
    other = json.load(open(os.path.join(ITEM, 'plans', 'shoulder2-other.json')))
    palm_lift = 0.025
    frames = [119, 179]
    h = np.radians(heading_deg)
    f = np.array([np.sin(h), 0, np.cos(h)]); r = np.array([-np.cos(h), 0, np.sin(h)])     # his forward, his right
    src = RAW('shoulder-free')
    turn = hand_turn_from(src, 30, 'R', np.radians(hand_deg))
    poses = []
    for fr in frames:
        tw = np.array(other['at'][fr]) + [0, palm_lift, 0]
        pel = tw - ahead * f - aside * r
        tk = tw / k
        P = placed(src, 30, [pel[0] / k, pel[2] / k], h)
        miss = P.reach('R', tk, turn)
        poses.append(P.as_ps())
        print('shoulder2: palm off by', round(miss, 4), 'pelvis (world)', np.round(pel[[0, 2]], 3),
              'from her pelvis', round(float(np.hypot(pel[0], pel[2] - 1.9)), 3), 'target', np.round(tw, 3))
    c = K.constraint('end-effector', frames, poses, ['RightHand'])
    return {'constraints': [c], 'seconds': [6], 'frames': frames,
            'world': {'other': {k2: other[k2] for k2 in ('who', 'motion', 'place', 'vertex')}, 'palm_lift': palm_lift,
                      'heading_deg': heading_deg},
            'kimodo': {'pelvis': [r4(p['p'][0]) for p in poses]}}

if __name__ == '__main__':
    name = sys.argv[1].replace("-", "_")
    out = globals()[name]()
    os.makedirs(os.path.join(ITEM, 'plans'), exist_ok=True)
    json.dump(out, open(os.path.join(ITEM, 'plans', name + '.json'), 'w'))
    print('constraints', len(json.dumps(out['constraints'])), 'chars')

