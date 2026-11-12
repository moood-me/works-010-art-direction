# The page's scenes (scenes.json) from the plans (plans/*.json): the things where the plans put them, the people, their
# motions (a chain where one was made to go on from another), the places the palms were asked to come to and over
# which frames of the clip the small correction is weighed in. Russian text is what a person reads on the page.
#   python3 tools/scenes.py
import json, os

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(HERE)
plan = lambda n: json.load(open(os.path.join(ITEM, 'plans', n + '.json')))
NAME = {'Left': 'левая ладонь', 'Right': 'правая ладонь'}
SIDE = {'L': 'Left', 'R': 'Right'}


# The correction is weighed in over the 15 frames after Kimodo's own palms come within 7 cm of their places (read off
# the page's numbers without the correction: table frame 177, armchair 109, shoulder below): it only finishes what
# Kimodo did, and never pulls a hand that is still on its way.


# for the second tries: the frame after Kimodo's own palm comes within 7 cm, plus 15 (filled in from their numbers)
FROM = {'shoulder2': 125, 'armchair2': 138}


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
                 'frames': [192, 1e9], 'ramp': 15} for s in 'LR']
    return {'id': 'table', 'label': 'стол',
            'about': 'Женщина подходит к столу и опирается на него руками. Kimodo дали место ладоней на столешнице '
                     'за секунду до конца и в последний кадр — и где при этом стоит таз; шаги, наклон, локти он '
                     'сделал сам. Подошла и остановилась — одно движение, наклон — второе, сделанное продолжать первое.',
            'person': {'character': 'woman', 'motions': ['table-walk', 'table-lean'], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [{'kind': 'table', 'at': [0, 0, tb['edge'] + tb['depth'] / 2], 'heading': 0, 'size': [tb['width'], tb['depth']], 'height': tb['top']}],
            'contacts': contacts, 'look': [0, 0.85, 1.6], 'camera': {'yaw': 0.9, 'pitch': 0.15, 'dist': 4.6},
            'views': {**views([0, 0.85, 1.4], 4.4, 0.0), 'close': {'yaw': 0.75, 'pitch': 0.5, 'dist': 1.3, 'target': [0, 0.78, tb['edge'] + 0.1]}}}


def armchair():
    p = plan('armchair'); w = p['world']; a = w['armchair']
    over = lambda sx: [[min(sx * (a['width'] / 2 - a['armWidth']), sx * a['width'] / 2), a['at'][2] - a['depth'] / 2],
                       [max(sx * (a['width'] / 2 - a['armWidth']), sx * a['width'] / 2), a['at'][2] + a['depth'] / 2]]
    contacts = [{'side': SIDE[s], 'name': NAME[SIDE[s]], 'at': w['palms'][s], 'surface': a['arm'],
                 'over': over(-1 if s == 'L' else 1),
                 'frames': [124, 1e9], 'ramp': 15} for s in 'LR']
    return {'id': 'armchair', 'label': 'кресло, первая попытка',
            'about': 'Женщина подходит к креслу, поворачивается, садится и кладёт руки на подлокотники (высота '
                     'подлокотников 62 см, сиденья 42 см). Kimodo дали место ладоней на подлокотниках и где сидит таз — '
                     'с 4,5 секунды и до конца; подход, поворот и посадку он сделал сам.',
            'person': {'character': 'woman', 'motions': ['armchair'], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [{'kind': 'armchair', **a}],
            'contacts': contacts, 'look': [0, 0.7, 1.6], 'camera': {'yaw': 0.9, 'pitch': 0.15, 'dist': 4.6},
            'views': {**views([0, 0.75, 1.4], 4.4, 0.0), 'whole': {'yaw': 2.3, 'pitch': 0.25, 'dist': 6.0, 'target': [0, 0.6, 1.4]},
                      'front': {'yaw': 3.1416, 'pitch': 0.12, 'dist': 5.2, 'target': [0, 0.75, 1.6]}, 'close': {'yaw': 2.4, 'pitch': 0.45, 'dist': 1.5, 'target': [0, 0.62, a['at'][2] - 0.1]}}}


def shoulder():
    p = plan('shoulder'); o = p['world']['other']
    contacts = [{'side': 'Right', 'name': 'правая ладонь', 'on': {'vertex': o['vertex']},
                 'frames': [120, 1e9], 'ramp': 12}]       # Kimodo's palm within 7 cm from frame 108
    return {'id': 'shoulder', 'label': 'плечо, первая попытка',
            'about': 'Мужчина подходит к женщине и кладёт правую руку ей на левое плечо. Она стоит в своём движении '
                     'Kimodo; точку на её плече (на коже) в каждом кадре дали Kimodo как место его ладони — за две '
                     'секунды до конца и в последний кадр; подход, остановку и руку он сделал сам.',
            'person': {'character': 'man', 'motions': ['shoulder'], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'other': {'character': o['who'], 'motions': [o['motion']], 'place': o['place'], 'color': '#c9a58a'},
            'props': [], 'contacts': contacts, 'look': [0, 1.0, 1.2], 'camera': {'yaw': 1.2, 'pitch': 0.12, 'dist': 4.2},
            'views': {'front': {'yaw': -0.75, 'pitch': 0.1, 'dist': 3.6, 'target': [0, 0.95, 1.3]},
                      'side': {'yaw': -1.5708, 'pitch': 0.06, 'dist': 5.0, 'target': [0, 0.95, 1.1]},
                      'whole': {'yaw': -0.9, 'pitch': 0.25, 'dist': 5.5, 'target': [0, 0.8, 1.0]},
                      'close': {'yaw': -1.2, 'pitch': 0.3, 'dist': 1.4, 'target': [-0.06, 1.3, 1.7]}}}

def shoulder2():
    p = plan('shoulder2'); o = p['world']['other']
    contacts = [{'side': 'Right', 'name': 'правая ладонь', 'on': {'vertex': o['vertex']},
                 'frames': [FROM.get('shoulder2', 120), 1e9], 'ramp': 12}]
    return {'id': 'shoulder2', 'label': 'рука на плечо',
            'about': 'Вторая попытка руки на плече: мужчина встаёт рядом с ней, сбоку от её левого плеча, а не перед '
                     'лицом, в полуметре, и кладёт ладонь на верх плеча, подальше от шеи; локоть согнут. Kimodo дали '
                     'точку на её плече, где он стоит и куда повёрнут; посмотреть на неё попросили словами.',
            'person': {'character': 'man', 'motions': ['shoulder2'], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'other': {'character': o['who'], 'motions': [o['motion']], 'place': o['place'], 'color': '#c9a58a'},
            'props': [], 'contacts': contacts, 'look': [0, 1.0, 1.2], 'camera': {'yaw': 1.2, 'pitch': 0.12, 'dist': 4.2},
            # across the line between them, on the side of her touched shoulder: him in profile, her from behind-left
            'views': {'front': {'yaw': -0.88, 'pitch': 0.08, 'dist': 3.6, 'target': [-0.2, 0.95, 1.7]},
                      'side': {'yaw': -1.5708, 'pitch': 0.06, 'dist': 5.0, 'target': [0, 0.95, 1.1]},
                      'whole': {'yaw': -0.5, 'pitch': 0.22, 'dist': 5.5, 'target': [0, 0.8, 1.1]},
                      'close': {'yaw': -0.88, 'pitch': 0.2, 'dist': 1.3, 'target': [-0.2, 1.35, 1.8]}}}


def armchair2():
    s = armchair()
    s.update(id='armchair2', label='кресло',
             about='Вторая попытка кресла: то же, но в позе, которую дали Kimodo, бёдра повёрнуты внутрь, колени '
                   'в 20 см друг от друга (как ширина таза), и Kimodo держит ещё и ступни там, где они в этой позе. '
                   'В первой попытке она сидела, широко расставив колени.',
             person={**s['person'], 'motions': ['armchair2']})
    for c in s['contacts']: c['frames'] = [FROM.get('armchair2', 124), 1e9]
    return s

if __name__ == '__main__':
    scenes = []
    for f in (table, shoulder2, shoulder, armchair2, armchair):
        try: scenes.append(f())
        except FileNotFoundError as e: print('skip', f.__name__, e)
    json.dump({'scenes': scenes}, open(os.path.join(ITEM, 'scenes.json'), 'w'), ensure_ascii=False, indent=1)
    print([s['id'] for s in scenes])
