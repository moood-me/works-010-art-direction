# The page's scenes (scenes.json) from the plans (plans/*.json): the things where the plans put them, the people, their
# motions (a chain where one was made to go on from another), the places the palms were asked to come to and over
# which frames of the clip the small correction is weighed in. Russian text is what a person reads on the page.
#   python3 tools/scenes.py
import json, os

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(os.path.dirname(HERE))
plan = lambda n: json.load(open(os.path.join(ITEM, 'plans', n + '.json')))
NAME = {'Left': 'левая ладонь', 'Right': 'правая ладонь'}
SIDE = {'L': 'Left', 'R': 'Right'}


# The correction is weighed in over the 15 frames after Kimodo's own palms come within 7 cm of their places (read off
# the page's numbers without the correction: table frame 177, armchair 109, shoulder below): it only finishes what
# Kimodo did, and never pulls a hand that is still on its way.


def views(target, dist, front_yaw):
    """front and side follow the person over the floor; `whole` stands still and sees the whole way"""
    t = list(target)
    return {'front': {'yaw': front_yaw, 'pitch': 0.12, 'dist': dist, 'target': t, 'follow': True},
            'side': {'yaw': front_yaw + 1.5708, 'pitch': 0.08, 'dist': dist, 'target': t, 'follow': True},
            'whole': {'yaw': front_yaw + 0.9, 'pitch': 0.3, 'dist': 6.5, 'target': [t[0], 0.6, t[2]]}}


WHO = {'child': 'ребёнок (1,31 м)', 'oldman': 'грузный мужчина (1,74 м)', 'elf': 'очень высокая (2,31 м, тело Т8 «эльф»)', 'woman': 'женщина (1,59 м, как в К1)'}
# the frame from which the correction is weighed in (over the 15 frames before it): К1 had 192 for the woman (its
# Kimodo palms within 7 cm from frame 177); per scene here, read off the page's numbers without the correction
FROM = {}


def table(plan_id, label, about_thing='столу', thing='стол', from_frame=192, motion=None, sid=None):
    motion = motion or plan_id
    p = plan(plan_id); w = p['world']; tb = w['table']
    walk_n = 120                                   # table-walk's frames; the lean plays from its 5th
    over = [[-tb['width'] / 2, tb['edge']], [tb['width'] / 2, tb['edge'] + tb['depth']]]
    f0 = FROM.get(plan_id, from_frame)
    contacts = [{'side': SIDE[s], 'name': NAME[SIDE[s]], 'at': w['palms'][s], 'surface': tb['top'], 'over': over,
                 'frames': [f0, 1e9], 'ramp': 15} for s in 'LR']
    who = p['who']; e = tb['edge']; top = tb['top']
    return {'id': sid or plan_id, 'label': label,
            'about': f'{WHO[who].capitalize()} подходит к {about_thing} высотой {str(top).replace(".", ",")} м и опирается на него руками — '
                     f'как в К1, тем же способом: походка К1 (то же движение Kimodo), наклон заказан заново для этого тела. '
                     f'Kimodo дали место ладоней на {"столешнице" if thing == "стол" else "стойке"} за секунду до конца и в последний кадр и где стоит таз; '
                     f'места пересчитаны под рост этого тела.',
            'person': {'character': who, 'motions': ['table-walk', motion], 'place': {'position': [0, 0, 0], 'heading': 0}},
            'props': [{'kind': 'table', 'at': [0, 0, e + tb['depth'] / 2], 'heading': 0, 'size': [tb['width'], tb['depth']], 'height': top}],
            'contacts': contacts, 'look': [0, 0.85, e - 0.6], 'camera': {'yaw': 0.9, 'pitch': 0.15, 'dist': 4.6},
            'views': {**views([0, 0.85, e - 0.8], 4.4, 0.0), 'close': {'yaw': 0.75, 'pitch': 0.5, 'dist': 1.3, 'target': [0, top + 0.04, e + 0.1]}}}


SCENES = [('lean-child', 'ребёнок, стол 0,74'), ('lean-oldman', 'грузный мужчина, стол 0,74'),
          ('bar-oldman', 'грузный мужчина, стойка 1,1'), ('lean-elf', 'очень высокая, стол 0,74')]

if __name__ == '__main__':
    scenes = []
    for pid, label in SCENES:
        try: scenes.append(table(pid, label, *(('барной стойке', 'стойка') if pid.startswith('bar') else ())))
        except FileNotFoundError as e: print('skip', pid, e)
    # the same ask with other seeds: how much the result depends on luck
    for seed in (1, 2):
        sc = table('lean-child', f'ребёнок, стол 0,74 — seed {seed}', motion=f'lean-child-s{seed}', sid=f'lean-child-s{seed}')
        sc['about'] = f'То же, что «ребёнок, стол 0,74», тот же заказ, другой seed ({seed}): насколько результат зависит от случая.'
        scenes.append(sc)
    json.dump({'scenes': scenes}, open(os.path.join(ITEM, 'table-scenes.json'), 'w'), ensure_ascii=False, indent=1)
    print([s['id'] for s in scenes])
