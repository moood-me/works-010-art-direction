"""Who this is, for make_pics.py: the drawing's sheets (their scales and the pose of the figure sheet) and the films."""
import math
import drawing as D

NAME = 'marat'
REST = 'grin'
FIG_PX = 1020 / 910 * 0.5      # the figure sheet: px a head unit (build.py's figure(): 1020 / TOP; the head at 0.5)
FIG_YAW = 0.55
FIG_CX = -(50 / FIG_PX * D.K) / math.cos(FIG_YAW)       # marat.X = 450: the figure stands 50 px right of the middle
Q_YAW = 0.55
FIG_EXPR = 'joy'
FIG_PROPS = None
# the figure as drawn: he laughs leaning back, the near arm up (the drawing's ladle is not made), the far one thrown open
FIG_POSE = dict(lean=-0.1, headNod=-0.1, headTurn=0.1,
                arms={'Right': {'upper': [-0.95, 0.05, -0.05], 'fore': [-0.08, 1, 0.1]}, 'Left': {'upper': [0.55, -0.3, 0.75], 'fore': [0.45, 0.1, 0.9]}})
BUST_POSE = dict(out=0.2)
BUST_CX = (0.0, 0.0)

FAR = dict(mode='persp', fov=22, dist=7.6, cy=0.98, follow=True, focus=None, pitch=0.04)
FILMS = dict(
    turn=dict(w=480, h=720, set=dict(cam=dict(mode='ortho', h=2.25, cy=0.98, cx=0, yaw=0, pitch=0, follow=False, focus=None)), **{'from': 0, 'to': 35, 'step': 1}, yaw=[0, 6.2832 * 35 / 36]),
    walk=dict(w=480, h=720, set=dict(still=False, clip='walk', cam=dict(FAR, yaw=0.9)), **{'from': 0, 'to': 117.5}),
    wave=dict(w=520, h=720, set=dict(still=False, clip='wave', exprTrack=[[0, REST], [0.6, 'joy'], [2.4, REST]], cam=dict(FAR, yaw=0.45)), **{'from': 0, 'to': 87.5}),
    talk=dict(w=480, h=600, set=dict(still=False, clip='idle', talk=True, talkFrom=0.4, talkTo=2.6,
                                      exprTrack=[[0, REST], [2.7, 'joy'], [3.7, 'surprise'], [4.4, REST]],
                                      cam=dict(mode='persp', fov=22, dist=2.5, follow=False, focus='Head', up=0.05, yaw=0.55, pitch=0.02)), **{'from': 0, 'to': 147.5}),
)
