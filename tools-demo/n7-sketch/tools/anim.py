# Control-point motions for mm_harness, as one would record them in Monster Mash's animate mode by dragging
# points with the mouse: points are put on the model in the front view; some held still, some moved.
# Coordinates are pixels of our front picture (frame.json maps them to Monster Mash's canvas).
# usage: python3 anim.py <workdir> <motion>   -> <workdir>/<char>/anim.txt
import json, math, os, sys

def ease(t): return t * t * (3 - 2 * t)

def bear_wave(F=60):
    """the bear lifts its right arm and waves, its head leaning a little after it; feet, body, left hand held"""
    hold = [(196, 368), (278, 368), (228, 255), (100, 284)]
    sh, hand = (300, 228), (376, 282)
    r = math.dist(sh, hand); a0 = math.atan2(hand[1] - sh[1], hand[0] - sh[0])
    head = (228, 100)
    frames = []
    for f in range(F):
        t = f / (F - 1)
        up = ease(min(1, t / 0.25)) * ease(min(1, (1 - t) / 0.25))           # raise, hold, lower
        wave = math.sin((t - 0.25) / 0.5 * 2 * math.pi * 2) * 0.35 if 0.25 < t < 0.75 else 0
        a = a0 + up * (-math.radians(110) + wave)
        hp = (sh[0] + r * math.cos(a), sh[1] + r * math.sin(a))
        frames.append([(0, 0)] * len(hold) + [(hp[0] - hand[0], hp[1] - hand[1]), (up * 10 + wave * 8, 0)])
    return 'bear', hold + [hand, head], frames

MOTIONS = {'bear-wave': bear_wave}

if __name__ == '__main__':
    work, m = sys.argv[1], sys.argv[2]
    ch, cps, frames = MOTIONS[m]()
    fr = json.load(open(os.path.join(work, ch, 'frame.json')))
    T = lambda x, y: ((x - fr['cx']) * fr['s'] + fr['canvas'] / 2, (y - fr['cy']) * fr['s'] + fr['canvas'] / 2)
    L = ['iters 6'] + ['cp %.1f %.1f' % T(*p) for p in cps]
    for f in frames:
        L.append('frame'); L += ['d %.2f %.2f' % (dx * fr['s'], dy * fr['s']) for dx, dy in f]
    open(os.path.join(work, ch, 'anim.txt'), 'w').write('\n'.join(L) + '\n')
