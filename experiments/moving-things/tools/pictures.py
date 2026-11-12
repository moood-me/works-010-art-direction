# All pictures, films and numbers of the page, made again from the repository:
#   python3 tools/pictures.py [scene …]
# Copied from К1 (experiments/contacts/tools/pictures.py) and changed. For each scene: its numbers with and without
# the correction (measures/<scene>.json, -raw.json, and a summary measures/<scene>.txt), a sheet of moments from two
# sides (pics/<scene>-sheet.png), two films from two sides (pics/<scene>-<view>.mp4, 10 frames a second: every
# third frame), and the touches close up — Kimodo's own and with the correction (pics/<scene>-close.png).
# Headless Chromium through tools/shots.cjs; frames in a temporary folder.
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); ITEM = os.path.dirname(HERE)
PICS = os.path.join(ITEM, 'pics')
# scene: its frames, the two sides (views of scenes.json), the close-ups (view, frame, caption), the sheet's moments
# (multiples of 3: the films take every third frame)
SCENES = {
    'door': {'frames': 250, 'views': ['side', 'front'], 'sheet': [102, 129, 141, 156, 168, 180, 192, 222],
             'close': [('close', 141, 'рука на ручке'), ('close', 168, 'дверь открыта на треть')]},
    'cup': {'frames': 325, 'views': ['side', 'front'], 'sheet': [111, 141, 165, 186, 213, 252, 285, 321],
            'close': [('close', 147, 'берёт чашку'), ('mouth', 213, 'пьёт'), ('close', 291, 'ставит чашку')]},
    'box': {'frames': 268, 'views': ['side', 'front'], 'sheet': [21, 45, 63, 90, 150, 210, 249, 264],
            'close': [('close', 51, 'берёт коробку'), ('put', 252, 'ставит коробку')]},
    'chair': {'frames': 235, 'views': ['side', 'front'], 'sheet': [99, 132, 141, 153, 165, 180, 201, 234],
              'close': [('close', 150, 'взялась за спинку'), ('close', 183, 'выдвинула стул')]},
}
LABEL = {'side': 'сбоку', 'front': 'с другой стороны', 'whole': 'весь путь'}


def run(jobs):
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f: json.dump(jobs, f)
    subprocess.run(['node', os.path.join(HERE, 'shots.cjs'), f.name], check=True, cwd=ITEM)


def scene(name):
    s = SCENES[name]; tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(ITEM, 'measures'), exist_ok=True)
    jobs = [{'scene': name, 'measure': f'measures/{name}.json'}, {'scene': name, 'raw': True, 'measure': f'measures/{name}-raw.json'}]
    for v in s['views']:
        jobs.append({'scene': name, 'view': v, 'frames': [0, s['frames'] - 1, 3], 'out': f'{tmp}/{v}-%03d.png', 'w': 480, 'h': 400})
    for k, (v, t, _) in enumerate(s['close']):
        jobs += [{'scene': name, 'view': v, 't': t, 'out': f'{tmp}/close{k}-1.png', 'w': 480, 'h': 400},
                 {'scene': name, 'view': v, 'raw': True, 't': t, 'out': f'{tmp}/close{k}-0.png', 'w': 480, 'h': 400}]
    run(jobs)
    with open(os.path.join(ITEM, 'measures', name + '.txt'), 'w') as f:
        for kind in ('', '-raw'):
            f.write(f'— {"без поправки (Kimodo как есть)" if kind else "с поправкой"}\n')
            f.write(subprocess.run(['python3', os.path.join(HERE, 'report.py'), f'measures/{name}{kind}.json'], cwd=ITEM, capture_output=True, text=True, check=True).stdout)
    for v in s['views']:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '10', '-i', f'{tmp}/{v}-%03d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                        '-crf', '30', '-preset', 'slow', '-movflags', '+faststart', os.path.join(PICS, f'{name}-{v}.mp4')], check=True)
    items = [f'{LABEL[v]}, кадр {t}|{tmp}/{v}-{t // 3:03d}.png' for v in s['views'] for t in s['sheet']]
    subprocess.run(['python3', os.path.join(HERE, 'sheet.py'), os.path.join(PICS, f'{name}-sheet.png'), str(len(s['sheet'])), *items], check=True)
    close = []
    for k, (v, t, cap) in enumerate(s['close']):
        close += [f'{cap}: Kimodo как есть, кадр {t}|{tmp}/close{k}-0.png', f'{cap}: с поправкой|{tmp}/close{k}-1.png']
    subprocess.run(['python3', os.path.join(HERE, 'sheet.py'), os.path.join(PICS, f'{name}-close.png'), '2', *close], check=True)
    # one picture of the scene: the corrected close-up of its middle moment
    mid = len(s['close']) // 2
    subprocess.run(['python3', '-c', f'from PIL import Image; Image.open("{tmp}/close{mid}-1.png").save("{PICS}/{name}.png")'], check=True)


if __name__ == '__main__':
    for n in sys.argv[1:] or list(SCENES): scene(n)
