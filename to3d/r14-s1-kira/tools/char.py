"""The character this folder makes: Кира of style С1 (styles/s1-pixar/tools/kira.py: kira, kira_hair, kira_person).
Everything that differs from the other characters of the style (Р6 Тим, Р13 Вера) is named here or in build.py."""
NAME = 'kira'
CACHE = '/home/user/cache/to3d-r14-s1-kira'
BODY = 'moood-girl'           # the engine body the figure starts from
BODY_LABEL = 'Anny, девушка 1,51 м'
FLOOR = 564.0                 # the floor in the drawing's person units (y down)
HS = 1.0                      # the drawn head's scale (person units per head unit)
EYE_R = 10.8                  # the eyeball (head units)
EYE_FRONT = 1.2               # how far the ball's front stands before the drawn face surface at the eye
NOSE_S = 0.76                 # the base's nose scaled about its root
NOSE_OUT = 0.6                # … and moved forward
EAR_S = 0.66


def person():
    import kira
    return kira.kira_person()


# the comparisons (compare.py): the stills stand in the drawing's own stance (web/char.js stancePose); the portrait's
# turn (the style's yaw 0.34 is the camera's −0.34 here) and face; the head a little down, as the style's sheets hold it
STAND = {'stance': True}
DRAWN_TURN = DRAWN_EXPR = False         # the style drew both
PORTRAIT_YAW = -0.34
PORTRAIT_EXPR = 'look'
PORTRAIT_SET = {'stance': {'head': [0.13, 0.07]}, 'still': True}
# the figure sheet's pose (styles/s1-pixar/tools/build.py FIGURE['kira']): the right foot out to the side; her hand in
# the pocket and the sheet's sideways line of action are not taken
FIGURE_SET = {'stance': {'kn': {'-1': [-24, 432, 14]}, 'an': {'-1': [-38, 544, 6], '1': [4, 544, -2]}, 'head': [0.13, 0.08]}, 'still': True}


# the films (films.py)
def FILMS(follow, motion_film):
    return {
        'walk': lambda: motion_film('walk', 120, follow(-0.6, 0.08, 5.2, 0.86, 20), [{'t': 0, 'name': 'calm'}, {'t': 2.4, 'name': 'look'}]),
        # she sneaks: Kimodo's «крадётся»
        'sneak': lambda: motion_film('sneak', 120, follow(-0.7, 0.08, 5.0, 0.8, 20), [{'t': 0, 'name': 'look'}, {'t': 2.5, 'name': 'surprise'}]),
        # she stands and mutters: Kimodo's «стоит» stoops, which is hers
        'idle': lambda: motion_film('idle', 120, follow(-0.3, 0.05, 4.4, 0.9, 20), [{'t': 0, 'name': 'calm'}, {'t': 2.2, 'name': 'smirk'}], [[0.8, 2.2]]),
    }


FACE_EXPR = [{'t': 0, 'name': 'calm'}, {'t': 3.2, 'name': 'look'}, {'t': 4.7, 'name': 'smirk'}, {'t': 6.1, 'name': 'surprise'},
             {'t': 7.4, 'name': 'sad'}, {'t': 8.8, 'name': 'anger'}, {'t': 10.2, 'name': 'calm'}]
FACE_TALK = [[1.0, 3.0]]
FACE_FRAMES = 340

SHEET = ['smirk', 'surprise', 'sad', 'anger']      # the style's sheet of her: joy (a crooked smirk), surprise, sadness, anger
