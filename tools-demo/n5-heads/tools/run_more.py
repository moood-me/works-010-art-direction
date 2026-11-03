"""More characters and their clothes as separate parts (Workbench, their viewport colours). python3 run_more.py"""
import json, subprocess
B = '/home/user/cache/blender/blender'; C = '/home/user/cache/n5-heads'; O = C + '/r/more'; T = __file__.rsplit('/', 1)[0]
def run(f, cfg):
    cfg['out'] = O; subprocess.run([B, '-b', f'{C}/{f}', '-P', f'{T}/render_any.py', '--', json.dumps(cfg)], check=False)
jay_j = ['GEO-jay_jacket', 'GEO-jay_jacket_zipper_pull_neck', 'GEO-jay_jacket_zipper_pull_pockets']
run('jay/jay.blend', {'name': 'jay', 'head': 'GEO-jay_head', 'views': ['body', 'bodytq'],
    'parts': [['jacket', jay_j], ['pants', ['GEO-jay_pants']], ['shoes', ['GEO-jay_shoes_base', 'GEO-jay_shoes_extra']], ['hat', ['GEO-jay_hat']], ['shades', ['GEO-jay_shades']], ['chain', ['GEO-jay_chain']]]})
run('jay/jay.blend', {'name': 'jay', 'head': 'GEO-jay_head', 'views': ['front', 'tq', 'side'], 'hide': ['GEO-jay_hat', 'GEO-jay_shades']})
run('phil/phil.blend', {'name': 'phil', 'head': 'GEO-phil_head', 'views': ['body', 'bodytq', 'front', 'tq', 'side'],
    'parts': [['shirt', ['GEO-phil_shirt']], ['pants', ['GEO-phil_pants', 'GEO-phil_shorts_fray']], ['flippers', ['GEO-phil_flippers']]]})
run('phileas/phileas.blend', {'name': 'phileas', 'head': 'GEO-Body', 'views': ['body', 'bodytq'], 'parts': [['backpack', ['GEO-Backpack', 'GEO-Backpack_Strap']]]})
run('einar/einar_release_v1.blend', {'name': 'einar', 'head': 'GEO-einar_head', 'views': ['body', 'bodytq', 'front', 'tq', 'side'],
    'parts': [['jacket', ['GEO-einar_jacket_main', 'GEO-einar_jacket_collar1', 'GEO-einar_jacket_collar2', 'GEO-einar_jacket_pocket1', 'GEO-einar_jacket_pocket2', 'GEO-einar_jacket_zipper', 'GEO-einar_jacket_tape', 'GEO-einar_jacket_belts']],
              ['pants', ['GEO-einar_pants_belt', 'GEO-einar_pants_belt_buckle', 'GEO-einar_pants_belt_straps']], ['boots', ['GEO-einar_boot_main.L', 'GEO-einar_boot_sole.L']], ['hat', ['GEO-einar_hat']], ['glove', ['GEO-einar_glove', 'GEO-einar_fingers']]]})
run('rain/Rain v3.3/rain_v3.2.blend', {'name': 'rain', 'head': 'GEO-rain-head', 'views': [],
    'parts': [['top', ['GEO-rain-top']], ['jeans', ['GEO-rain-jeans']], ['scarf', ['GEO-rain-scarf']], ['shoes', ['GEO-rain-shoes']], ['hair', ['GEO-rain-hair_main', 'GEO-rain-hair_ponytail', 'GEO-rain-hair_strand', 'GEO-rain-hairband']], ['teeth', ['GEO-rain-gums_upper', 'GEO-rain-gums_lower', 'GEO-rain-tongue']]]})
run('snow/Snow/snow_v4.2.blend', {'name': 'snow', 'head': 'GEO-snow-head', 'views': [],
    'parts': [['shirt', ['GEO-snow-shirt']], ['pants', ['GEO-snow-pants']], ['shoes', ['GEO-snow-shoes_base', 'GEO-snow-shoes_bottom', 'GEO-snow-shoes_parts']], ['hair', ['GEO-snow-hair_base']]]})
run('autumn/autumn/autumn.blend', {'name': 'autumn', 'head': 'GEO_autumn_body', 'views': ['body', 'bodytq']})
