"""A render job for a moving picture: frames from move.mjs, a camera that goes with the character.
usage: python3 films.py CACHE NAME FRAMES.bin KIND [yaw]   KIND: full (the whole figure) | face (a close view on the head)
→ CACHE/job_NAME.json; frames go to CACHE/film/NAME/"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import who
C, name, frames, kind = os.path.abspath(sys.argv[1]), sys.argv[2], os.path.abspath(sys.argv[3]), sys.argv[4]
yaw = float(sys.argv[5]) if len(sys.argv) > 5 else -28
H = who.FLOOR + 110                                  # units from above the crown to under the floor
if kind == 'full':
    s = 600 / H
    v = dict(name=name, yaw=yaw, pitch=-7, s=s, cx=240, cy=600 - who.FLOOR * s, W=480, H=640, lw=2.0, bg=who.PANEL,
             follow=True)
else:
    s = 2.1
    v = dict(name=name, yaw=yaw, pitch=-4, s=s, cx=240, cy=215, W=480, H=480, lw=2.6, bg=who.PANEL, follow='head')
json.dump(dict(scene=C + '/scene.npz', offsets=C + '/engine/offsets.json', frames=frames, out=f'{C}/film/{name}',
               samples=8, no_subsurf=kind == 'full', views=[v]), open(f'{C}/job_{name}.json', 'w'))
print(json.dumps(v))
