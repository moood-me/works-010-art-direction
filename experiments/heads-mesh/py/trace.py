# python3 py/trace.py name → t-<name>.png: the drawn head alone, sphere-traced (front, 3/4, side, the picture's angle)
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image
from target import Head
from chars import CH
def render(H, yaw, pitch, S=300, half=1.45, cy=-0.25):
    u = (np.arange(S) + 0.5) / S * 2 - 1; X, Y = np.meshgrid(u * half, -u * half + cy)
    cyw, syw, cp, spt = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch)
    fwd = np.array([-syw * cp, -spt, -cyw * cp]); right = np.array([cyw, 0, -syw]); up = np.cross(right, fwd)
    o = X.reshape(-1, 1) * right + Y.reshape(-1, 1) * up - fwd * 4 + [0, cy, -0.4]
    t = np.zeros(len(o)); hit = np.zeros(len(o), bool); alive = np.ones(len(o), bool)
    for _ in range(90):
        idx = np.where(alive)[0]
        if not len(idx): break
        d = H.f(o[idx] + t[idx, None] * fwd)
        t[idx] += d * 0.8; h = d < 1e-3; hit[idx[h]] = True; alive[idx[h]] = False; alive[idx[t[idx] > 8]] = False
    img = np.full((len(o), 3), 0.86)
    p = o[hit] + t[hit, None] * fwd; n = H.grad(p); n /= np.linalg.norm(n, axis=1, keepdims=True)
    L = -fwd * 0.7 + up * 0.5 - right * 0.4; L /= np.linalg.norm(L)
    sh = 0.35 + 0.65 * np.clip(n @ L, 0, 1); img[hit] = sh[:, None] * [0.93, 0.66, 0.52]
    return (img.reshape(S, S, 3) * 255).astype(np.uint8)
if __name__ == '__main__':
    n = sys.argv[1]; P = CH[n]; H = Head(P); v = P.get('view', [0, 0])
    ims = [render(H, a, b) for a, b in [(v[0], v[1]), (0, 0.05), (0.65, 0.05), (1.5708, 0.05)]]
    Image.fromarray(np.concatenate(ims, 1)).save('t-%s.png' % n)
