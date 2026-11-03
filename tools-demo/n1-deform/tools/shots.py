# Writes the jobs for shot.mjs and puts the single shots together into the page's pictures.
# python shots.py jobs <set> > jobs.json ; node shot.mjs jobs.json ; python shots.py sheet <set>
import sys, json, os
from PIL import Image, ImageDraw, ImageFont
M, O, S = '/home/user/cache/n1-deform/mesh', '/home/user/cache/n1-deform/out', '/home/user/cache/n1-deform/shots'
PICS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pics')
TR = M + '/tris.i4'
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
def m(n): return f'{M}/{n}.f4'
def o(n): return f'{O}/{n}.f4'
SETS = {}
# rows of [mesh, label]; cam; size
FACE_CAM = {'yaw': 0.35, 'pitch': 0.03, 'dist': 0.95, 'target': [0.0, 1.655, 0.05]}
SETS['face'] = dict(w=340, h=400, cam=FACE_CAM, rows=[[(m('ft_disney'), 'исходное'), (m('ft_face_' + k), 'наше: ' + lab), (o('face_bih_' + k), 'libigl бигармон.'), (o('face_arap_' + k), 'libigl ARAP')] for k, lab in [('anime', 'аниме'), ('burton', 'Бёртон'), ('pixar', 'Pixar'), ('hero', 'герой')]])
SM = [(m('raw_woman'), 'исходное'), (m('ours_taubin'), 'наше старое (равномерное)'), (m('ours_cot_2'), 'наше: 2 см'), (o('mcf_2'), 'libigl MCF: 2 см'), (m('ours_cot_4'), 'наше: 4 см'), (o('mcf_4'), 'libigl MCF: 4 см')]
SETS['smooth'] = dict(w=330, h=560, rows=[SM, SM, SM], cams=[
    {'yaw': 0.25, 'pitch': 0.05, 'dist': 4.3, 'target': [0.0, 0.84, 0.0]},
    {'yaw': 0.3, 'pitch': 0.05, 'dist': 1.25, 'target': [0.0, 1.1, 0.05]},
    {'yaw': 0.45, 'pitch': 0.35, 'dist': 1.0, 'target': [0.06, 0.08, 0.06]}])
CG = [('hourglass', 'песочные часы'), ('pear', 'груша'), ('egg', 'яйцо'), ('wedge', 'клин')]
BODY = {'yaw': 0.3, 'pitch': 0.05, 'dist': 5.0, 'target': [0.0, 0.92, 0.0]}
SETS['cage'] = dict(w=330, h=560, cam=BODY, rows=[[(m('ft_disney'), 'исходное')] + [(m('ft_cage_' + k), 'наше: ' + l) for k, l in CG], [(m('ft_disney'), 'исходное')] + [(o('cage_bbw_' + k), 'libigl: ' + l) for k, l in CG]])
TORSO = {'yaw': 0.7, 'pitch': 0.1, 'dist': 2.3, 'target': [0.0, 1.15, 0.0]}
SETS['cage-close'] = dict(w=360, h=520, cam=TORSO, rows=[[(m('ft_cage_' + k), 'наше: ' + l), (o('cage_bbw_' + k), 'libigl: ' + l)] * 1 for k, l in [('wedge', 'клин'), ('hourglass', 'песочные часы')]])
SETS['cage-close']['rows'] = [SETS['cage-close']['rows'][0] + SETS['cage-close']['rows'][1]]
POSED = {'yaw': 0.0, 'pitch': 0.05, 'dist': 4.6, 'target': [0.0, 0.85, 0.0]}
ARMS = {'yaw': 0.5, 'pitch': 0.12, 'dist': 1.9, 'target': [0.12, 1.15, 0.0]}
KNEES = {'yaw': 0.3, 'pitch': 0.15, 'dist': 2.0, 'target': [0.0, 0.45, 0.0]}
AR = [(m('ln_base'), 'исходное'), (m('ln_arc1'), 'наше: дуга 1'), (o('arap_arc1'), 'ARAP: колено, локоть'), (o('arapR_arc1'), 'ARAP: по всей дуге'), (o('arapR_arc05'), 'ARAP по дуге: 0.5')]
SETS['arap'] = dict(w=330, h=540, rows=[AR, AR, AR], cams=[POSED, ARMS, KNEES])
# libigl in its own uses (uses.py)
FULL = {'yaw': 0.2, 'pitch': 0.05, 'dist': 5.2, 'target': [0.0, 0.95, 0.0]}
SETS['use-puppet'] = dict(w=380, h=600, cam=FULL, rows=[[(m('raw_woman'), 'исходное: булавки на стопах'), (o('use_naive'), 'просто гладко: тянется'), (o('use_arap'), 'ARAP: форма держится')]])
SETS['use-rig'] = dict(w=380, h=600, cam=FULL, rows=[[(m('raw_woman'), 'веса 11 ручек', o('use_bbw_colors')), (o('use_bbw_posed'), 'ручки повёрнуты', o('use_bbw_posed_colors')), (o('use_bbw_posed'), 'та же поза, без цвета')]])
HEAD = {'yaw': 0.45, 'pitch': 0.05, 'dist': 1.3, 'target': [0.0, 1.38, 0.03]}
SETS['use-denoise'] = dict(w=420, h=520, cam=HEAD, rows=[[(m('raw_woman'), 'исходное'), (o('use_noisy'), 'с шумом, как со сканера'), (o('use_denoised'), 'после сглаживания libigl')]])
SETS['use-geodesic'] = dict(w=380, h=600, rows=[[(m('raw_woman'), 'спереди', o('use_geo_colors')), (m('raw_woman'), 'сзади', o('use_geo_colors'))]], cams=[{'yaw': 0.3, 'pitch': 0.05, 'dist': 5.2, 'target': [0.0, 0.95, 0.0]}, {'yaw': 2.8, 'pitch': 0.05, 'dist': 5.2, 'target': [0.0, 0.95, 0.0]}])
def jobs(name):
    s = SETS[name]; out = []
    for r, row in enumerate(s['rows']):
        for c, (mesh, lab, *col) in enumerate(row):
            out.append({'out': f'{S}/{name}-{r}-{c}.png', 'tris': TR, 'meshes': [mesh], 'colors': [col[0] if col else None], 'w': s['w'], 'h': s['h'], 'cam': row_cam(s, r, c), 'gap': 0})
    return out
def row_cam(s, r, c):
    cams = s.get('cams')
    if not cams: return s['cam']
    return cams[r] if len(cams) == len(s['rows']) and len(s['rows']) > 1 else cams[c]
def sheet(name, fmt='webp'):
    s = SETS[name]; W, H = s['w'], s['h']; rows = s['rows']; cols = max(len(r) for r in rows); lh = 34
    im = Image.new('RGB', (W * cols, (H + lh) * len(rows)), '#f3efe8'); d = ImageDraw.Draw(im)
    for r, row in enumerate(rows):
        for c, (mesh, lab, *col) in enumerate(row):
            im.paste(Image.open(f'{S}/{name}-{r}-{c}.png').convert('RGB'), (c * W, r * (H + lh)))
            tw = d.textlength(lab, font=FONT); d.text((c * W + (W - tw) / 2, r * (H + lh) + H + 5), lab, fill='#2a2622', font=FONT)
    p = os.path.join(PICS, f'{name}.{fmt}'); im.save(p, quality=86); print(p, im.size)
if __name__ == '__main__':
    os.makedirs(S, exist_ok=True)
    if sys.argv[1] == 'jobs': print(json.dumps(jobs(sys.argv[2])))
    else: sheet(sys.argv[2])
