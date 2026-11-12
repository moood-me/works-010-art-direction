"""Вера of С14: what is the character's own for the pictures and films (drawing.py, make.py)."""
FOLDER = 'r39-s14-vera'
WHO = 'vera'                      # the style's module
NAME = 'Вера'
SHEET = '#f2eae7'                 # lite(BG, .55): the sheet of her portrait
MIRROR = False
FIG_S = 1.3                       # pixels in a unit on the figure's sheet
BUST_S = 2.1                      # pixels in a head unit on the busts
EXPR_S = 1.5
HS = 0.56                         # head units in a figure unit
HEAD_H = 516                      # the face's centre above the ground, units
BUSTS = [(0, 'front'), (0.5, 'q')]            # the style has no profile of Вера
EXPRS = ['calm', 'joy', 'surprise', 'sad', 'angry']
EXPR_RU = {'calm': 'спокойна', 'joy': 'радость', 'surprise': 'удивление', 'sad': 'грусть', 'angry': 'злость'}
Q_YAW = -27                       # the camera's turn for the drawing's three-quarter (degrees; she looks to our right)
DRAWN_HEAD = dict(headYaw=24, headTilt=-4)    # the figure's sheet: the body faces us, the head is turned and tilted
WALK = dict(motion='walk', ground='path')
FILMS = ['turn', 'walk', 'life', 'bow']
HERO = dict(headYaw=10, headTilt=-3)
STEPS = [['f:', 'hair', 'bun', 'glasses', 'nose', 'ear', 'paper', 'line', 'scarf', 'placket', 'button', 'brad'], ['f:']]
STEP_RU = ['полосы и оболочки на скелете SOMA', 'волосы, нос, очки, шарф, бумаги, скрепки', 'лицо из кусков', 'бумага: тени, кромки, зерно']
MOTIONS = dict(bow=dict(frames=36, yaw=-.7), idle=dict(frames=60))
LIFE_EXPR = [(18, 'joy'), (40, 'calm'), (58, 'surprise'), (76, 'sad'), (94, 'angry'), (112, 'calm')]
LIFE_TALK = [(24, True), (40, False), (112, True), (128, False)]
FIG_YAW = 0
FIG_OVERLAY = True
HERO_YAW = -22
MID = .86                         # the middle of the figure, metres: where the films' camera looks
BUST_SET = {}
OTHER_SIDE = False
SIDE_RU = 'профиль'
HERO_WARM = 1.5
