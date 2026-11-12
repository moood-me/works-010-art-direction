"""The character this folder makes: Вера of style С1 (styles/s1-pixar/tools/cast.py: vera, vera_hair, vera_person).
Everything that differs from the other characters of the style (Р6 Тим, Р14 Кира) is named here or in build.py."""
NAME = 'vera'
CACHE = '/home/user/cache/to3d-r13-s1-vera'
BODY = 'moood-woman'          # the engine body the figure starts from
BODY_LABEL = 'Anny, женщина 1,59 м'
FLOOR = 590.0                 # the floor in the drawing's person units (y down)
HS = 1.12                     # the drawn head's scale (person units per head unit)
EYE_R = 11.5                  # the eyeball (head units)
EYE_FRONT = 1.2               # how far the ball's front stands before the drawn face surface at the eye
NOSE_S = 0.88                 # the base's nose scaled about its root
NOSE_OUT = 1.6                # … and moved forward
EAR_S = 0.66


def person():
    import cast
    return cast.vera_person()

# the comparisons (compare.py): the pose the stills stand in, the portrait's turn (the style's yaw −0.32 is the
# camera's 0.32 here: the style turns the figure, the page turns the camera) and face
STAND = {'stance': True}                # the drawing's own stance (web/char.js stancePose): no Kimodo motion in the stills
DRAWN_TURN = DRAWN_EXPR = True          # drawn for the comparison by drawn.py (the style's page has none of Вера)
PORTRAIT_YAW = 0.32
PORTRAIT_EXPR = 'calm'
PORTRAIT_SET = {'look': [-4, 0]}
# the figure sheet's pose (styles/s1-pixar/tools/build.py FIGURE['vera']): her left forearm before her, the right foot a step out
# (the arm's joints moved out of the coat, as in build.py STANCE)
FIGURE_SET = {'stance': {'el': {'1': [60, 194, -4]}, 'wr': {'1': [50, 276, 22]}, 'kn': {'-1': [-8, 450, 10]}, 'an': {'-1': [-6, 574, 14]}, 'curl': 0.45}, 'look': [-4, 0]}


# the films (films.py)
def FILMS(follow, motion_film):
    return {
        # she walks and speaks, strict, then softens
        'walk': lambda: motion_film('walk', 120, follow(-0.6, 0.08, 5.6, 0.92, 20), [{'t': 0, 'name': 'strict'}, {'t': 2.6, 'name': 'smile'}], [[0.6, 2.4]]),
        # a bow: Kimodo's «кланяется»
        'bow': lambda: motion_film('bow', 100, follow(-0.5, 0.06, 5.6, 0.92, 20), [{'t': 0, 'name': 'calm'}, {'t': 2.2, 'name': 'smile'}]),
    }


FACE_EXPR = [{'t': 0, 'name': 'calm'}, {'t': 3.4, 'name': 'strict'}, {'t': 4.9, 'name': 'smile'}, {'t': 6.2, 'name': 'joy'}, {'t': 7.4, 'name': 'surprise'},
             {'t': 8.6, 'name': 'sad'}, {'t': 9.8, 'name': 'anger'}, {'t': 11.0, 'name': 'calm'}]
FACE_TALK = [[1.0, 3.2]]
FACE_FRAMES = 360
