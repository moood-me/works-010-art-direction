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
    mel = st['melanin']
    mat = S.hair_material('hair', mel[0], mel[1], S.srgb(mel[2]) if len(mel) > 2 else None, rough=st.get('rough', 0.25))
    hairs = []
    for k, part in enumerate(st['parts']):
        p = {**st, **part}
        sc = S.scalp(R, c, r, st['line'], p.get('region'), name=f'scalp-{k}')
        g = S.guides_object(f'hair-{k}', p['guides'], sc)
        g.data.materials.append(mat)
        S.gn(g, 'Interpolate Hair Curves', Surface=sc, Surface_UV_Map=('attr', 'UVMap'), Part_by_Mesh_Islands=False,
             Interpolation_Guides=p.get('guides_k', 4), Density=p.get('density', 1500000), Seed=3 + k)
        S.gn(g, 'Clump Hair Curves', Existing_Guide_Map=False, Guide_Distance=p.get('clump', 0.04), Factor=p.get('clump_f', 1.0),
             Shape=p.get('clump_shape', 0.4), Tip_Spread=p.get('tip_spread', 0.003), Preserve_Length=True, Seed=1 + k)
        S.gn(g, 'Clump Hair Curves', Existing_Guide_Map=False, Guide_Distance=p.get('clump2', 0.012), Factor=p.get('clump2_f', 0.5),
             Shape=0.1, Tip_Spread=0.0005, Preserve_Length=True, Seed=2 + k)
        if p.get('noise'): S.gn(g, 'Hair Curves Noise', Distance=p['noise'], Scale=40.0, Shape=0.3, Seed=4)
        for on in p.get('shrink_on', []):
            S.gn(g, 'Shrinkwrap Hair Curves', Surface=bpy.data.objects[on], Offset_Distance=p.get('shrink', 0.006),
                 Above_Surface=0.5, Smoothing_Steps=3, Lock_Roots=True)
        S.gn(g, 'Smooth Hair Curves', Amount=0.6, Iterations=6, Preserve_Length=True)
        S.gn(g, 'Set Hair Curve Profile', Radius=p.get('radius', 0.0011), Shape=p.get('profile', 0.3))
        hairs.append(g)
    if 'tie' in st:   # the hair tie: a plain torus
        T = S.bl(st['tie']); d = S.bl(st['tie_dir'])
        bpy.ops.mesh.primitive_torus_add(major_radius=0.016, minor_radius=0.006, location=tuple(T))
        tie = bpy.context.active_object; tie.name = 'tie'
        tie.rotation_euler = S.Vector(tuple(d)).to_track_quat('Z', 'Y').to_euler()
        tie.data.materials.append(S.principled('tie', S.srgb(0x2a2228), 0.4))
        for p in tie.data.polygons: p.use_smooth = True
    return dict(st=st, R=R, body=body, hairs=hairs, c=c, r=r, ey=ey, who=who)

WHO = {'gwen': 'woman', 'alva': 'woman', 'kpony': 'woman', 'kbraid': 'woman', 'marco': 'child', 'jack': 'man'}

if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:]
    name, out = argv[0], argv[1]
    views = {'front': -0.55, 'back': math.pi - 0.55}
    H = make(name)
    co = S.stage(samples=int(argv[2]) if len(argv) > 2 else 48)
    head = np.asarray(H['R']['head'])
    ev = bpy.context.evaluated_depsgraph_get()
    print('strands', sum(len(h.evaluated_get(ev).data.curves) for h in H['hairs']))
    for v, yaw in views.items():
        S.look(co, head - np.array([0, 0.03, 0]), yaw, 0.06, H['st']['dist'])
        bpy.context.scene.render.filepath = f'{out}/{name}-{v}.png'
        bpy.ops.render.render(write_still=True)
    if len(argv) > 3: bpy.ops.wm.save_as_mainfile(filepath=argv[3])
