"""Render jobs for the comparison pictures: the drawing's own cameras (build.py: turnaround, portrait, figure).
usage: python3 jobs.py CACHE → CACHE/job_turn.json, job_portrait.json, job_figure.json"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import who
C = os.path.abspath(sys.argv[1])
base = dict(scene=C + '/scene.npz', offsets=C + '/engine/offsets.json', still_marks=True, samples=16)
turn = [dict(name=f'turn{i}', yaw=yaw, s=1.05, cx=210, cy=50 + 118 * 1.05, W=420, H=472, lw=2.2, bg=who.PANEL)
        for i, yaw in enumerate(getattr(who, 'TURN_YAWS', (0, -45, -90)))]
json.dump(dict(base, frames=C + '/stand.bin', out=C + '/cmp', views=turn), open(C + '/job_turn.json', 'w'))
ps = getattr(who, 'PORTRAIT_S', 1.42)
json.dump(dict(base, frames=C + '/stand_head.bin', out=C + '/cmp',
               views=[dict(name='portrait', yaw=-20, s=ps, cx=250, cy=70 + 118 * ps, W=500, H=600, lw=2.5, bg=who.PANEL)]),
          open(C + '/job_portrait.json', 'w'))
s = 780 / 1410
json.dump(dict(base, frames=C + '/stand_fig.bin', out=C + '/cmp',
               views=[dict(name='figure', yaw=-22, pitch=-7, s=s, cx=250, cy=840 - who.FLOOR * s, W=500, H=900, lw=1.9,
                           bg=who.PANEL)]), open(C + '/job_figure.json', 'w'))
