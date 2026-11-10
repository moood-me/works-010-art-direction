"""Pictures and films of a С14 character in 3D: python3 make.py [compare] [steps] [expr] [hero] [films | turn walk life …]
Renders go through the page (web/view.html?shots) by shots.mjs — a browser drawing frames, a heavy run: taken through
the shared locks (heavy.sh). Work files in /home/user/cache/to3d-<folder>. What is the character's own: character.py."""
import json, os, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import character as C   # noqa: E402

PICS = os.path.join(HERE, '..', 'pics')
CACHE = '/home/user/cache/to3d-' + C.FOLDER
DRAW = os.path.join(CACHE, 'drawing')
os.makedirs(PICS, exist_ok=True)
FONT = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
U, D = 0.003, math.pi / 180
INK = (91, 74, 60)


def shots(jobs, name):
    d = os.path.join(CACHE, 'r', name)
    os.makedirs(d, exist_ok=True)
    jf = os.path.join(d, 'jobs.json')
    json.dump(jobs, open(jf, 'w'))
    subprocess.run([os.path.join(HERE, 'heavy.sh'), 'node', os.path.join(HERE, 'shots.mjs'), jf, d], check=True)
    return d


def jpg(img, name, q=88):
    img.convert('RGB').save(os.path.join(PICS, name), quality=q)
    print('pic', name, img.size)


def label(img, text, x, y, size=24, fill=INK):
    dr = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT, size)
    w = dr.textlength(text, font=f)
    dr.text((x - w / 2, y), text, font=f, fill=fill)


def row(tiles, labels, pad=46, size=24, bg=None):
    bg = bg or tuple(int(C.SHEET[i:i + 2], 16) for i in (1, 3, 5))
    w = sum(t.size[0] for t in tiles)
    h = max(t.size[1] for t in tiles)
    out = Image.new('RGB', (w, h + pad), bg)
    x = 0
    for t, lb in zip(tiles, labels):
        out.paste(t.convert('RGB'), (x, 0))
        label(out, lb, x + t.size[0] / 2, h + 8, size)
        x += t.size[0]
    return out


def stack(rows):
    w = max(r.size[0] for r in rows)
    out = Image.new('RGB', (w, sum(r.size[1] for r in rows)), rows[0].getpixel((2, 2)))
    y = 0
    for r in rows:
        out.paste(r, ((w - r.size[0]) // 2, y))
        y += r.size[1]
    return out


STILL = dict(alive=False, motion=None, expr='calm', talk=False, ground='none', headYaw=0, headTilt=0, hide=None, only=None,
             look=dict(flat=False, grain=1, bg=C.SHEET))


def fig_cam(yaw=0):
    return dict(pxu=C.FIG_S, fov=13, yaw=yaw * D, pitch=0, target=[0, (880 - 500) / C.FIG_S * U, 0])


def bust_cam(yaw=0, s=None, cy=440, H=960):
    pxu = (s or C.BUST_S) / C.HS
    return dict(pxu=pxu, fov=13, yaw=yaw * D, pitch=0, target=[0, C.HEAD_H * U - (H / 2 - cy) / pxu * U, 0])


def compare():
    jobs = [dict(name='figure', size=[800, 1000], set=dict(STILL, cam=fig_cam(), **C.DRAWN_HEAD)),
            dict(name='figure-front', size=[800, 1000], set=dict(STILL, cam=fig_cam())),
            dict(name='figure-q', size=[800, 1000], set=dict(STILL, cam=fig_cam(-35))),
            dict(name='figure-side', size=[800, 1000], set=dict(STILL, cam=fig_cam(-90))),
            dict(name='figure-back', size=[800, 1000], set=dict(STILL, cam=fig_cam(155))),
            dict(name='bust-front', size=[800, 960], set=dict(STILL, cam=bust_cam())),
            dict(name='bust-q', size=[800, 960], set=dict(STILL, cam=bust_cam(C.Q_YAW))),
            dict(name='bust-side', size=[800, 960], set=dict(STILL, cam=bust_cam(-90))),
            dict(name='bust-back', size=[800, 960], set=dict(STILL, cam=bust_cam(140)))]
    d = shots(jobs, 'compare')
    R = lambda n: Image.open(os.path.join(d, n + '.png')).convert('RGB')
    Dr = lambda n: Image.open(os.path.join(DRAW, n + '.png')).convert('RGB')
    crop = lambda im: im.crop((150, 60, 650, 960))
    a, b = Dr('figure'), R('figure')
    jpg(row([crop(a), crop(b), crop(Image.blend(a, b, .5))], ['рисунок', '3D', 'одно на другом']), 'compare-figure.jpg')
    rows = []
    for n, ru in [('front', 'анфас'), ('q', 'три четверти')]:
        if not os.path.exists(os.path.join(DRAW, 'bust-%s.png' % n)):
            continue
        a, b = Dr('bust-' + n), R('bust-' + n)
        c = lambda im: im.crop((90, 110, 710, 880)).resize((496, 616), Image.LANCZOS)
        rows.append(row([c(a), c(b), c(Image.blend(a, b, .5))], ['рисунок, ' + ru, '3D', 'одно на другом']))
    jpg(stack(rows), 'compare-head.jpg')
    c = lambda im: im.crop((90, 110, 710, 880)).resize((496, 616), Image.LANCZOS)
    jpg(row([c(R('bust-front')), c(R('bust-q')), c(R('bust-side')), c(R('bust-back'))], ['анфас', 'три четверти', 'профиль', 'сзади сбоку']), 'head-around.jpg')
    c = lambda im: im.crop((200, 60, 600, 960))
    jpg(row([c(R('figure-front')), c(R('figure-q')), c(R('figure-side')), c(R('figure-back'))], ['анфас', 'три четверти', 'профиль', 'сзади']), 'figure-around.jpg')


def steps():
    base = dict(STILL, cam=fig_cam(-28))
    H = C.STEPS
    jobs = [dict(name='s1', size=[800, 1000], set=dict(base, hide=H[0], look=dict(flat=True, grain=0, bg=C.SHEET))),
            dict(name='s2', size=[800, 1000], set=dict(base, hide=H[1], look=dict(flat=True, grain=0, bg=C.SHEET))),
            dict(name='s3', size=[800, 1000], set=dict(base, look=dict(flat=True, grain=0, bg=C.SHEET))),
            dict(name='s4', size=[800, 1000], set=dict(base))]
    d = shots(jobs, 'steps')
    c = lambda n: Image.open(os.path.join(d, n + '.png')).crop((190, 60, 610, 960))
    jpg(row([c('s1'), c('s2'), c('s3'), c('s4')], C.STEP_RU, size=21), 'steps.jpg')


def expr():
    cam = bust_cam(0, C.EXPR_S, 300, 620)
    jobs = [dict(name=e, size=[560, 620], set=dict(STILL, expr=e, cam=cam)) for e in C.EXPRS]
    cam2 = bust_cam(C.Q_YAW, C.EXPR_S, 300, 620)
    jobs += [dict(name=e + '-q', size=[560, 620], set=dict(STILL, expr=e, cam=cam2)) for e in C.EXPRS]
    d = shots(jobs, 'expr')
    c = lambda im: im.crop((60, 40, 500, 580)).resize((330, 405), Image.LANCZOS)
    r1 = row([c(Image.open(os.path.join(DRAW, 'expr-%s.png' % e))) for e in C.EXPRS], ['рисунок: ' + C.EXPR_RU[e] for e in C.EXPRS], size=20)
    r2 = row([c(Image.open(os.path.join(d, e + '.png'))) for e in C.EXPRS], ['3D'] * len(C.EXPRS), size=20)
    r3 = row([c(Image.open(os.path.join(d, e + '-q.png'))) for e in C.EXPRS], ['3D, три четверти'] * len(C.EXPRS), size=20)
    jpg(stack([r1, r2, r3]), 'expressions.jpg')


def hero():
    jobs = [dict(name='hero', size=[900, 1200], warm=1.2, set=dict(STILL, alive=True, lifeSeed=3, ground='disc', cam=dict(pxu=1.62, fov=13, yaw=-.42, pitch=.035, target=[0, .86, 0]), **C.HERO)),
            dict(name='portrait', size=[900, 1080], warm=1.2, set=dict(STILL, alive=True, lifeSeed=3, cam=dict(bust_cam(-22, 2.3, 500, 1080)), **C.HERO))]
    d = shots(jobs, 'hero')
    jpg(Image.open(os.path.join(d, 'hero.png')), 'hero.jpg', 90)
    jpg(Image.open(os.path.join(d, 'portrait.png')), 'portrait.jpg', 90)


def film(name, job, fps=12):
    d = shots([dict(job, name=name)], 'film-' + name)
    out = os.path.join(PICS, name + '.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', os.path.join(d, name, 'f%04d.png'), '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p', '-crf', '24', '-r', '24', '-movflags', '+faststart', out], check=True)
    # a strip of moments to look at
    fr = sorted(os.listdir(os.path.join(d, name)))
    pick = [fr[int(i * (len(fr) - 1) / 7)] for i in range(8)]
    ims = [Image.open(os.path.join(d, name, f)).convert('RGB') for f in pick]
    w, h = ims[0].size
    st = Image.new('RGB', (w * 4 // 2, h * 2 // 2))
    for i, im in enumerate(ims):
        st.paste(im.resize((w // 2, h // 2), Image.LANCZOS), ((i % 4) * (w // 2), (i // 4) * (h // 2)))
    st.save(os.path.join(CACHE, 'strip-%s.jpg' % name), quality=85)
    print('film', name, os.path.getsize(out) // 1024, 'KB')


SZ = [640, 800]


def turn():
    n = 84
    frames = [dict(cam=dict(yaw=-2 * math.pi * (i + 1) / n)) for i in range(n)]
    film('turn', dict(size=SZ, set=dict(STILL, alive=True, lifeSeed=5, ground='disc', cam=dict(pxu=1.12, fov=13, yaw=0, pitch=.05, target=None, h=.86)), frames=frames, dt=1 / 12))


def walk():
    film('walk', dict(size=SZ, set=dict(STILL, alive=True, lifeSeed=9, t=0, cam=dict(pxu=1.12, fov=13, yaw=-.75, pitch=.06, target=None, h=.86, smooth=4), **C.WALK), frames=96, dt=1 / 12))


def motion(name):
    m = C.MOTIONS[name]
    film(name, dict(size=SZ, set=dict(STILL, alive=True, lifeSeed=4, t=0, loop=False, ground='disc', motion=name, cam=dict(pxu=1.12, fov=13, yaw=m.get('yaw', -.5), pitch=.05, target=None, h=.86, smooth=4)), frames=m['frames'], dt=1 / 12))


def life():
    """A close look at the live face: blinks, glances, the head after the gaze, expressions one into another, speech."""
    fr = []
    for i in range(132):
        o = {}
        for at, e in C.LIFE_EXPR:
            if i == at:
                o['expr'] = e
        for at, tk in C.LIFE_TALK:
            if i == at:
                o['talk'] = tk
        fr.append(o)
    film('life', dict(size=[640, 720], set=dict(STILL, alive=True, lifeSeed=12, cam=bust_cam(-14, 1.55, 330, 720)), frames=fr, dt=1 / 12))


ALL = dict(compare=compare, steps=steps, expr=expr, hero=hero, turn=turn, walk=walk, life=life)
if __name__ == '__main__':
    for a in sys.argv[1:]:
        if a == 'films':
            for f in C.FILMS:
                ALL[f]() if f in ALL else motion(f)
        elif a in ALL:
            ALL[a]()
        else:
            motion(a)
