"""Who this is, for make_pics.py: the drawing's sheets (their scales and the pose of the figure sheet) and the films."""
import drawing as D

NAME = 'anya'
REST = 'dream'
FIG_PX = 1.4 * 0.46            # the figure sheet: px a head unit (anya.figure draws the head at 0.46)
FIG_CX = 0.0
FIG_YAW = 0.5
Q_YAW = 0.55               # the drawing's three-quarter is a modest turn: at more the 3D face's far half is gone
FIG_EXPR = 'dream'
FIG_PROPS = None
# the figure as drawn: the head bent to a sprig held at the chest, the near arm across the chest, the far arm hanging
FIG_POSE = dict(headNod=0.16, headTurn=-0.14, headTilt=0.1,
                arms={'Left': {'upper': [0.22, -1, 0.1], 'fore': [-0.72, 0.6, 0.5]}})
BUST_POSE = dict(out=0.14)
BUST_CX = (0.0, 0.0)           # the camera's shift in the three-quarter and the side bust (metres)

FAR = dict(mode='persp', fov=22, dist=6.6, cy=0.86, follow=True, focus=None, pitch=0.04)
FILMS = dict(
    turn=dict(w=480, h=720, set=dict(cam=dict(mode='ortho', h=1.95, cy=0.86, cx=0, yaw=0, pitch=0, follow=False, focus=None)), **{'from': 0, 'to': 35, 'step': 1}, yaw=[0, 6.2832 * 35 / 36]),
    walk=dict(w=480, h=720, set=dict(still=False, clip='walk', cam=dict(FAR, yaw=0.9)), **{'from': 0, 'to': 117.5}),
    bow=dict(w=480, h=720, set=dict(still=False, clip='bow', cam=dict(FAR, yaw=0.5)), **{'from': 0, 'to': 87.5}),
    talk=dict(w=480, h=600, set=dict(still=False, clip='idle', talk=True, talkFrom=0.4, talkTo=2.6,
                                      exprTrack=[[0, REST], [2.7, 'joy'], [3.6, 'surprise'], [4.3, REST]],
                                      cam=dict(mode='persp', fov=22, dist=2.0, follow=False, focus='Head', up=0.03, yaw=0.55, pitch=0.02)), **{'from': 0, 'to': 147.5}),
)
