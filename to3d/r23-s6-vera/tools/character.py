"""Вера (С6): what build.py and make.py need to know about this character of the style.
Sides: the drawing's 'L' is the person's right (SOMA Right), 'R' the person's left."""
ID, LABEL, FOLDER = 'vera', 'Вера', 'r23-s6-vera'
MODULE, FUNC, BODY = 'cast', 'vera', 'VERA_B'       # styles/s6-symbolic/tools/cast.py: vera(), VERA_B
OPTS = {}

# the solids in the order cast.vera() makes them, and what each is
TUBES = ['leg:L', 'foot:L', 'leg:R', 'foot:R',      # legs and soft flat shoes
         'neck', 'neck',                            # the high collar, the neck
         'arm:L', 'hand:L', 'arm:R', 'hand:R',
         'on:Head:hair']                            # the bun
LOFTS = [('torso', [0, .25, .3, .55, .8, .92, 1]),  # the long straight coat
         ('skirt', .62),                            # its column to below the knee
         ('head',),
         ('on', 'Head', 'hair'),                    # hair pulled back tight
         ('on', 'Chest', 'folder')]                 # the folder pressed to the chest

# Moods: the posture is the expression (the style's rule «выражения — позой всего тела»). С6 has no sheet for Вера;
# the first is the drawn stand, the others are written by that rule with the drawing's pose numbers, over the drawn
# stand. Her right arm (the drawing's L) always holds the folder to the chest: only the free arm speaks.
# arms = (person's left, person's right): how much the mood holds each arm when it lies on a motion.
HOLD = (18, 3, 58, -80)
MOODS = {
    'folder': dict(label='стоит с папкой', pose={}, arms=(1, 1), yaw=-58),
    # strict: drawn up to her full height, the chin up, the free hand on the hip, the elbow out
    'strict': dict(label='строга', pose=dict(lean=-3, hunch=-2, neck=-3, nod=-6, headRoll=0, slump=0, shrug=.6,
                                             armR=(-16, 40, 10, -86), legL=(0, 4, 0, 0), legR=(0, 5, 0, 0)), arms=(1, 1), yaw=-50),
    # tired: the shoulders go down, the head sinks, the free hand comes up to the bridge of the nose under the glasses
    'tired': dict(label='устала', pose=dict(lean=3, hunch=14, neck=10, nod=24, headRoll=4, slump=3, shrug=-1.6,
                                            armR=(38, 2, 118, -22)), arms=(1, 1), yaw=-64),
    # thinking: the weight on one leg, the head a little aside, the free hand at the chin
    'thinks': dict(label='думает', pose=dict(lean=-2, hunch=5, neck=4, nod=2, headRoll=-7, slump=1,
                                             armR=(30, 4, 132, -14), legR=(8, 3, 10, 0), footR=(6, 12)), arms=(1, 1), yaw=-60),
    # surprised: she draws back, the head goes back, the free hand flies up before the chest, the fingers spread
    'surprised': dict(label='удивлена', pose=dict(lean=-9, hunch=2, neck=-6, nod=-8, headRoll=0, slump=-1, shrug=2.2,
                                                  armR=(24, 20, 124, 0), legL=(-8, 2, 2, 0), legR=(8, 2, 4, 0)), arms=(1, 1), yaw=-62),
    # angry: the body forward from the hips, the head pushed out, the free arm thrown out straight — «вон»
    'angry': dict(label='сердится', pose=dict(lean=9, hunch=4, neck=14, nod=-10, headRoll=0, slump=1, shrug=2.4,
                                              armR=(76, 6, 8, 0), legL=(-10, 2, 2, 0), legR=(12, 2, 4, 0)), arms=(1, 1), yaw=-66),
    # glad (rare, small): the head tilts, the shoulders let go, the free hand opens a little aside
    'glad': dict(label='довольна', pose=dict(lean=-4, hunch=-1, neck=-2, nod=-12, headRoll=-8, slump=0, shrug=-.4,
                                             armR=(6, 24, 34, 12), legR=(6, 4, 8, 0), footR=(4, 14)), arms=(1, 1), yaw=-52),
    # on a motion: her own carriage (the head a little down, the shoulders tired) and the folder at the chest;
    # the free arm is the motion's
    'plain': dict(label='идёт с папкой', pose={}, arms=(0, 1), menu=False),
}
MOOD_SHEET = ['folder', 'strict', 'tired', 'thinks', 'surprised', 'angry', 'glad']

# the drawing's sheets this figure is compared with
TURN = dict(k=3.2, light=1, pic='turn-vera.jpg')
FULL = dict(yaw=-58, k=3.55, x=.5, light=-1, pic='full-vera.jpg')
