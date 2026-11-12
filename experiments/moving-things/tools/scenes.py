# The page's scenes (scenes.json) from the plans (plans/*.json): the things where the plans put them, the person and
# their motions, the places the palms were asked to come to (and over which frames the small correction is weighed
# in), and what is held from which frame to which. Russian text is what a person reads on the page.
#   python3 tools/scenes.py
# Copied from К1 (experiments/contacts/tools/scenes.py) and changed: things here move — `holds` says which thing is
# held by which hand(s) from which frame to which (`hinge`: a door turning about its hinge, its handle in the hand;
# otherwise the thing keeps its place relative to the hand(s) from the frame it is taken; let go, it stays).
import json, os
import numpy as np
import kimodo as K

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(HERE)
plan = lambda n: json.load(open(os.path.join(ITEM, 'plans', n + '.json')))


DOOR = 'door-3'


def door():
    p = plan(DOOR); w = p['world']; d = w['door']; D = d['D']; pm = w['palm']
    walk_n = 120                                   # table-walk's frames; the door plays from its 5th
    at = lambda f: walk_n + f - p['after']['frames']
    grab = at(p['frames'][0])
    # let go where Kimodo's hand leaves the handle by itself: after the last constrained frame, the first frame its palm
    # is more than 4 cm off the handle's arc (the hand keeps pushing the door a little after that frame, then
    # comes away) — so the door follows the hand as long as the hand is on it
    m = K.read_raw(os.path.join(ITEM, 'motions', 'raw', DOOR + '.json')); o = np.array(p['after']['origin']); k = 0.896
    f = p['frames'][-1]
    while f < m['n'] - 1:
        x = (K.palm(m['p'][f], 'R') + o) * k
        if abs(np.hypot(x[0] - d['hinge'][0], x[2] - d['hinge'][1]) - pm['r']) > 0.04: break
        f += 1
    let_go = at(f - 1)
    wall_t, half = 0.12, d['width'] / 2 + 0.02
    wall = {'id': 'wall', 'kind': 'wall', 'at': [0, 0, D], 'color': '#b7ab9b', 'boxes': [
        {'c': [half + 0.9, 1.3, 0], 's': [1.8, 2.6, wall_t]}, {'c': [-half - 0.9, 1.3, 0], 's': [1.8, 2.6, wall_t]},
        {'c': [0, (d['height'] + 0.02 + 2.6) / 2, 0], 's': [2 * half, 2.6 - d['height'] - 0.02, wall_t]}]}
    leaf = {'id': 'door', 'kind': 'leaf', 'at': [d['hinge'][0], 0, D], 'width': d['width'], 'height': d['height'],
            'thick': d['thick'], 'handle': d['handle'], 'maxOpen': 1.75, 'color': '#7d5a3e'}
    contacts = [{'side': 'Right', 'name': 'правая ладонь на ручке', 'handle': {'prop': 'door', 'r': pm['r'], 'y': pm['y'], 'a0': pm['a0']},
                 'frames': [grab, let_go], 'ramp': 12}]
    return {'id': 'door', 'label': 'дверь',
            'about': 'Женщина подходит к двери, берётся правой рукой за ручку, толкает дверь от себя и проходит. Подошла и '
                     'остановилась — одно движение Kimodo, дверь — второе, сделанное продолжать первое. '
                     'Kimodo дали место ладони на ручке — у закрытой двери и дальше по дуге, по которой ручка идёт, '
                     'когда дверь открывается (на 25°, 50° и 70°), — и где при этом таз; шаги, руку, проход он сделал '
                     'сам. Дверь поворачивается на петлях за ладонью, пока рука на ручке; отпущенная — ещё немного доходит сама, замедляясь.',
            'person': {'character': 'woman', 'motions': ['table-walk', DOOR], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [wall, leaf], 'contacts': contacts,
            'holds': [{'prop': 'door', 'kind': 'hinge', 'hands': ['Right'], 'from': grab, 'to': let_go, 'a0': pm['a0']}],
            'look': [0, 0.95, 2.0], 'camera': {'yaw': 0.7, 'pitch': 0.15, 'dist': 4.8},
            'views': {'front': {'yaw': -0.5, 'pitch': 0.15, 'dist': 4.2, 'target': [0.1, 0.9, D - 0.1]},
                      'side': {'yaw': 2.3, 'pitch': 0.22, 'dist': 4.2, 'target': [0.1, 0.9, D - 0.3]},
                      'whole': {'yaw': -1.1, 'pitch': 0.3, 'dist': 6.5, 'target': [0, 0.8, D - 0.4]},
                      'close': {'yaw': -2.4, 'pitch': 0.3, 'dist': 1.5, 'target': [-0.15, 1.0, D - 0.1]}}}


def cup():
    p = plan(CUP); w = p['world']; tb = w['table']; c = w['cup']
    walk_n = 120
    at = lambda f: walk_n + f - p['after']['frames']
    k0, k1, k2, k3 = [at(f) for f in p['frames']]
    contacts = [{'side': 'Right', 'name': 'правая ладонь у чашки', 'at': w['palm'], 'frames': [k0, k1], 'ramp': 12},
                {'side': 'Right', 'name': 'правая ладонь ставит чашку', 'at': w['palm'], 'frames': [k2, k3], 'ramp': 12}]
    if w.get('drink'):        # the hand where the cup's rim is at the lips (the plan's drink frames)
        d0, d1 = [at(f) for f in p['drink_frames']]
        contacts.insert(1, {'side': 'Right', 'name': 'правая ладонь: край чашки у губ', 'lips': {'prop': 'cup'}, 'frames': [d0, d1], 'ramp': 15})
    return {'id': 'cup', 'label': 'чашка',
            'about': 'Женщина подходит к столу, берёт правой рукой чашку, пьёт из неё и ставит обратно. Kimodo дали '
                     'место ладони у чашки — когда берёт и когда ставит — и где стоит таз; подъём к губам и всё '
                     'остальное он сделал сам. Чашка держится за ладонью, пока она в руке. Подошла — одно движение, '
                     'чашка — второе, сделанное продолжать первое.',
            'person': {'character': 'woman', 'motions': ['table-walk', CUP], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [{'id': 'table', 'kind': 'table', 'at': [0, 0, tb['edge'] + tb['depth'] / 2], 'heading': 0, 'size': [tb['width'], tb['depth']], 'height': tb['top']},
                      {'id': 'cup', 'kind': 'cup', 'at': c['at'], 'r': c['r'], 'h': c['h'], 'standsOn': tb['top'], 'color': '#e8e2d6',
                       'handleAt': [0, c['h'] * 0.55, c['r'] + 0.012], 'handleTurn': 1.5708}],
            'contacts': contacts,
            'holds': [{'prop': 'cup', 'hands': ['Right'], 'from': k1, 'to': k2 + (k3 - k2) // 2}],
            'look': [0, 0.95, 1.8], 'camera': {'yaw': 0.9, 'pitch': 0.15, 'dist': 3.6},
            'views': {'front': {'yaw': 0.4, 'pitch': 0.12, 'dist': 3.0, 'target': [0, 1.0, 2.0]},
                      'side': {'yaw': -1.1, 'pitch': 0.15, 'dist': 3.0, 'target': [0, 0.95, 1.9]},
                      'whole': {'yaw': 0.9, 'pitch': 0.25, 'dist': 5.5, 'target': [0, 0.8, 1.4]},
                      'close': {'yaw': -0.9, 'pitch': 0.4, 'dist': 1.0, 'target': [-0.2, 0.82, 2.3]},
                      'mouth': {'yaw': 0.4, 'pitch': 0.05, 'dist': 1.0, 'target': [-0.03, 1.35, 1.98]}}}


CUP = 'cup-3'
BOX = 'box-2'

def box():
    p = plan(BOX); w = p['world']; b = w['box']; tb = w['table']
    f = p['frames']                                       # taken at f0–f1, put at f2–f3
    take, let_go = (f[0] + f[1]) // 2, (f[2] + f[3]) // 2
    contacts = [{'side': s, 'name': n, 'grip': {'prop': 'box', 'half': b['half'], 'y': b['grip_y'], 'f0': f[0], 'f1': f[1], 'f2': f[2], 'ramp': 15, 'put': b['put']},
                 'frames': [f[0], f[3]], 'ramp': 12} for s, n in (('Left', 'левая ладонь на коробке'), ('Right', 'правая ладонь на коробке'))]
    return {'id': 'box', 'label': 'коробка',
            'about': 'Мужчина берёт с пола коробку обеими руками, несёт три метра и ставит на стол. Kimodo дали места '
                     'ладоней на боках коробки — где она лежит и куда её ставят — и где при этом таз; присед, подъём, '
                     'ходьбу с коробкой он сделал сам. Пока коробка в руках, она держится между ладонями, а ладони '
                     'держатся на её боках (ширина коробки — между ними).',
            'person': {'character': 'man', 'motions': [BOX], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [{'id': 'table', 'kind': 'table', 'at': [0, 0, tb['edge'] + tb['depth'] / 2], 'heading': 0, 'size': [tb['width'], tb['depth']], 'height': tb['top']},
                      {'id': 'box', 'kind': 'box', 'at': b['at'], 'size': b['size'], 'standsOn': 0.0, 'putOn': tb['top'], 'color': '#b88d5a'}],
            'contacts': contacts,
            'holds': [{'prop': 'box', 'hands': ['Left', 'Right'], 'from': take, 'to': let_go}],
            'look': [0, 0.8, 1.6], 'camera': {'yaw': 1.0, 'pitch': 0.15, 'dist': 5.0},
            'views': {'front': {'yaw': -0.9, 'pitch': 0.18, 'dist': 5.5, 'target': [0, 0.7, 1.7]},
                      'side': {'yaw': 2.2, 'pitch': 0.18, 'dist': 5.5, 'target': [0, 0.7, 1.7]},
                      'whole': {'yaw': 1.6, 'pitch': 0.25, 'dist': 6.5, 'target': [0, 0.7, 1.8]},
                      'close': {'yaw': 0.9, 'pitch': 0.3, 'dist': 1.8, 'target': [0, 0.4, 0.5]},
                      'put': {'yaw': 2.3, 'pitch': 0.35, 'dist': 1.8, 'target': [0, 0.9, 3.4]}}}


if __name__ == '__main__':
    import sys
    scenes = []
    for f in (door, cup, box):
        try: scenes.append(f())
        except (FileNotFoundError, KeyError) as e: print('skip', f.__name__, e)
    json.dump({'scenes': scenes}, open(os.path.join(ITEM, 'scenes.json'), 'w'), ensure_ascii=False, indent=1)
    print([s['id'] for s in scenes])
