# python3 py/fit.py name → f-<name>.png: the drawn head seen at the picture's angle, laid over the picture by its landmarks
# (the eyes, the nose's tip, the mouth and its corners, the chin): the head's outline and its shading over the picture
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from target import Head
from chars import CH
from scipy.optimize import minimize

def basis(yaw, pitch, roll):
    cyw, syw, cp, spt = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch)
    fwd = np.array([-syw * cp, -spt, -cyw * cp]); right = np.array([cyw, 0, -syw]); up = np.cross(right, fwd)
    cr, sr = np.cos(roll), np.sin(roll); r2 = right * cr + up * sr; u2 = -right * sr + up * cr
    return fwd, r2, u2

def chinpt(H):
    ys = np.linspace(-0.6, -1.2, 121); z = H.rayz(np.c_[np.zeros(121), ys]); k = np.where(~np.isnan(z))[0][-1]
    # the chin's lowest point seen from the front-below: the last height the midline still has skin
    return [0, ys[k], z[k]]
def lands(H, P):
    e = P['eye']; L = P['lips']; N = P['nose']; my = lambda x: L['y'] + L.get('smile', 0) * (x / L['w']) ** 2
    zs = lambda x, y: H.rayz(np.array([[x, y]]))[0]
    cx = L['w'] * L.get('corner', 0.92)
    return {'eL': [e['x'], e['y'], e['z'] + e['r']], 'eR': [-e['x'], e['y'], e['z'] + e['r']], 'tip': [0, N['tip'][0], zs(0, N['tip'][0])],
            'mouth': [0, my(0), zs(0, my(0))], 'mL': [cx, my(cx), zs(cx, my(cx))], 'mR': [-cx, my(-cx), zs(-cx, my(-cx))], 'chin': chinpt(H)}

def trace(H, fwd, right, up, S=360, half=1.6, c=(0, -0.3, -0.4)):
    u = (np.arange(S) + 0.5) / S * 2 - 1; X, Y = np.meshgrid(u * half, -u * half)
    o = X.reshape(-1, 1) * right + Y.reshape(-1, 1) * up - fwd * 4 + np.array(c)
    t = np.zeros(len(o)); hit = np.zeros(len(o), bool); alive = np.ones(len(o), bool)
    for _ in range(90):
        idx = np.where(alive)[0]
        if not len(idx): break
        d = H.f(o[idx] + t[idx, None] * fwd); t[idx] += d * 0.8; h = d < 1e-3; hit[idx[h]] = True; alive[idx[h]] = False; alive[idx[t[idx] > 8]] = False
    img = np.zeros((len(o), 4))
    p = o[hit] + t[hit, None] * fwd; n = H.grad(p); n /= np.linalg.norm(n, axis=1, keepdims=True)
    Lt = -fwd * 0.7 + up * 0.5 - right * 0.4; Lt /= np.linalg.norm(Lt)
    sh = 0.3 + 0.7 * np.clip(n @ Lt, 0, 1); img[hit, :3] = sh[:, None]; img[hit, 3] = 1
    return img.reshape(S, S, 4), (lambda P3: np.c_[((np.asarray(P3) - c) @ right / half + 1) / 2 * S, (1 - (np.asarray(P3) - c) @ up / half) / 2 * S])

def run(name, out=None):
    P = CH[name]; H = Head(P); R = P['pts']; keys = [k for k in R if k in ('eL', 'eR', 'tip', 'mouth', 'mL', 'mR', 'chin')]
    L3 = lands(H, P); A3 = np.array([L3[k] for k in keys]); B = np.array([R[k] for k in keys], float)
    def proj(a):
        f, r, u = basis(*a[:3]); return np.c_[A3 @ r, -(A3 @ u)]
    def sim(a):
        Q = proj(a); qm, bm = Q.mean(0), B.mean(0); Qc, Bc = Q - qm, B - bm
        # least-squares similarity Q→B
        aa = (Qc * Bc).sum() / (Qc ** 2).sum(); bb = (Qc[:, 0] * Bc[:, 1] - Qc[:, 1] * Bc[:, 0]).sum() / (Qc ** 2).sum()
        M = np.array([[aa, -bb], [bb, aa]]); return M, bm - qm @ M.T, ((Qc @ M.T - Bc) ** 2).sum()
    v = P.get('view', [0, 0]); a0 = np.array([v[0], v[1], 0.0])
    if P.get('fitView', True):
        best = min((np.r_[minimize(lambda a: sim(np.r_[a, 0])[2], a0[:2] + d, method='Nelder-Mead').x, 0] for d in [np.zeros(2), [0.25, 0], [-0.25, 0]]), key=lambda a: sim(a)[2])
    else: best = a0
    M, t, err = sim(best)
    f, r, u = basis(*best); img, pj = trace(H, f, r, u)
    # the image's pixel (x, y) ↔ the plane coords (X, -Y): build the map from trace pixels to the picture
    S = img.shape[0]; half = 1.6; c = np.array((0, -0.3, -0.4))
    # trace pixel → plane coords (X along right, -Y along up) relative to origin 0: X = (px/S*2-1)*half + c·r ; -Y = (py/S*2-1)*half - c·u
    ref = Image.open('/home/user/works-010-art-direction/docs/pictures/references/' + P['ref']).convert('RGB')
    cr = P.get('crop') or [0, 0, ref.width, ref.height]; ref = ref.crop(cr)
    K = 3; ref = ref.resize((ref.width * K, ref.height * K), Image.LANCZOS)
    # affine: picture px = K*(M @ plane + t - crop0)
    cr0 = np.array(cr[:2], float)
    # plane coords of trace pixel: X = (px+0.5)/S*2-1)*half + c@r ; Yp = ((py+0.5)/S*2-1)*half - c@u
    s1 = 2 * half / S; ox, oy = -half + c @ r, -half - c @ u
    A2 = K * M @ np.array([[s1, 0], [0, s1]]); b2 = K * (M @ np.array([ox, oy]) + t - cr0)
    Ai = np.linalg.inv(A2); bi = -Ai @ b2
    tim = Image.fromarray((img * 255).astype(np.uint8), 'RGBA')
    warped = tim.transform(ref.size, Image.AFFINE, (Ai[0, 0], Ai[0, 1], bi[0], Ai[1, 0], Ai[1, 1], bi[1]), Image.BILINEAR)
    w = np.asarray(warped).astype(float) / 255; rf = np.asarray(ref).astype(float) / 255
    a = w[..., 3:4]
    # left: the picture with the head's outline; right: the head's shading half over the picture
    edge = np.asarray(Image.fromarray((a[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.FIND_EDGES)).astype(float) / 255
    left = rf.copy(); left[edge > 0.3] = [0, 1, 0.2]
    right = rf * (1 - 0.6 * a) + w[..., :3] * 0.6 * a
    Qp = sim(best)[0]; dr = Image.fromarray((np.concatenate([left, right], 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(dr)
    Q = proj(best) @ M.T + t
    for (bx, by), (qx, qy) in zip(B, Q):
        for off in (0, ref.width):
            d.ellipse([K * (bx - cr[0]) - 4 + off, K * (by - cr[1]) - 4, K * (bx - cr[0]) + 4 + off, K * (by - cr[1]) + 4], outline=(255, 0, 0), width=2)
            d.ellipse([K * (qx - cr[0]) - 3 + off, K * (qy - cr[1]) - 3, K * (qx - cr[0]) + 3 + off, K * (qy - cr[1]) + 3], fill=(0, 80, 255))
    dr.save(out or 'f-%s.png' % name)
    print(name, 'view', np.round(best, 3).tolist(), 'roll %.3f' % np.arctan2(M[1, 0], M[0, 0]), 'err/pt %.2f px' % np.sqrt(err / len(keys)))
if __name__ == '__main__':
    for n in sys.argv[1:]: run(n)
