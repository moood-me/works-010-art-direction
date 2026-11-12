# All pictures, films and numbers of the page, made again from the repository:
#   python3 tools/pictures.py [scene …]
# For each scene: its numbers with and without the correction (measures/<scene>.json, -raw.json, and a summary
# measures/<scene>.txt), a sheet of moments from two sides (pics/<scene>-sheet.png), two short films from two sides
# (pics/<scene>-<view>.mp4, 15 frames a second), and the touch close up — Kimodo's own and with the correction
# (pics/<scene>-close.png). Headless Chromium through tools/shots.cjs; frames in a temporary folder.
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(os.path.dirname(HERE))
PICS = os.path.join(ITEM, 'pics')
# scene: its frames, the two sides (views of scenes.json), the moment of the close-up, the moments of the sheet (even:
# the films take every second frame)
SCENES = {k: {'frames': 235, 'views': ['side', 'whole'], 'close': 225, 'sheet': [0, 60, 120, 159, 183, 204, 222, 234]}
          for k in ('lean-child', 'lean-oldman', 'bar-oldman', 'lean-elf', 'lean-child-s1', 'lean-child-s2')}
for k in ('lean-child-s1', 'lean-child-s2'): SCENES[k]['films'] = False   # the seeds: a sheet and the numbers, no films
LABEL = {'side': 'сбоку', 'whole': 'весь путь', 'front': 'спереди'}


def run(jobs):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f: json.dump(jobs, f)
    subprocess.run(['node', os.path.join(HERE, 'shots.cjs'), f.name], check=True, cwd=ITEM)


def scene(name):
    s = SCENES[name]; tmp = tempfile.mkdtemp()
    jobs = [{'scene': name, 'measure': f'measures/{name}.json'}, {'scene': name, 'raw': True, 'measure': f'measures/{name}-raw.json'}]
    for v in s['views']:
        if s.get('films', True):
            jobs.append({'scene': name, 'view': v, 'frames': [0, s['frames'] - 1, 3], 'out': f'{tmp}/{v}-%03d.png', 'w': 480, 'h': 400})
        else:   # only the sheet's moments, named as the film's frames would be
            jobs += [{'scene': name, 'view': v, 't': t, 'out': f'{tmp}/{v}-{t // 3:03d}.png', 'w': 480, 'h': 400} for t in s['sheet']]
    jobs += [{'scene': name, 'view': 'close', 't': s['close'], 'out': f'{tmp}/close1.png', 'w': 600, 'h': 450},
             {'scene': name, 'view': 'close', 'raw': True, 't': s['close'], 'out': f'{tmp}/close0.png', 'w': 600, 'h': 450}]
    run(jobs)
    with open(os.path.join(ITEM, 'measures', name + '.txt'), 'w') as f:
        for kind in ('', '-raw'):
            f.write(f'— {"без поправки (Kimodo как есть)" if kind else "с поправкой"}\n')
            f.write(subprocess.run(['python3', os.path.join(HERE, 'report.py'), f'measures/{name}{kind}.json'], cwd=ITEM, capture_output=True, text=True, check=True).stdout)
    for v in s['views'] if s.get('films', True) else []:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '10', '-i', f'{tmp}/{v}-%03d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                        '-crf', '30', '-preset', 'slow', '-movflags', '+faststart', os.path.join(PICS, f'{name}-{v}.mp4')], check=True)
    items = [f'{LABEL[v]}, кадр {t}|{tmp}/{v}-{t // 3:03d}.png' for v in s['views'] for t in s['sheet']]
    subprocess.run(['python3', os.path.join(HERE, 'sheet.py'), os.path.join(PICS, f'{name}-sheet.png'), str(len(s['sheet'])), *items], check=True)
    subprocess.run(['python3', os.path.join(HERE, 'sheet.py'), os.path.join(PICS, f'{name}-close.png'), '2',
                    f'Kimodo как есть, кадр {s["close"]}|{tmp}/close0.png', f'с поправкой|{tmp}/close1.png'], check=True)
    # one picture of the scene: the first side at the moment of the close-up
    subprocess.run(['python3', '-c', f'from PIL import Image; Image.open("{tmp}/{s["views"][0]}-{s["close"] // 3:03d}.png").save("{PICS}/{name}.png")'], check=True)


if __name__ == '__main__':
    for n in sys.argv[1:] or list(SCENES): scene(n)
