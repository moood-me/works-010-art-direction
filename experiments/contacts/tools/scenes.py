# The page's scenes (scenes.json) from the plans (plans/*.json): the things where the plans put them, the people, their
# motions (a chain where one was made to go on from another), the places the palms were asked to come to and over
# which frames of the clip the small correction is weighed in. Russian text is what a person reads on the page.
#   python3 tools/scenes.py
import json, os

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(HERE)
plan = lambda n: json.load(open(os.path.join(ITEM, 'plans', n + '.json')))
NAME = {'Left': 'левая ладонь', 'Right': 'правая ладонь'}
SIDE = {'L': 'Left', 'R': 'Right'}


def views(target, dist, front_yaw):
    """front and side follow the person over the floor; `whole` stands still and sees the whole way"""
    t = list(target)
    return {'front': {'yaw': front_yaw, 'pitch': 0.12, 'dist': dist, 'target': t, 'follow': True},
            'side': {'yaw': front_yaw + 1.5708, 'pitch': 0.08, 'dist': dist, 'target': t, 'follow': True},
            'whole': {'yaw': front_yaw + 0.9, 'pitch': 0.3, 'dist': 6.5, 'target': [t[0], 0.6, t[2]]}}


def table():
    p = plan('table_lean'); w = p['world']; tb = w['table']
    walk_n = 120                                   # table-walk's frames; the lean plays from its 5th
    at = lambda f: walk_n + f - p['after']['frames']
    over = [[-tb['width'] / 2, tb['edge']], [tb['width'] / 2, tb['edge'] + tb['depth']]]
    contacts = [{'side': SIDE[s], 'name': NAME[SIDE[s]], 'at': w['palms'][s], 'surface': tb['top'], 'over': over,
                 'frames': [at(p['frames'][0]) - 25, 1e9], 'ramp': 20} for s in 'LR']
    return {'id': 'table', 'label': 'стол',
            'about': 'Женщина подходит к столу и опирается на него руками. Kimodo дали место ладоней на столешнице '
                     'за секунду до конца и в последний кадр — и где при этом стоит таз; шаги, наклон, локти он '
                     'сделал сам. Подошла и остановилась — одно движение, наклон — второе, сделанное продолжать первое.',
            'person': {'character': 'woman', 'motions': ['table-walk', 'table-lean'], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [{'kind': 'table', 'at': [0, 0, tb['edge'] + tb['depth'] / 2], 'heading': 0, 'size': [tb['width'], tb['depth']], 'height': tb['top']}],
            'contacts': contacts, 'look': [0, 0.85, 1.6], 'camera': {'yaw': 0.9, 'pitch': 0.15, 'dist': 4.6},
            'views': {**views([0, 0.85, 1.4], 3.4, 0.0), 'close': {'yaw': 0.75, 'pitch': 0.5, 'dist': 1.3, 'target': [0, 0.78, tb['edge'] + 0.1]}}}


def armchair():
    p = plan('armchair'); w = p['world']; a = w['armchair']
    over = lambda sx: [[min(sx * (a['width'] / 2 - a['armWidth']), sx * a['width'] / 2), a['at'][2] - a['depth'] / 2],
                       [max(sx * (a['width'] / 2 - a['armWidth']), sx * a['width'] / 2), a['at'][2] + a['depth'] / 2]]
    contacts = [{'side': SIDE[s], 'name': NAME[SIDE[s]], 'at': w['palms'][s], 'surface': a['arm'],
                 'over': over(-1 if s == 'L' else 1),
                 'frames': [p['frames'][0] - 20, 1e9], 'ramp': 20} for s in 'LR']
    return {'id': 'armchair', 'label': 'кресло',
            'about': 'Женщина подходит к креслу, поворачивается, садится и кладёт руки на подлокотники (высота '
                     'подлокотников 62 см, сиденья 42 см). Kimodo дали место ладоней на подлокотниках и где сидит таз — '
                     'с 4,5 секунды и до конца; подход, поворот и посадку он сделал сам.',
            'person': {'character': 'woman', 'motions': ['armchair'], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [{'kind': 'armchair', **a}],
            'contacts': contacts, 'look': [0, 0.7, 1.6], 'camera': {'yaw': 0.9, 'pitch': 0.15, 'dist': 4.6},
            'views': {**views([0, 0.75, 1.4], 3.4, 0.0), 'close': {'yaw': 2.4, 'pitch': 0.45, 'dist': 1.5, 'target': [0, 0.62, a['at'][2] - 0.1]}}}


if __name__ == '__main__':
    scenes = []
    for f in (table, armchair):
        try: scenes.append(f())
        except FileNotFoundError as e: print('skip', f.__name__, e)
    json.dump({'scenes': scenes}, open(os.path.join(ITEM, 'scenes.json'), 'w'), ensure_ascii=False, indent=1)
    print([s['id'] for s in scenes])
