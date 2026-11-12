"""Кира's drawing as the shapes the 3D is fitted to: the style's own front and profile (styles/s3-graphic/tools/kira.py),
named for build.py. The head's shapes are in the head's own units (eye line y=0; kira.py draws the head tilted and
pushed forward: PITCH, HEAD_DZ, HEAD_DY put the built head there); the body's are the figure's (soles at y=1350), the
profile's upper body leaned back as kira.LEAN does."""
import os, sys
import numpy as np
S3 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'styles', 's3-graphic', 'tools')
sys.path.insert(0, S3)
import kira  # noqa: E402
from lib import mx  # noqa: E402,F401

C = kira.C
FLOOR, CROWN = 1350.0, -130.0
# the head in the figure: its own origin goes HEAD_DY down and HEAD_DZ forward (kira.HX + 14 in the profile), and it
# is pitched down about its neck point (0, 100) as the profile's head is turned
PITCH, HEAD_DZ, HEAD_DY, PIVOT_Y = 12.0, kira.HX + 14.0, float(kira.HY), 100.0
LEAN_DEG, LEAN_Y = 6.0, 640.0          # kira.LEAN: the upper body turned back about the hips

# ---- the head (its own units)
HEAD_F = [kira.FACE_F, 'M -30 80 L -32 176 L 32 176 L 30 80 Z']
NECK_S = 'M -40 70 C -36 120, -40 150, -46 176 L 18 176 C 14 150, 16 128, 22 104 Z'
NOSE_S = 'M 70 -2 C 76 14, 90 28, 94 40 C 96 46, 90 50, 82 50 C 76 50, 72 48, 68 48 Z'
PLANE_S = [kira.FACE_S, NECK_S]
HEAD_S = PLANE_S + [NOSE_S]
HAIR_FRONT = [kira.NEAR_F, kira.FRINGE_F]      # what hangs over the face in the front view
HAIR_BACK_F = kira.BACK_F
HAIR_S = kira.HAIR_S

# ---- the body (the figure's units)
HOODIE_F = kira.HOODIE_F
HOODIE_S = ('M -44 178 C -96 196, -122 260, -118 340 C -116 440, -106 540, -96 640 C -40 658, 40 656, 100 636 '
            'C 104 520, 100 400, 90 300 C 84 240, 66 196, 30 178 C 10 168, -24 168, -44 178 Z')      # local to kira.body_s()
HOOD_F = ('M -112 186 C -150 160, -146 116, -110 100 C -60 86, 60 86, 110 100 C 146 116, 150 160, 112 186 '
          'C 70 204, 20 222, 0 250 C -20 222, -70 204, -112 186 Z')                                  # local to kira.body_f()
HOOD_S = ('M -64 190 C -104 170, -108 120, -74 100 C -44 86, 10 100, 40 130 C 60 150, 60 176, 44 190 '
          'C 20 206, -30 208, -64 190 Z')                                                            # local to kira.body_s()
POCKET_F = 'M -74 452 C -30 458, 30 458, 74 452 C 90 490, 100 540, 104 588 C 40 602, -40 602, -104 588 C -100 540, -90 490, -74 452 Z'


def lean_z(y):
    """How far back the leaned upper body is at figure height y (drawing units)."""
    return -np.sin(np.radians(LEAN_DEG)) * (LEAN_Y - np.asarray(y, float))
