# The page's scenes (scenes.json) from the plans (plans/*.json): the things where the plans put them (as boxes in each
# thing's frame), the person and their motions (a chain where one was made to go on from another), the hands' places
# and when the small correction is weighed in, and the "touches" — a part of the body resting on a thing, measured.
# Russian text is what a person reads on the page.   python3 tools/scenes.py
# (A copy of К1's tools/scenes.py, its scenes replaced.)
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(HERE)
plan = lambda n: json.load(open(os.path.join(ITEM, 'plans', n + '.json')))
SCENES = json.load(open(os.path.join(HERE, 'scene_list.json')))        # which scene plays which motions
# from which frame of the clip a hand is weighed onto its place: when Kimodo's own palm has come within 7 cm of it
# (read off the page's numbers without the correction)
HAND_ON = {'stairs': [25, 160]}


def views(target, dist, front_yaw):
    """front and side follow the person over the floor; `whole` stands still and sees the whole way"""
    t = list(target)
    return {'front': {'yaw': front_yaw, 'pitch': 0.12, 'dist': dist, 'target': t, 'follow': True},
            'side': {'yaw': front_yaw + 1.5708, 'pitch': 0.08, 'dist': dist, 'target': t, 'follow': True},
            'whole': {'yaw': front_yaw + 0.9, 'pitch': 0.3, 'dist': 6.5, 'target': [t[0], 0.6, t[2]]}}


def wall():
    p = plan('wall'); face = p['world']['wall']['face']; th = 0.2
    return {'id': 'wall', 'label': 'спиной к стене',
            'about': 'Женщина подходит к стене, поворачивается и прислоняется к ней спиной; стоит, потом отталкивается и уходит. '
                     'Kimodo дали всю позу целиком — его собственную позу «прислонился спиной», поставленную так, что '
                     'спина касается нашей стены, — в трёх кадрах; подход, поворот и наклон назад он сделал сам. Уход — '
                     'второе движение, сделанное продолжать первое.',
            'person': {'character': 'woman', 'motions': SCENES['wall'], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [{'kind': 'wall', 'at': [0, 0, face + th / 2], 'heading': 0,
                       'boxes': [{'c': [0, 1.2, 0], 's': [3.0, 2.4, th], 'part': 'wall', 'mat': 'wall'}]}],
            'contacts': [],
            'touches': [{'name': 'спина до стены', 'parts': ['spine', 'pelvis', 'Lclavicle', 'Rclavicle'], 'prop': 0, 'boxes': ['wall'], 'held': [95, 209]}],
            'look': [0, 0.9, 1.6], 'camera': {'yaw': 2.2, 'pitch': 0.15, 'dist': 5.2},
            'views': {'front': {'yaw': 2.6, 'pitch': 0.12, 'dist': 4.2, 'target': [0, 0.9, 1.6], 'follow': True},
                      'side': {'yaw': 1.5708, 'pitch': 0.08, 'dist': 4.6, 'target': [0, 0.9, 1.6], 'follow': False},
                      'whole': {'yaw': 2.2, 'pitch': 0.3, 'dist': 6.5, 'target': [0, 0.8, 1.4]},
                      'close': {'yaw': 1.5708, 'pitch': 0.1, 'dist': 1.8, 'target': [0, 1.1, face - 0.2]}}}


def stairs():
    p = plan('stairs'); g = p['world']; w = g['measures']['width']; r = g['rail']
    boxes = []
    for st in g['steps']:      # solid steps, each from the floor to its top
        boxes.append({'c': [0, st['top'] / 2, (st['z'][0] + st['z'][1]) / 2], 's': [w, st['top'], st['z'][1] - st['z'][0]], 'part': 'step', 'mat': 'stone'})
    a, b = r['a'], r['b']; L = math.dist(a, b); slope = math.atan2(b[1] - a[1], b[2] - a[2])
    boxes.append({'c': [(a[k] + b[k]) / 2 for k in range(3)], 's': [2 * r['r'], 2 * r['r'], L], 'rx': -slope, 'part': 'rail', 'mat': 'wood', 'round': True})
    for st in g['steps'][:-1:3] + [g['steps'][-2]]:   # posts under the rail
        z = (st['z'][0] + st['z'][1]) / 2; top = a[1] + (z - a[2]) * math.tan(slope)
        boxes.append({'c': [r['a'][0], (st['top'] + top) / 2, z], 's': [0.03, top - st['top'], 0.03], 'part': 'post', 'mat': 'metal'})
    contacts = [{'side': 'Right', 'name': 'правая ладонь на перилах', 'rail': {**r, 'palm': 0.022}, 'frames': HAND_ON['stairs'], 'ramp': 10}]
    return {'id': 'stairs', 'label': 'лестница с перилами',
            'about': 'Женщина поднимается на десять ступеней (14 см высотой, 22 см глубиной), правая рука скользит по '
                     'перилам. Kimodo дали места ступней на наших ступенях — в середине каждого шага, — и пять раз за '
                     'подъём место правой ладони на перилах; шаги, наклон и руку между ними он сделал сам.',
            'person': {'character': 'woman', 'motions': SCENES['stairs'], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [{'kind': 'stairs', 'at': [0, 0, 0], 'heading': 0, 'boxes': boxes}],
            'contacts': contacts,
            'feet': [{'side': 'Left', 'name': 'левая ступня', 'prop': 0, 'boxes': ['step']},
                     {'side': 'Right', 'name': 'правая ступня', 'prop': 0, 'boxes': ['step']}],
            'look': [0, 1.2, 1.4], 'camera': {'yaw': -1.2, 'pitch': 0.15, 'dist': 5.0},
            'views': {'front': {'yaw': -0.45, 'pitch': 0.12, 'dist': 6.0, 'target': [0, 1.5, 1.4], 'follow': False},
                      'side': {'yaw': -1.5708, 'pitch': 0.1, 'dist': 6.2, 'target': [0, 1.5, 1.5], 'follow': False},
                      'whole': {'yaw': -0.9, 'pitch': 0.3, 'dist': 6.5, 'target': [0, 1.0, 1.4]},
                      'close': {'yaw': -1.9, 'pitch': 0.3, 'dist': 1.3, 'target': [-0.42, 1.72, 1.4]}}}


def bed(id='bed', label='кровать, первый заход', motions=None, about=None):
    p = plan('bed_sit'); b = p['world']['bed']; L, D = b['length'], b['depth']
    boxes = [{'c': [0, b['frame_h'] / 2, 0], 's': [L, b['frame_h'], D], 'part': 'frame', 'mat': 'wood'},
             {'c': [0, (b['frame_h'] + b['top']) / 2, 0], 's': [L, b['top'] - b['frame_h'], D], 'part': 'mattress', 'mat': 'sheet'},
             {'c': [L / 2 + 0.03, 0.5, 0], 's': [0.06, 1.0, D], 'part': 'head', 'mat': 'wood'}]
    if b.get('pillow'):
        pw = b['pillow']
        boxes.append({'c': [L / 2 - pw['len'] / 2, b['top'] + pw['h'] / 2, 0], 's': [pw['len'], pw['h'], D * 0.8], 'part': 'pillow', 'mat': 'sheet'})
    return {'id': id, 'label': label,
            'about': about or BED_ABOUT,
            'person': {'character': 'woman', 'motions': motions or SCENES['bed'], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [{'kind': 'bed', 'at': [b['centre_x'], 0, b['edge'] + D / 2], 'heading': 0, 'boxes': boxes}],
            'contacts': [],
            'touches': [{'name': 'ягодицы и бёдра до матраса', 'parts': ['pelvis', 'Lthigh', 'Rthigh'], 'prop': 0, 'boxes': ['mattress'], 'held': [150, 179]},
                        {'name': 'спина до матраса', 'parts': ['spine'], 'prop': 0, 'boxes': ['mattress', 'pillow'], 'held': [305, 354]},
                        {'name': 'голова до матраса', 'parts': ['head'], 'prop': 0, 'boxes': ['pillow', 'mattress'], 'held': [305, 354]}],
            'look': [0, 0.7, 1.8], 'camera': {'yaw': 2.4, 'pitch': 0.25, 'dist': 5.0},
            'views': {'front': {'yaw': 2.6, 'pitch': 0.2, 'dist': 4.0, 'target': [0, 0.7, 1.8], 'follow': True},
                      'side': {'yaw': -1.5708, 'pitch': 0.15, 'dist': 4.6, 'target': [0, 0.7, 2.0], 'follow': False},
                      'whole': {'yaw': 2.3, 'pitch': 0.35, 'dist': 6.0, 'target': [0, 0.6, 1.6]},
                      'close': {'yaw': 2.9, 'pitch': 0.35, 'dist': 2.6, 'target': [0, 0.6, b['edge'] + 0.3]}}}


BED_ABOUT = ('Женщина подходит к кровати, садится на край, ложится на спину вдоль кровати, потом садится, спускает '
             'ноги и встаёт. Три движения, каждое продолжает предыдущее. Kimodo дали: для посадки — его собственную '
             'сидячую позу, поставленную так, что ягодицы на матрасе (место таза и ступней); для лёжа — всю позу '
             '«лёг на спину» целиком, повёрнутую вдоль кровати, спиной на матрасе; для подъёма — только где встать. '
             'Разворот на кровати, закидывание ног и подъём он сделал сам.')


def desk():
    p = plan('desk'); d = p['world']; top, t = d['top'], d['thick']; W, D = 1.2, 0.7
    table = [{'c': [0, top - t / 2, 0], 's': [W, t, D], 'part': 'top', 'mat': 'wood'}]
    for sx in (-1, 1):
        for sz in (-1, 1):
            table.append({'c': [sx * (W / 2 - 0.05), (top - t) / 2, sz * (D / 2 - 0.05)], 's': [0.05, top - t, 0.05], 'part': 'leg', 'mat': 'wood'})
    s_, sw, sd, bh = d['seat'], 0.42, 0.42, 0.45
    chair = [{'c': [0, s_ - 0.025, 0], 's': [sw, 0.05, sd], 'part': 'seat', 'mat': 'wood'},
             {'c': [0, s_ + bh / 2, -sd / 2 + 0.02], 's': [sw, bh, 0.04], 'part': 'back', 'mat': 'wood'}]
    for sx in (-1, 1):
        for sz in (-1, 1):
            chair.append({'c': [sx * (sw / 2 - 0.03), (s_ - 0.05) / 2, sz * (sd / 2 - 0.03)], 's': [0.035, s_ - 0.05, 0.035], 'part': 'leg', 'mat': 'wood'})
    return {'id': 'desk', 'label': 'за столом',
            'about': 'Женщина стоит у стола, рядом стул; она шагает к стулу, садится и кладёт предплечья на столешницу '
                     '(сиденье 42 см, стол 72 см); потом встаёт. Kimodo дали место рук и таза — его собственную позу «сидит '
                     'за столом, предплечья на столе», поставленную на наш стул, — в двух кадрах; шаг, посадку и локти он '
                     'сделал сам.',
            'person': {'character': 'woman', 'motions': SCENES['desk'], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [{'kind': 'table', 'at': [d['chair_x'] + 0.1, 0, d['edge'] + D / 2], 'heading': 0, 'boxes': table},
                      {'kind': 'chair', 'at': [d['chair_x'], 0, d['chair_z'] - 0.03], 'heading': 0, 'boxes': chair}],
            'contacts': [],
            'touches': [{'name': 'предплечья до столешницы', 'parts': ['LforeArm', 'RforeArm'], 'prop': 0, 'boxes': ['top'], 'held': [120, 240]},
                        {'name': 'ягодицы до сиденья', 'parts': ['pelvis', 'Lthigh', 'Rthigh'], 'prop': 1, 'boxes': ['seat'], 'held': [120, 240]}],
            'look': [-0.3, 0.7, 0.5], 'camera': {'yaw': -2.3, 'pitch': 0.3, 'dist': 3.6},
            'views': {'front': {'yaw': 0.35, 'pitch': 0.2, 'dist': 3.0, 'target': [-0.4, 0.75, 0.5]},
                      'side': {'yaw': -1.5708, 'pitch': 0.12, 'dist': 3.4, 'target': [-0.4, 0.7, 0.5]},
                      'whole': {'yaw': -2.3, 'pitch': 0.35, 'dist': 4.2, 'target': [-0.3, 0.6, 0.5]},
                      'close': {'yaw': -2.0, 'pitch': 0.55, 'dist': 1.5, 'target': [-0.45, 0.72, 0.6]}}}


def bed2():
    s = bed('bed2', 'лечь на кровать', SCENES['bed2'], BED2_ABOUT)
    s['touches'][1]['held'] = s['touches'][2]['held'] = [305, 354]
    return s


BED2_ABOUT = ('Женщина подходит к кровати, садится на край, ложится на спину вдоль кровати, руки вдоль тела, потом '
              'садится, спускает ноги и встаёт. Три движения, каждое продолжает предыдущее. Kimodo дали: для посадки — '
              'его собственную сидячую позу на матрасе (место таза и ступней, таз попрошен выше — Kimodo садится '
              'ниже, чем просят); для лёжа — его же позу «лёг на спину, руки вдоль тела» целиком, повёрнутую вдоль '
              'кровати; для подъёма — только где встать.')


if __name__ == '__main__':
    scenes = []
    for name in SCENES:
        try: scenes.append(globals()[name]())
        except FileNotFoundError as e: print('skip', name, e)
    json.dump({'scenes': scenes}, open(os.path.join(ITEM, 'scenes.json'), 'w'), ensure_ascii=False, indent=1)
    print([s['id'] for s in scenes])
