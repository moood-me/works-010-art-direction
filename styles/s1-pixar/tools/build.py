"""build — draws every picture of the page: svg/*.svg, then pics/*.png through headless Chrome.

    python3 tools/build.py            # all
    python3 tools/build.py portraits  # only names that contain the word
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pix import Canvas, f, smooth_path, mix
from face import expr, draw_head
from person import draw_person
import cast
import marat
import kira

ROOT = os.path.dirname(HERE)
SVG = os.path.join(ROOT, "svg")
PICS = os.path.join(ROOT, "pics")
SCRATCH = "/home/user/cache/styles-s1-pixar/render"   # full-size PNG renders, outside the repository
os.makedirs(SVG, exist_ok=True)
os.makedirs(PICS, exist_ok=True)

PEOPLE = {
    "anya": cast.anya_person, "savely": cast.savely_person, "tim": cast.tim_person, "vera": cast.vera_person,
    "marat": marat.marat_person, "kira": kira.kira_person,
}
BG = {   # inner, outer of a soft backdrop
    "anya": ("#f4ece0", "#c9d6c4"), "savely": ("#f3e5cf", "#c7a982"), "tim": ("#eef3f6", "#a9c3d6"),
    "vera": ("#eceef2", "#a7b0bf"), "cast": ("#f6efe4", "#cbbfae"),
    "marat": ("#f7ead8", "#d9a482"), "kira": ("#ebe8ee", "#a99db4"),
}


def backdrop(cv, key, cx=None, cy=None, r=None):
    a, b = BG[key]
    cx = cv.w / 2 if cx is None else cx
    cy = cv.h * 0.42 if cy is None else cy
    r = max(cv.w, cv.h) * 0.75 if r is None else r
    g = cv.radgrad([(0, a, 1), (0.55, mix(a, b, 0.45), 1), (1, b, 1)], cx, cy, r)
    cv.add(f'<rect width="{cv.w}" height="{cv.h}" fill="url(#{g})"/>')


def floor(cv, y, key):
    a, b = BG[key]
    g = cv.lingrad([(0, mix(b, "#ffffff", 0.2), 0), (1, mix(b, "#000000", 0.08), 0.6)], 0, y - 40, 0, cv.h)
    cv.add(f'<rect x="0" y="{f(y - 40)}" width="{cv.w}" height="{f(cv.h - y + 40)}" fill="url(#{g})"/>')


def save(cv, name):
    p = os.path.join(SVG, name + ".svg")
    with open(p, "w") as fh:
        fh.write(cv.svg())
    os.makedirs(SCRATCH, exist_ok=True)
    png = os.path.join(SCRATCH, name + ".png")
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={cv.w},{cv.h}", f"--screenshot={png}", "file://" + p],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    subprocess.run(["convert", png, "-quality", "88", os.path.join(PICS, name + ".webp")], check=True)
    print("made", name)


# ------------------------------------------------------------------ what each character does

PORTRAIT = {
    "anya": dict(yaw=0.32, ex=expr(smile=0.45, gaze=(-0.3, -0.35), open=0.92), head_roll=0.07, head_yaw=-0.05),
    "savely": dict(yaw=-0.3, ex=expr(frown=0.45, brow_in=-0.6, open=0.72, gaze=(0.25, 0.15)), head_roll=-0.04, head_pitch=0.06),
    "tim": dict(yaw=0.3, ex=expr(smile=0.9, mopen=0.35, skew=0.35, brow_l=0.7, squint=0.2, gaze=(0.35, 0)), head_roll=-0.08),
    "vera": dict(yaw=-0.32, ex=expr(open=0.84, brow_in=-0.15, frown=0.15, gaze=(0.15, 0)), head_pitch=-0.03),
}

FIGURE = {
    "anya": dict(yaw=0.25, ex=expr(smile=0.5, gaze=(-0.25, -0.3)), head_roll=0.08,
                 pose=dict(el={-1: (-42, 182, 8), 1: (42, 182, 8)}, wr={-1: (-11, 262, 32), 1: (11, 266, 32)}, curl=0.6,
                           kn={-1: (-7, 425, 12)}, an={-1: (-15, 548, 2)})),
    "savely": dict(yaw=-0.35, ex=expr(frown=0.4, brow_in=-0.55, open=0.75), head_pitch=0.05,
                   pose=dict(el={-1: (-40, 170, -16), 1: (40, 170, -16)}, wr={-1: (-16, 246, -30), 1: (16, 246, -30)},
                             hide_hand=(-1, 1), an={-1: (-17, 448, 0), 1: (17, 448, 0)}, kn={-1: (-15, 370, 2), 1: (15, 370, 2)})),
    "tim": dict(yaw=0.3, ex=expr(smile=0.9, mopen=0.35, skew=0.35, brow_l=0.7, squint=0.2, gaze=(0.35, 0)), head_roll=-0.1,
                pose=dict(el={-1: (-34, 140, -14)}, wr={-1: (-12, 188, -26)}, hide_hand=(-1,), curl=0.9,
                          kn={-1: (-14, 292, 3), 1: (14, 292, 3)}, an={-1: (-19, 372, -2), 1: (19, 372, -2)})),
    "vera": dict(yaw=-0.3, ex=expr(open=0.84, brow_in=-0.15, frown=0.15, gaze=(0.15, 0)),
                 pose=dict(el={1: (48, 196, -6)}, wr={1: (34, 286, 18)}, hide_hand=(1,),
                           kn={-1: (-8, 450, 10)}, an={-1: (-6, 574, 14)})),
}

FLOOR = {"anya": 566, "savely": 462, "tim": 388, "vera": 590, "marat": 642, "kira": 564}

# the two of round three: Марат laughs with the whole body, Кира slouches and looks from under the fringe
MARAT_SMILE = expr(smile=0.85, mopen=0.45, squint=0.5, lower=0.5, brow=0.2)
MARAT_LAUGH = expr(smile=1.0, mopen=0.95, mwide=1.1, squint=1.0, open=1.0, lower=1.15, brow=0.5)
KIRA_LOOK = expr(open=0.74, brow=-0.5, brow_in=-0.45, skew=0.45, smile=0.1, gaze=(-0.75, -0.25))
PORTRAIT.update(
    marat=dict(yaw=-0.3, ex=dict(MARAT_SMILE, gaze=(0.25, 0)), head_roll=0.06, head_pitch=0.03, s=2.05, top=300),
    kira=dict(yaw=0.34, ex=KIRA_LOOK, head_roll=0.07, head_pitch=-0.13),
)
FIGURE.update(
    marat=dict(yaw=-0.22, ex=dict(MARAT_LAUGH, gaze=(0.2, 0)), head_roll=0.1, head_pitch=0.1,
               pose=dict(bend=dict(x=[(-40, 16), (110, 10), (330, -10), (500, -4), (642, 0)],
                                   z=[(-40, -12), (110, -8), (300, 8), (480, 3), (642, 0)]),
                         sh={-1: (-76, 110, -4)}, el={-1: (-128, 178, 4), 1: (146, 236, -22)},
                         wr={-1: (-150, 86, 18), 1: (90, 316, 12)},
                         hand_dir={-1: (-0.25, -1, 0.1), 1: (-0.55, 0.5, 0.67)}, palm={-1: (0.1, 0, 1)},
                         spread={-1: 0.9}, curl={-1: 0.12, 1: 1.35},
                         kn={1: (48, 485, 6)}, an={-1: (-16, 622, -2), 1: (62, 622, 4)})),
    kira=dict(yaw=0.3, ex=KIRA_LOOK, head_roll=0.08, head_pitch=-0.13,
              pose=dict(bend=dict(x=[(-40, -6), (100, -2), (300, 9), (428, 4), (564, 0)], z=kira.SLOUCH["z"]),
                        el={1: (52, 196, -10)}, wr={1: (17, 250, 24)}, hide_hand=(1,),
                        kn={-1: (-24, 432, 14)}, an={-1: (-38, 544, 6), 1: (4, 544, -2)})),
)
CALM = {"savely": expr(frown=0.3, open=0.8), "marat": MARAT_SMILE,
        "kira": expr(open=0.8, brow=-0.4, brow_in=-0.2, frown=0.12, gaze=(0, -0.1))}


def portrait(name, w=640, h=760, s=2.75):
    cv = Canvas(w, h)
    backdrop(cv, name, cy=h * 0.38)
    P = PEOPLE[name]()
    kw = dict(PORTRAIT[name])
    s = kw.pop("s", s)                 # a big man is drawn smaller, so that his shoulders fit the sheet
    hy = P.get("head_at", (0, 0, 0))[1]
    draw_person(cv, P, w / 2, kw.pop("top", 285) - hy * s, s, shadow=False, **kw)
    save(cv, f"{name}-portrait")


def figure(name, w=620, h=900):
    cv = Canvas(w, h)
    backdrop(cv, name, cy=h * 0.4)
    floor(cv, h - 90, name)
    P = PEOPLE[name]()
    fl = FLOOR[name]
    s = min(1.6, (h - 150) / (fl + 60))
    draw_person(cv, P, w / 2, h - 90 - fl * s, s, **FIGURE[name])
    save(cv, f"{name}-figure")


def turnaround(name, w=1500, h=900):
    cv = Canvas(w, h)
    backdrop(cv, name, cy=h * 0.4, r=w * 0.7)
    floor(cv, h - 90, name)
    P = PEOPLE[name]()
    fl = FLOOR[name]
    s = min(1.6, (h - 150) / (fl + 60))
    calm = CALM.get(name, expr(smile=0.25))
    for i, yaw in enumerate([0.0, 0.62, 1.5708]):
        draw_person(cv, P, w * (0.18 + 0.32 * i), h - 90 - fl * s, s, yaw=yaw, ex=calm)
    save(cv, f"{name}-turnaround")


EXPR = [
    ("joy", expr(smile=1.0, mopen=0.85, mwide=1.15, squint=0.45, brow=0.45, gaze=(0, -0.1))),
    ("surprise", expr(open=1.3, mopen=1.0, mwide=0.5, brow=1.3, teeth=False, pupil=0.75)),
    ("sadness", expr(brow_in=1.3, brow=-0.1, frown=1.0, open=0.72, gaze=(0.1, 0.65), lower=0.2, mwide=0.85)),
    ("anger", expr(brow_in=-1.4, brow=-0.6, squint=0.5, frown=0.45, mopen=0.75, mwide=1.2, gaze=(0, 0.05))),
]


EXPR_S = {"marat": 1.6}     # a big man is drawn smaller, so that four of him fit the sheet
EXPR_OF = {
    # Марат: the laugh shuts the eyes to slits; Кира never smiles openly — her joy is a crooked smirk
    "marat": [("joy", MARAT_LAUGH), EXPR[1],
              ("sadness", expr(brow_in=1.3, brow=-0.1, frown=1.0, open=0.72, gaze=(0.1, 0.65), lower=0.2, mwide=0.8)),
              ("anger", expr(brow_in=-1.4, brow=-0.6, squint=0.5, frown=0.6, mopen=0.8, mwide=1.0, gaze=(0, 0.05)))],
    "kira": [("joy", expr(smile=0.5, skew=0.6, open=0.92, brow=0.3, brow_l=0.7, lower=0.3, gaze=(0.45, -0.1))),
             ("surprise", expr(open=1.3, brow=1.2, mopen=0.5, mwide=0.55, teeth=False, pupil=0.8)),
             ("sadness", expr(brow_in=1.1, brow=-0.2, frown=0.75, open=0.68, gaze=(-0.25, 0.7), lower=0.15, mwide=0.8)),
             ("anger", expr(brow_in=-1.3, brow=-0.7, squint=0.45, frown=0.7, mwide=0.9, skew=-0.35, gaze=(0, 0.05)))],
}


def expressions(name, w=1600, h=560, s=2.3):
    s = EXPR_S.get(name, s)
    cv = Canvas(w, h)
    backdrop(cv, name, cy=h * 0.45, r=w * 0.7)
    P = PEOPLE[name]()
    hy = P.get("head_at", (0, 0, 0))[1]
    rolls = [0.06, 0.0, -0.05, 0.0]
    for i, (k, e) in enumerate(EXPR_OF.get(name, EXPR)):
        if name == "savely":
            e = dict(e)
            e["open"] = e.get("open", 1.0) * 0.85
        draw_person(cv, P, w * (0.125 + 0.25 * i), 250 - hy * s, s, yaw=0.18, ex=e, shadow=False, head_roll=rolls[i],
                    head_pitch=0.06 if k == "sadness" else 0.0)
    save(cv, f"{name}-expressions")


def together(w=1600, h=1000):
    cv = Canvas(w, h)
    backdrop(cv, "cast", cy=h * 0.4, r=w * 0.7)
    floor(cv, h - 110, "cast")
    s = 1.3
    base = h - 110
    # back row: Вера, Аня, Савелий; Тим in front
    items = [
        ("vera", 1130, base - 20, -0.38, expr(open=0.86, frown=0.1, gaze=(-0.2, 0.25)), dict(el={1: (48, 196, -6)}, wr={1: (34, 286, 18)}, hide_hand=(1,)), 0.0),
        ("savely", 420, base - 10, 0.42, expr(frown=0.35, brow_in=-0.5, open=0.75, gaze=(0.35, 0.3)), dict(el={-1: (-40, 170, -16), 1: (40, 170, -16)}, wr={-1: (-16, 246, -30), 1: (16, 246, -30)}, hide_hand=(-1, 1)), 0.0),
        ("anya", 860, base - 25, -0.15, expr(smile=0.55, gaze=(-0.4, 0.3)), dict(el={-1: (-42, 182, 8), 1: (42, 182, 8)}, wr={-1: (-11, 262, 32), 1: (11, 266, 32)}, curl=0.6), 0.1),
        ("tim", 640, base + 25, 0.2, expr(smile=0.9, mopen=0.4, skew=0.35, brow_l=0.7, squint=0.2, gaze=(0.4, -0.2)), dict(el={-1: (-34, 140, -14)}, wr={-1: (-12, 188, -26)}, hide_hand=(-1,), curl=0.9), -0.1),
    ]
    for name, x, fy, yaw, e, pose, roll in items:
        P = PEOPLE[name]()
        fl = FLOOR[name]
        draw_person(cv, P, x, fy - fl * s, s, yaw=yaw, ex=e, pose=pose, head_roll=roll)
    save(cv, "cast")


def together6(w=2000, h=1100):
    """all six; the four stand as in `together`, Марат behind them in the middle, Кира a step apart"""
    cv = Canvas(w, h)
    backdrop(cv, "cast", cy=h * 0.4, r=w * 0.7)
    floor(cv, h - 110, "cast")
    s = 1.3
    base = h - 110
    items = [
        ("marat", 870, base - 22, 0.1, dict(MARAT_LAUGH, gaze=(-0.2, 0.2)), FIGURE["marat"]["pose"], 0.08, 0.1),
        ("vera", 1390, base - 20, -0.38, expr(open=0.86, frown=0.1, gaze=(-0.2, 0.25)), dict(el={1: (48, 196, -6)}, wr={1: (34, 286, 18)}, hide_hand=(1,)), 0.0, 0.0),
        ("savely", 330, base - 10, 0.42, expr(frown=0.35, brow_in=-0.5, open=0.75, gaze=(0.35, 0.3)), dict(el={-1: (-40, 170, -16), 1: (40, 170, -16)}, wr={-1: (-16, 246, -30), 1: (16, 246, -30)}, hide_hand=(-1, 1)), 0.0, 0.0),
        ("anya", 1150, base - 25, -0.15, expr(smile=0.55, gaze=(-0.4, 0.3)), dict(el={-1: (-42, 182, 8), 1: (42, 182, 8)}, wr={-1: (-11, 262, 32), 1: (11, 266, 32)}, curl=0.6), 0.1, 0.0),
        ("tim", 560, base + 25, 0.2, expr(smile=0.9, mopen=0.4, skew=0.35, brow_l=0.7, squint=0.2, gaze=(0.4, -0.2)), dict(el={-1: (-34, 140, -14)}, wr={-1: (-12, 188, -26)}, hide_hand=(-1,), curl=0.9), -0.1, 0.0),
        ("kira", 1690, base + 2, -0.5, dict(KIRA_LOOK, gaze=(0.7, -0.3)),
         dict(el={-1: (-46, 192, -8), 1: (46, 192, -8)}, wr={-1: (-17, 248, 24), 1: (17, 248, 24)}, hide_hand=(-1, 1),
              kn={1: (18, 432, 12)}, an={1: (26, 544, 4)}), -0.07, -0.13),
    ]
    for name, x, fy, yaw, e, pose, roll, pitch in items:
        P = PEOPLE[name]()
        fl = FLOOR[name]
        draw_person(cv, P, x, fy - fl * s, s, yaw=yaw, ex=e, pose=pose, head_roll=roll, head_pitch=pitch)
    save(cv, "cast6")


def construction(w=1200, h=760):
    """the head's construction, with guide lines: where the eyes, nose, mouth sit; eye spacing"""
    cv = Canvas(w, h, bg="#f6f1e8")
    c = cast.anya()
    s = 4.6
    cx, cy = 330, 350
    from body import Rig, tube
    for x0, yaw in ((cx, 0.0), (880, 1.5708)):
        rig = Rig(x0, cy, s, yaw)
        tube(cv, rig, [(0, 30, -12), (0, 60, -11), (0, 92, -10)], [9.5, 9.8, 10.5], c["skin"], c["skin_sh"], caps=(False, False))
    hd = draw_head(cv, c, cx, cy, s, ex=expr(smile=0.3), hair=None)
    ink = "#b4532a"
    for y, lab in [(-50, ""), (c["eye_y"], ""), (c["nose_y"] + 3, ""), (c["mouth_y"], ""), (50, "")]:
        yy = cy + y * s
        cv.add(f'<path d="M{f(cx - 60 * s)},{f(yy)} L{f(cx + 60 * s)},{f(yy)}" stroke="{ink}" stroke-width="1.5" stroke-dasharray="6 5" opacity="0.8"/>')
    # eye widths: three eye-widths across the eye line
    for x in (-c["eye_x"] - c["eye_w"] / 2, -c["eye_x"] + c["eye_w"] / 2, c["eye_x"] - c["eye_w"] / 2, c["eye_x"] + c["eye_w"] / 2):
        xx = cx + x * s
        cv.add(f'<path d="M{f(xx)},{f(cy + (c["eye_y"] - 14) * s)} L{f(xx)},{f(cy + (c["eye_y"] + 14) * s)}" stroke="{ink}" stroke-width="1.5" opacity="0.8"/>')
    # profile
    c2 = cast.anya()
    draw_head(cv, c2, 880, cy, s, yaw=1.5708, ex=expr(smile=0.3), hair=None)
    for y in (-50, c["eye_y"], c["nose_y"] + 3, c["mouth_y"], 50):
        yy = cy + y * s
        cv.add(f'<path d="M{f(880 - 62 * s)},{f(yy)} L{f(880 + 62 * s)},{f(yy)}" stroke="{ink}" stroke-width="1.5" stroke-dasharray="6 5" opacity="0.8"/>')
    save(cv, "rules-head")


JOBS = {
    **{f"{n}-portrait": (lambda n=n: portrait(n)) for n in PEOPLE},
    **{f"{n}-figure": (lambda n=n: figure(n)) for n in PEOPLE},
    "anya-turnaround": lambda: turnaround("anya"),
    "tim-turnaround": lambda: turnaround("tim"),
    "tim-expressions": lambda: expressions("tim"),
    "savely-expressions": lambda: expressions("savely"),
    "cast": together,
    "marat-turnaround": lambda: turnaround("marat"),
    "kira-turnaround": lambda: turnaround("kira"),
    "marat-expressions": lambda: expressions("marat"),
    "kira-expressions": lambda: expressions("kira"),
    "cast6": together6,
    "rules-head": construction,
}

if __name__ == "__main__":
    want = sys.argv[1:]
    for k, fn in JOBS.items():
        if not want or any(w in k for w in want):
            fn()
