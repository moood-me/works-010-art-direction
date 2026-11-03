"""Parts only, again (with every other object hidden). More characters and their clothes as separate parts (Workbench, their viewport colours). python3 run_more.py"""
import json, subprocess
B = '/home/user/cache/blender/blender'; C = '/home/user/cache/n5-heads'; O = C + '/r/more'; T = __file__.rsplit('/', 1)[0]
def run(f, cfg):
    cfg['out'] = O; subprocess.run([B, '-b', f'{C}/{f}', '-P', f'{T}/render_any.py', '--', json.dumps(cfg)], check=False)
jay_j = ['GEO-jay_jacket', 'GEO-jay_jacket_zipper_pull_neck', 'GEO-jay_jacket_zipper_pull_pockets']
run('jay/jay.blend', {'name': 'jay', 'head': 'GEO-jay_head', 'views': [],
    'parts': [['jacket', jay_j], ['pants', ['GEO-jay_pants']], ['shoes', ['GEO-jay_shoes_base', 'GEO-jay_shoes_extra']], ['hat', ['GEO-jay_hat']], ['shades', ['GEO-jay_shades']], ['chain', ['GEO-jay_chain']]]})
run('rain/Rain v3.3/rain_v3.2.blend', {'name': 'rain', 'head': 'GEO-rain-head', 'views': [],
    'parts': [['top', ['GEO-rain-top']], ['jeans', ['GEO-rain-jeans']], ['scarf', ['GEO-rain-scarf']], ['shoes', ['GEO-rain-shoes']], ['hair', ['GEO-rain-hair_main', 'GEO-rain-hair_ponytail', 'GEO-rain-hair_strand', 'GEO-rain-hairband']], ['teeth', ['GEO-rain-gums_upper', 'GEO-rain-gums_lower', 'GEO-rain-tongue']]]})
run('snow/Snow/snow_v4.2.blend', {'name': 'snow', 'head': 'GEO-snow-head', 'views': [],
    'parts': [['shirt', ['GEO-snow-shirt']], ['pants', ['GEO-snow-pants']], ['shoes', ['GEO-snow-shoes_base', 'GEO-snow-shoes_bottom', 'GEO-snow-shoes_parts']], ['hair', ['GEO-snow-hair_base']]]})
