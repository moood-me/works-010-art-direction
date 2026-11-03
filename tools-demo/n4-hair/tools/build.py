# One hairstyle on its body, built with Blender's hair node groups (Essentials asset library, Blender 4.5).
import bpy, sys, math
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import scene as S
from styles import STYLES

def make(name, motion_body=False):
    S.reset()
    who = WHO[name]
    import json
    R = json.load(open(f'{S.CACHE}/bodies/{who}-rest.json'))
    c, r, ey = S.skull(R)
    st = STYLES[name](c, r, ey)
    R, body, garments = S.person(who, st['skin'])
    sc = S.scalp(R, c, r, st['line'])
    g = S.guides_object('hair', st['guides'], sc)
    g.data.materials.append(S.hair_material('hair', S.srgb(st['color']), S.srgb(st.get('tip', st['color'])), rough=st.get('rough', 0.3)))
    S.gn(g, 'Interpolate Hair Curves', Surface=sc, Surface_UV_Map=('attr', 'UVMap'), Part_by_Mesh_Islands=False,
         Interpolation_Guides=st.get('guides_k', 4), Density=st['density'], Seed=3)
    S.gn(g, 'Clump Hair Curves', Existing_Guide_Map=False, Guide_Distance=st['clump'], Factor=st.get('clump_f', 0.95),
         Shape=st.get('clump_shape', 0.35), Tip_Spread=st.get('tip_spread', 0.0015), Preserve_Length=True, Seed=1)
    S.gn(g, 'Clump Hair Curves', Existing_Guide_Map=False, Guide_Distance=st['clump2'], Factor=st.get('clump2_f', 0.6), Shape=0.1,
         Tip_Spread=0.0005, Preserve_Length=True, Seed=2)
    if st.get('noise'): S.gn(g, 'Hair Curves Noise', Distance=st['noise'], Scale=40.0, Shape=0.3, Seed=4)
    if st.get('shrink'):
        S.gn(g, 'Shrinkwrap Hair Curves', Surface=st.get('shrink_on') and bpy.data.objects[st['shrink_on']] or body,
             Offset_Distance=st['shrink'], Above_Surface=0.5, Smoothing_Steps=3, Lock_Roots=True)
    S.gn(g, 'Smooth Hair Curves', Amount=0.6, Iterations=6, Preserve_Length=True)
    S.gn(g, 'Set Hair Curve Profile', Radius=st['radius'], Shape=st.get('profile', 0.3))
    for o in st.get('extra', []): o(R, c, r, ey)
    return dict(st=st, R=R, body=body, hair=g, scalp=sc, c=c, r=r, ey=ey, who=who)

WHO = {'gwen': 'woman', 'alva': 'woman', 'kpony': 'woman', 'kbraid': 'woman', 'marco': 'child', 'jack': 'man'}

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:]
    name, out = argv[0], argv[1]
    views = {'front': -0.55, 'back': math.pi - 0.55}
    H = make(name)
    co = S.stage(samples=int(argv[2]) if len(argv) > 2 else 48)
    head = np.asarray(H['R']['head'])
    ev = bpy.context.evaluated_depsgraph_get()
    print('strands', len(H['hair'].evaluated_get(ev).data.curves))
    for v, yaw in views.items():
        S.look(co, head - np.array([0, 0.03, 0]), yaw, 0.06, H['st']['dist'])
        bpy.context.scene.render.filepath = f'{out}/{name}-{v}.png'
        bpy.ops.render.render(write_still=True)
    if len(argv) > 3: bpy.ops.wm.save_as_mainfile(filepath=argv[3])
