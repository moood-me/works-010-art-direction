"""GarmentCode's body measurements (docs/Body Measurements GarmentCode.pdf) taken from a mesh with a part segmentation.
GarmentCode's own measuring tool (GarmentMeasurements) works only on its own body model, so for Anny they are taken here.
Run on GarmentCode's mean body first to compare with its own numbers:  python measure.py DIR NAME [arm_angle]
Mesh: metres, y up, facing +z, left +x.  Prints the yaml (cm, degrees)."""
import json, sys, math, numpy as np, trimesh
from scipy.spatial import ConvexHull

d, name = sys.argv[1], sys.argv[2]
m = trimesh.load(f'{d}/{name}.obj', process=False)
V, F = np.asarray(m.vertices), np.asarray(m.faces)
seg = json.load(open(f'{d}/ggg_body_segmentation.json'))
lab = np.full(len(V), '', object)
for k, ids in seg.items(): lab[ids] = k
def sub(keep):
    fm = np.all(np.isin(lab[F], keep), axis=1)
    return trimesh.Trimesh(V, F[fm], process=False)
torso = sub(['body', 'left_leg', 'right_leg', 'face_internal'])  # no arms: a tape measure goes under them
larm = sub(['left_arm']); lleg = sub(['left_leg'])
floor = V[:, 1].min(); top = V[:, 1].max()

def loops(mesh, y, normal=(0, 1, 0), origin=None):
    o = origin if origin is not None else (0, y, 0)
    s = mesh.section(plane_origin=o, plane_normal=normal)
    if s is None: return []
    return [np.asarray(p) for p in s.discrete]
def hull_len(pts2):
    h = ConvexHull(pts2); q = pts2[h.vertices]; return np.sum(np.linalg.norm(q - np.roll(q, 1, 0), axis=1)), q
def ring(y, mesh=torso):
    """the tape at height y round the torso (all loops together), as its convex hull in (x, z)"""
    L = loops(mesh, y)
    if not L: return 0, None, 0
    P = np.vstack(L)[:, [0, 2]]
    l, q = hull_len(P); return l, q, len(L)
def back_part(q):
    """from one balance line (the side, at the widest x) round the back to the other"""
    i0, i1 = np.argmin(q[:, 0]), np.argmax(q[:, 0])
    n = len(q); a = [(i0 + k) % n for k in range((i1 - i0) % n + 1)]; b = [(i1 + k) % n for k in range((i0 - i1) % n + 1)]
    def length(ix): p = q[ix]; return np.sum(np.linalg.norm(np.diff(p, axis=0), axis=1)), p[:, 1].mean()
    (la, za), (lb, zb) = length(a), length(b)
    return la if za < zb else lb

ys = np.arange(floor + 0.3, top, 0.002)
R = [ring(y) for y in ys]; C = np.array([r[0] if r[0] else np.nan for r in R]); NL = np.array([r[2] for r in R])
H = top - floor
# crotch: the highest height where the torso's tape falls apart into two legs
legs = [i for i, y in enumerate(ys) if y < floor + 0.6 * H and NL[i] >= 2]
crotch = ys[max(legs)]
# armpit: lowest height where the arms join the trunk (the whole body's section at that height is one piece with arms)
def nloops_all(y): return len(loops(m, y))
J = sys.argv[4:] and None
# chest region between armpits and waist: find with front profile
def front_z(y, xmin, xmax, mesh=torso):
    L = loops(mesh, y)
    if not L: return None
    P = np.vstack(L); P = P[(P[:, 0] >= xmin) & (P[:, 0] <= xmax)]
    return P[np.argmax(P[:, 2])] if len(P) else None
def back_z(y, xmin, xmax, mesh=torso):
    L = loops(mesh, y)
    if not L: return None
    P = np.vstack(L); P = P[(P[:, 0] >= xmin) & (P[:, 0] <= xmax)]
    return P[np.argmin(P[:, 2])] if len(P) else None
# armpit: going down from the neck, the first height where the arm part and the trunk are no longer joined
arm_pts = V[lab == 'left_arm']
armpit = None
for y in np.arange(floor + 0.6 * H, floor + 0.9 * H, 0.002)[::-1]:
    pass
# the arm's lowest junction with the trunk: arm vertices nearest to the trunk's vertices, take the lowest of those
from scipy.spatial import cKDTree
fl = lab[F]; mixed = F[np.any(fl == 'left_arm', 1) & np.any(fl == 'body', 1)]
junction = V[np.unique(mixed[lab[mixed] == 'left_arm'])]
armpit = junction[:, 1][junction[:, 0] < np.percentile(junction[:, 0], 60)].min()
shoulder_pts = junction[junction[:, 1] > armpit + 0.05]
acrom = shoulder_pts[np.argmax(shoulder_pts[:, 1])] if len(shoulder_pts) else junction[np.argmax(junction[:, 1])]
# acromion: the top-outer end of the shoulder, on the arm/trunk junction: highest junction point
acrom = junction[np.argmax(junction[:, 1])]
# waist: narrowest tape between crotch+ and armpit
w_rng = (ys > crotch + 0.12) & (ys < armpit - 0.08)
wi = np.nanargmin(np.where(w_rng, C, 1e9)); waist_y = ys[wi]; waist = C[wi]
# bust: the tape at the height of the breasts' most forward point
cand = [(y, front_z(y, 0.03, 0.15)) for y in ys[(ys > waist_y + 0.05) & (ys < armpit)]]
bust_y, bp = max(((y, p) for y, p in cand if p is not None), key=lambda t: t[1][2])
bi = int(np.argmin(np.abs(ys - bust_y))); bust = C[bi]
# underbust: narrowest below the bust within 12 cm
u_rng = (ys < bust_y - 0.03) & (ys > max(bust_y - 0.09, waist_y))
ui = np.nanargmin(np.where(u_rng, C, 1e9)); underbust = C[ui]
# hips: the tape at the height of the bottom's most backward point
cand = [(y, back_z(y, 0.05, 0.15)) for y in ys[(ys > crotch) & (ys < waist_y - 0.04)]]
hip_y, bum = min(((y, p) for y, p in cand if p is not None), key=lambda t: t[1][2])
hi = int(np.argmin(np.abs(ys - hip_y))); hips = C[hi]
# bust points, bum points: the most forward / most backward point of each side at those heights
bust_points = 2 * bp[0]; bum_points = 2 * bum[0]
# nape and neck base: the neck's narrowest tape above the armpits, its base where it starts to widen to the shoulders
n_rng = (ys > armpit) & (ys < top - 0.12)
ni = np.nanargmin(np.where(n_rng, C, 1e9)); neck_y = ys[ni]
base_i = ni
while base_i > 0 and C[base_i - 1] < C[ni] * 1.12 and R[base_i - 1][1] is not None: base_i -= 1
nape_y = ys[base_i]
neck_q = R[base_i][1]; neck_w = back_part(neck_q)
neck_side_x = neck_q[:, 0].max()
head_l = top - nape_y
# back profile from nape to waist (x = 0): tape along the back's convex profile
def profile(x, y0, y1, side):
    """tape along the front (side +1) or back (-1) of the body in the plane at x, from height y1 down to y0:
    the outward chain of the profile's convex hull (as a tape measure lies over hollows)"""
    pts = []
    for y in np.arange(y0, y1 + 1e-9, 0.004):
        p = (back_z if side < 0 else front_z)(y, x - 0.01, x + 0.01)
        if p is not None: pts.append([y, side * p[2]])
    P = np.array(sorted(pts))
    chain = []
    for p in P:   # upper hull in (y, side*z) by the monotone chain
        while len(chain) >= 2 and np.cross(chain[-1] - chain[-2], p - chain[-2]) >= 0: chain.pop()
        chain.append(p)
    q = np.array(chain)
    return np.sum(np.linalg.norm(np.diff(q, axis=0), axis=1)), P
waist_line, _ = profile(0.0, waist_y, nape_y, -1)
wob, Pf = profile(bp[0], waist_y, nape_y - 0.0, +1)
bl, _ = profile(bp[0], bust_y, nape_y - 0.0, +1)
waist_over_bust_line = wob; bust_line = bl
vert_bust_line = nape_y - bust_y
hips_line = waist_y - hip_y
crotch_hip_diff = hip_y - crotch
# widest thigh of one leg (below the crotch)
lc = [ring(y, lleg)[0] for y in np.arange(crotch - 0.15, crotch - 0.005, 0.004)]
leg_circ = max(lc)
# wrist: the arm's tape across the forearm, at its thinnest near the hand
hand_dir = None
arm = arm_pts[arm_pts[:, 0] > acrom[0]]
tip = arm[np.argmax(arm[:, 0] - arm[:, 1])]
axis = tip - acrom; axis /= np.linalg.norm(axis)
best = 1e9
for t in np.linspace(0.55, 0.85, 40):
    o = acrom + axis * t * np.linalg.norm(tip - acrom)
    L = loops(larm, 0, normal=axis, origin=o)
    if not L: continue
    P = np.vstack(L); u = np.cross(axis, [0, 0, 1]); u /= np.linalg.norm(u); w = np.cross(axis, u)
    l, _ = hull_len(np.c_[P @ u, P @ w])
    if l < best: best, wrist_o = l, o
wrist = best
arm_length = np.linalg.norm(wrist_o - acrom)
shoulder_w = 2 * acrom[0]
shoulder_incl = math.degrees(math.atan2(nape_y + 0.0 - acrom[1], acrom[0] - neck_side_x))
# hip inclination: the side from the waist to the hips
wq, hq = R[wi][1], R[hi][1]
hip_inclination = math.degrees(math.atan2(hq[:, 0].max() - wq[:, 0].max(), hips_line))
armscye_depth = acrom[1] - armpit
out = dict(arm_length=arm_length * 100, arm_pose_angle=float(sys.argv[3]) if len(sys.argv) > 3 else 45.0,
    armscye_depth=armscye_depth * 100, back_width=back_part(R[bi][1]) * 100, bum_points=bum_points * 100,
    bust=bust * 100, bust_line=bust_line * 100, bust_points=bust_points * 100, crotch_hip_diff=crotch_hip_diff * 100,
    head_l=head_l * 100, height=H * 100, hip_back_width=back_part(R[hi][1]) * 100, hip_inclination=hip_inclination,
    hips=hips * 100, hips_line=hips_line * 100, leg_circ=leg_circ * 100, neck_w=neck_w * 100, shoulder_incl=shoulder_incl,
    shoulder_w=shoulder_w * 100, underbust=underbust * 100, vert_bust_line=vert_bust_line * 100, waist=waist * 100,
    waist_back_width=back_part(wq) * 100, waist_line=waist_line * 100, waist_over_bust_line=waist_over_bust_line * 100,
    wrist=wrist * 100)
import yaml
print(yaml.dump({'body': {k: round(float(v), 4) for k, v in out.items()}}))
print('# heights (m): floor', round(floor,3), 'crotch', round(crotch,3), 'hip', round(hip_y,3), 'waist', round(waist_y,3),
      'bust', round(bust_y,3), 'armpit', round(armpit,3), 'nape', round(nape_y,3), 'top', round(top,3), file=sys.stderr)
print('# waist centre (x, z):', wq.mean(0).round(4), file=sys.stderr)
