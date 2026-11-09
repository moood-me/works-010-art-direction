"""The character this folder makes: Вера of style С1 (styles/s1-pixar/tools/cast.py: vera, vera_hair, vera_person).
Everything that differs from the other characters of the style (Р6 Тим, Р14 Кира) is named here or in build.py."""
NAME = 'vera'
CACHE = '/home/user/cache/to3d-r13-s1-vera'
BODY = 'moood-woman'          # the engine body the figure starts from
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
STAND = {'motion': ['stomp'], 't': 0}        # Kimodo's «топает», its first frame: she stands upright, arms down
DRAWN_TURN = DRAWN_EXPR = True          # drawn for the comparison by drawn.py (the style's page has none of Вера)
PORTRAIT_YAW = 0.32
PORTRAIT_EXPR = 'calm'
PORTRAIT_SET = {}
