"""Кира (С6): what build.py and make.py need to know about this character of the style.
Sides: the drawing's 'L' is the person's right (SOMA Right), 'R' the person's left."""
ID, LABEL, FOLDER = 'kira', 'Кира', 'r24-s6-kira'
MODULE, FUNC, BODY = 'cast_more', 'kira', 'KIRA_B'   # styles/s6-symbolic/tools/cast_more.py: kira(), KIRA_B
OPTS = {}

# the solids in the order cast_more.kira() makes them, and what each is
TUBES = ['leg:L', 'shin:L', 'foot:L', 'leg:R', 'shin:R', 'foot:R',   # thin legs; a boot's shaft on the shin; the boot
         'on:Chest:hood',                                           # the hood hanging on the back
         'neck',
         'arm:L', 'hand:L', 'arm:R', 'hand:R',                      # wide sleeves that swallow the hands
         'pocket',                                                  # the hands in the hoodie's pocket
         'on:Head:hair', 'on:Head:hair', 'on:Head:hair', 'on:Head:hair',   # sharp ends at the nape and the sides
         'on:Head:hair', 'on:Head:hair', 'on:Head:hair']            # the long fringe over one eye
LOFTS = [('torso', [-.2, .1, .45, .75, .9, 1]),                     # the oversized hoodie
         ('head',),
         ('on', 'Head', 'hair')]
# her one sharp colour: the headphones — round the neck, or (when a mood puts them on) on the head
LIME = '#d2ee3c'
SIGN_SETS = [dict(part='phones', joint='Chest', col=LIME, opts={}),
             dict(part='phonesOn', joint='Head', col=LIME, opts=dict(phones='on'))]
HIDDEN = ['phonesOn']

# Moods: the posture is the expression. The first is the drawn stand; the next four are the style's own expression
# sheet for her (scenes_more.EXPR_KIRA — pose numbers, the yaw each is drawn at, what it does to the hands' pocket and
# the headphones). arms = (person's left, person's right): how much the mood holds each arm when it lies on a motion.
OUT = ['pocket']
MOODS = {
    'slouch': dict(label='руки в карманах', pose={}, arms=(1, 1), yaw=55),
    # her joy is hers alone: the headphones on, the head back, a sway to the music
    'joy': dict(label='радость', pose=dict(lean=-8, hunch=2, neck=0, nod=-26, headRoll=-10, roll=7, slump=0, shrug=1,
                                           armL=(10, 100, 0, 135), armR=(-12, 34, 46, 24),
                                           legL=(4, 4, 2, 0), legR=(26, 10, 56, 0), footL=(0, 8), footR=(30, 4)),
                opts=dict(pocket=False, phones='on'), yaw=-30, arms=(1, 1), hide=OUT + ['phones'], show=['phonesOn']),
    'surprise': dict(label='удивление', pose=dict(lean=-14, hunch=4, neck=-8, nod=-8, shrug=4, slump=0, armL=(30, 24, 115, 0), armR=(36, 22, 120, 0),
                                                  legL=(-16, 4, 6, 0), legR=(12, 4, 2, 0), footL=(0, 6), footR=(0, 6)),
                     opts=dict(pocket=False), yaw=58, arms=(1, 1), hide=OUT),
    'sad': dict(label='грусть', pose=dict(lean=18, hunch=34, neck=10, nod=14, slump=5, shrug=2, armL=(80, 8, -110, -10), armR=(80, 8, -110, -10),
                                          legL=(104, 3, 150, 0), legR=(100, 3, 146, 0), footL=(0, 2), footR=(0, 2)),
                opts=dict(pocket=False), yaw=65, arms=(1, 1), hide=OUT),
    'angry': dict(label='злость', pose=dict(lean=-5, hunch=18, neck=22, nod=6, shrug=4, slump=2, armL=(-22, 24, 4, -8), armR=(-18, 26, 4, -8),
                                            legL=(48, 4, 12, 0), legR=(-6, 4, 8, 0), footL=(-16, 4), footR=(0, 10)),
                  opts=dict(pocket=False), yaw=62, arms=(1, 1), hide=OUT),
    # on a motion: her slouch (the back round, the head down and forward) — with the hands in the pocket …
    'plain': dict(label='сутулится, руки в карманах', pose={}, arms=(1, 1), menu=False),
    # … with the arms the motion's own …
    'loose': dict(label='сутулится', pose={}, arms=(0, 0), hide=OUT, menu=False),
    # … and with the headphones on, the back a little straighter, the head up to the music
    'music': dict(label='в наушниках', pose=dict(lean=-2, hunch=10, neck=4, nod=-14, slump=1, shrug=.5), arms=(0, 0),
                  hide=OUT + ['phones'], show=['phonesOn'], menu=False),
}
MOOD_SHEET = ['slouch', 'joy', 'surprise', 'sad', 'angry']

# the drawing's sheets this figure is compared with
TURN = dict(k=3.2, light=1, pic='turn-kira.jpg')
FULL = dict(yaw=55, k=3.55, x=.52, light=-1, foot=20, pic='full-kira.jpg')
# the style's expression sheet (scenes_more.expr_sheet('kira', EXPR_KIRA, SNOW, 3.0, xs=[0, 0, 0, -30], foot=20))
EXPR = dict(order=['joy', 'surprise', 'sad', 'angry'], labels=['радость', 'удивление', 'грусть', 'злость'], k=3.0, xs=[0, 0, 0, -30], foot=20,
            pal=dict(top='#1b2233', hor='#6d7894', fog='#9aa4bd', ground='#c3cad8', rim='#e7ecf6'), pic='expr-kira.jpg')

# ------------------------------------------------------------------ pictures and films (make.py)
WORLD_LABEL = 'дальний город, туман, тень, зерно'
MOOD_K = 3.0
# standing in her world: her back to the town's light, where we look from
HERO = dict(heading=.95, lamp=[-26, 0, -30], mood='slouch',
            cam=dict(yaw=0.05, pitch=-0.03, dist=4.6, h=.9, fov=33))
WALK = dict(motion='walk', mood='plain', heading=1.5708, position=[-3.0, 0, 0], lamp=[-26, 0, -30],
            cam=dict(yaw=0.18, pitch=0.0, dist=3.9, h=.85, fov=34, smooth=2.5), frames=200)
LIFE = dict(plan=[(0, 'slouch'), (2.6, 'surprise'), (4.6, 'angry'), (6.8, 'sad'), (9.6, 'joy'), (12.6, 'slouch')], talk=(4.9, 6.4), seconds=14.5)
FILMS = [('sneak', 120, 'loose', dict(heading=1.5708, position=[-1.6, 0, 0])), ('dance', 120, 'music'), ('stomp', 100, 'loose'), ('sit', 119, 'loose')]
