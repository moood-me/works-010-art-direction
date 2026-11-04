"""Quick look while fitting: the fitted head (software raster) over the drawing's front and profile, 1 px = 1 unit."""
import sys, numpy as np
from PIL import Image
import mesh as M, head as H

TURN = '/home/user/works-010-art-direction/styles/s2-klaus/pics/turn-anya.png'


def overlay(V, T, out, col=None):
    K, y = H.K, lambda yd: (H.CHIN_Y - yd) * K
    turn = Image.open(TURN).convert('RGB')
    rows = []
    for yaw, x0, frame in ((0, H.XF, 0), (np.pi / 2, None, 1000)):
        if yaw == 0: box = ((0 - H.XF) * K, (500 - H.XF) * K, y(600), y(0))
        else: box = ((0 - H.XS) * K, (500 - H.XS) * K, y(600), y(0))   # profile: screen x = -z → drawing x
        img, _ = M.raster(V, T, yaw, 500, box, col)
        dr = np.asarray(turn.crop((frame, 0, frame + 500, 600))).astype(float)
        m = (img.min(2) < 250)[..., None]
        rows += [img, (dr * 0.55 + img * 0.45 * m + dr * 0.45 * ~m).astype(np.uint8), dr.astype(np.uint8)]
    Image.fromarray(np.hstack(rows)).save(out)


if __name__ == '__main__':
    V, P, patch = H.build()
    overlay(V, M.triangulate(P), sys.argv[1])
