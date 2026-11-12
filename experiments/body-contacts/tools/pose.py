# Writing the pose a hand constraint carries (tools/kimodo.py: a hand constraint is a whole pose, of which Kimodo holds
# the hands' places and turn and the pelvis's place and heading). Only those count; the rest of that pose is only the
# means to put the hands there, and Kimodo makes the body itself. So the pose is: a standing (or sitting) pose of
# Kimodo's own, its pelvis where the person should be, and its arms turned by plain two-bone IK so that each palm is on
# its place with the hand turned as Kimodo turned a hand lying on something (taken from a frame of a made motion).
import numpy as np
from scipy.spatial.transform import Rotation as Rot
import kimodo as K

CHILDREN = [[k for k in range(77) if K.PARENT[k] == j] for j in range(77)]


def subtree(j):
    out = [j]; i = 0
    while i < len(out): out += CHILDREN[out[i]]; i += 1
    return out


def heading_of(G):
    """the pelvis's heading (radians about y, 0: +z)"""
    f = G[0].apply([0, 0, 1]); return float(np.arctan2(f[0], f[2]))


class Pose:
    def __init__(self, ps):
        self.G = [ps['G'][j] for j in range(77)]; self.p = ps['p'].copy()

    def refk(self):
        G = Rot.concatenate(self.G); self.p = K.fk(G, self.p[0])

    def turn(self, j, r):
        """turn joint j and everything under it by r (in the world), about j"""
        for k in subtree(j): self.G[k] = r * self.G[k]
        self.refk()

    def as_ps(self):
        return dict(G=Rot.concatenate(self.G), p=self.p.copy())

    def palm(self, side): return K.palm(self.p, side)

    def reach(self, side, palm_target, hand_turn):
        """the arm of `side` ('L'/'R') turned so its hand has the world turn `hand_turn` and its palm is at palm_target"""
        s = 'Left' if side == 'L' else 'Right'
        S, E, H = K.IDX[s + 'Arm'], K.IDX[s + 'ForeArm'], K.IDX[s + 'Hand']
        self.turn(H, hand_turn * self.G[H].inv())
        off = self.palm(side) - self.p[H]                       # palm from wrist, with the hand turned as wanted
        want = np.asarray(palm_target) - off
        a = np.linalg.norm(self.p[E] - self.p[S]); b = np.linalg.norm(self.p[H] - self.p[E])
        d = np.clip(np.linalg.norm(want - self.p[S]), abs(a - b) + 1e-4, a + b - 1e-4)
        n = np.cross(self.p[E] - self.p[S], self.p[H] - self.p[E])
        if np.linalg.norm(n) < 1e-6: n = np.cross(self.p[E] - self.p[S], [0, 1, 0])
        n /= np.linalg.norm(n)
        now = np.arccos(np.clip(np.dot((self.p[S] - self.p[E]) / a, (self.p[H] - self.p[E]) / b), -1, 1))
        wantA = np.arccos(np.clip((a * a + b * b - d * d) / (2 * a * b), -1, 1))
        for sgn in (-1, 1):
            G0, p0 = list(self.G), self.p.copy()
            self.turn(E, Rot.from_rotvec(n * sgn * (wantA - now)))
            if abs(np.linalg.norm(self.p[H] - self.p[S]) - d) < 1e-3: break
            self.G, self.p = G0, p0
        u = (self.p[H] - self.p[S]); v = (want - self.p[S])
        ax = np.cross(u, v); ang = np.arctan2(np.linalg.norm(ax), np.dot(u, v))
        if np.linalg.norm(ax) > 1e-9: self.turn(S, Rot.from_rotvec(ax / np.linalg.norm(ax) * ang))
        self.turn(H, hand_turn * self.G[H].inv())
        return float(np.linalg.norm(self.palm(side) - palm_target))


def hand_turn_from(m, f, side, heading=0.0):
    """a hand's turn in a made motion's frame, taken relative to that pelvis's heading, given another heading"""
    ps = K.pose(m, f); s = 'Left' if side == 'L' else 'Right'
    h0 = heading_of(ps['G'])
    return Rot.from_rotvec([0, heading - h0, 0]) * ps['G'][K.IDX[s + 'Hand']]


def placed(m, f, pelvis_xz, heading, dy=0.0):
    """a frame of a made motion turned to `heading` and moved so its pelvis is over pelvis_xz (and dy up)"""
    ps = K.pose(m, f); h0 = heading_of(ps['G'])
    r = Rot.from_rotvec([0, heading - h0, 0])
    p = r.apply(ps['p'] - ps['p'][0] * [1, 0, 1]) + [pelvis_xz[0], dy, pelvis_xz[1]]
    return Pose(dict(G=r * ps['G'], p=p))
