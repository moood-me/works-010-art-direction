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
        wave = math.sin((t - 0.25) / 0.5 * 2 * math.pi * 2) * 0.3 if 0.25 < t < 0.75 else 0
        a = a0 + up * (-math.radians(62) + wave)
        hp = (sh[0] + r * math.cos(a), sh[1] + r * math.sin(a))
        frames.append([(0, 0)] * len(hold) + [(hp[0] - hand[0], hp[1] - hand[1]), (up * 6 + wave * 6, 0)])
    return 'bear', hold + [hand, head], frames

def monster_walk(F=48, cycles=2):
    """the drawn creature walks on the spot, as in the paper's examples: four feet stepping in diagonal pairs,
    the body bobbing, the tail and head swinging a little"""
    feet = [(380, 798), (670, 798), (326, 803), (722, 803)]    # far front, far back, near front, near back
    phase = [0.5, 0.0, 0.0, 0.5]
    body, head, tail = (550, 500), (300, 380), (866, 285)
    frames = []
    for f in range(F * cycles):
        t = (f / F) % 1
        fr = []
        for (x, y), ph in zip(feet, phase):
            q = (t + ph) % 1
            if q < 0.6: dx = 45 - 90 * (q / 0.6); dy = 0                      # on the ground, moving back
            else: s = (q - 0.6) / 0.4; dx = -45 + 90 * ease(s); dy = -38 * math.sin(math.pi * s)   # lifted, forward
            fr.append((dx, dy))
        bob = -8 * math.cos(4 * math.pi * t)
        fr += [(0, bob), (6 * math.sin(2 * math.pi * t), bob * 1.4), (0, 25 * math.sin(2 * math.pi * t))]
        frames.append(fr)
    return 'monster', feet + [body, head, tail], frames

MOTIONS = {'bear-wave': bear_wave, 'monster-walk': monster_walk}

if __name__ == '__main__':
    work, m = sys.argv[1], sys.argv[2]
    ch, cps, frames = MOTIONS[m]()
    fr = json.load(open(os.path.join(work, ch, 'frame.json')))
    T = lambda x, y: ((x - fr['cx']) * fr['s'] + fr['canvas'] / 2, (y - fr['cy']) * fr['s'] + fr['canvas'] / 2)
    L = ['iters 10'] + ['cp %.1f %.1f' % T(*p) for p in cps]
    for f in frames:
        L.append('frame'); L += ['d %.2f %.2f' % (dx * fr['s'], dy * fr['s']) for dx, dy in f]
    open(os.path.join(work, ch, 'anim.txt'), 'w').write('\n'.join(L) + '\n')
