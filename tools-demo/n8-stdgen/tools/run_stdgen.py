"""Run StdGEN's four stages on each input picture through the private Space; save A-pose, views and meshes."""
import os, sys, shutil, time
from gradio_client import Client, handle_file

tok = [l.split('=', 1)[1].strip() for l in open(os.path.join(os.path.dirname(__file__), '.env')) if l.startswith('HF_TOKEN')][0]
c = Client('completelyreal/StdGEN', token=tok, verbose=False)
for name in sys.argv[1:]:
    t0 = time.time(); out = f'out/{name}'; os.makedirs(out, exist_ok=True)
    ap = c.predict(handle_file(f'in/{name}.png'), 52, api_name='/arbitrary_to_apose')
    shutil.copy(ap, f'{out}/apose.png')
    gal = c.predict(handle_file(f'{out}/apose.png'), 50, api_name='/apose_to_multiview')
    for i, g in enumerate(gal):
        im = g['image']; shutil.copy(im['path'] if isinstance(im, dict) else im, f'{out}/view{i}.png')
    print(name, 'views', round(time.time() - t0), flush=True)
    gal = [{'image': handle_file(f'{out}/view{i}.png'), 'caption': None} for i in range(len(gal))]
    m = c.predict(gal, api_name='/multiview_to_mesh')
    for i, f in enumerate(m):
        if f: shutil.copy(f, f'{out}/mesh{i}' + os.path.splitext(f)[1])
    print(name, 'mesh', round(time.time() - t0), flush=True)
    r = c.predict(handle_file(m[0]), handle_file(m[1]), handle_file(m[2]), 50, api_name='/refine_mesh')
    for i, f in enumerate(r):
        if f: shutil.copy(f, f'{out}/refined{i}' + os.path.splitext(f)[1])
    print(name, 'refined', round(time.time() - t0), flush=True)
