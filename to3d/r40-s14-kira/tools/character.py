"""Кира of С14: what is the character's own for the pictures and films (drawing.py, make.py)."""
FOLDER = 'r40-s14-kira'
WHO = 'kira'                      # the style's module
NAME = 'Кира'
SHEET = '#ece9d7'                 # lite(BG, .55): the sheet of her portrait
MIRROR = False
FIG_S = 1.3                       # pixels in a unit on the figure's sheet
BUST_S = 2.1                      # pixels in a head unit on the busts
EXPR_S = 1.5
HS = 0.56                         # head units in a figure unit
HEAD_H = 492                      # the face's centre above the ground when she stands straight, units
BUSTS = [(0, 'front'), (0.5, 'q'), (1, 'side')]
EXPRS = ['calm', 'joy', 'surprise', 'sad', 'angry']
EXPR_RU = {'calm': 'как всегда', 'joy': 'радость (усмешка)', 'surprise': 'удивление', 'sad': 'грусть', 'angry': 'злость'}
Q_YAW = -27                       # the camera's turn for the drawing's three-quarter (degrees)
DRAWN_HEAD = dict(headYaw=-8, headTilt=-6)    # the figure's sheet: the whole body three-quarters, the head hung and tilted
FIG_YAW = -42                     # the figure is drawn turned to our right
FIG_OVERLAY = False               # the drawn slouch is a flat S of pieces: side by side, not one over the other
BUST_SET = dict(straight=True)    # the busts are drawn straight: the slouch is taken off to lay them over
HERO = dict(headYaw=-6, headTilt=-5)
HERO_YAW = -30
MID = .80
WALK = dict(motion='walk', ground='path')
FILMS = ['turn', 'walk', 'life', 'sneak']
STEPS = [['f:', 'hair', 'fringe', 'nose', 'ear', 'cup', 'phones', 'pocket', 'string', 'hood', 'hem', 'LeftLace', 'RightLace'], ['f:']]
STEP_RU = ['полосы и оболочки на скелете SOMA', 'волосы, нос, капюшон, карман, наушники', 'лицо из кусков', 'бумага: тени, кромки, зерно']
MOTIONS = dict(sneak=dict(frames=48, yaw=-.75, ground='path'))
LIFE_EXPR = [(18, 'joy'), (40, 'calm'), (58, 'surprise'), (76, 'sad'), (94, 'angry'), (112, 'calm')]
LIFE_TALK = [(24, True), (40, False), (112, True), (128, False)]
OTHER_SIDE = True
SIDE_RU = 'профиль со стороны чёлки'
HERO_WARM = 2.0
