# What Blender's hair node groups do by themselves: one patch of scalp, the same nine guide curves, and on top of
# Interpolate Hair Curves one more node group each (Clump, Curl, Frizz, Braid, Noise). Then a realistic groom (the use
# they are mostly made for) of Alva's hairstyle: thin strands, many of them, frizz and noise, less clumping.
# blender -b --factory-startup -P uses.py -- <out dir> patches|real
import bpy, sys, math
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import scene as S

argv = sys.argv[sys.argv.index('--') + 1:]
out, what = argv[0], argv[1]

def patch(x, extra, title):
    me = bpy.data.meshes.new('p'); s = 0.035
    me.from_pydata([(x - s, -s, 0), (x + s, -s, 0), (x + s, s, 0), (x - s, s, 0)], [], [(0, 1, 2, 3)])
    me.uv_layers.new(name='UVMap')
    p = bpy.data.objects.new('patch', me); bpy.context.scene.collection.objects.link(p)
    p.data.materials.append(S.principled('skin', S.srgb(0xf0c8b0), 0.6))
    G = []
    for i in range(3):
        for j in range(3):
            r = np.array([x + (i - 1) * 0.022, (j - 1) * 0.022, 0.0])
            G.append(np.array([r + [0.012 * t * t, 0, 0.22 * t] for t in np.linspace(0, 1, 24)]))
    G = [np.stack([g[:, 0], g[:, 2], -g[:, 1]], -1) for g in G]   # (written in three's axes, as guides_object wants)
    h = S.guides_object('hair', G, p)
    h.data.materials.append(MAT)
    S.gn(h, 'Interpolate Hair Curves', Surface=p, Surface_UV_Map=('attr', 'UVMap'), Part_by_Mesh_Islands=False, Density=60000.0)
    for g, kw in extra: S.gn(h, g, **kw)
    S.gn(h, 'Set Hair Curve Profile', Radius=0.0006, Shape=0.3)

S.reset()
if what == 'patches':
    MAT = S.hair_material('hair', 0.55, 0.55)
    V = [([], 'Interpolate'),
         ([('Clump Hair Curves', dict(Existing_Guide_Map=False, Guide_Distance=0.03, Shape=0.3, Preserve_Length=True))], 'Clump'),
         ([('Curl Hair Curves', dict(Existing_Guide_Map=False, Guide_Distance=0.03, Radius=0.012, Frequency=6.0, Curl_Start=0.15))], 'Curl'),
         ([('Frizz Hair Curves', dict(Distance=0.01, Shape=0.4))], 'Frizz'),
         ([('Braid Hair Curves', dict(Existing_Guide_Map=False, Guide_Distance=0.2, Radius=0.012, Frequency=1.5, Braid_Start=0.1, Thickness=0.8))], 'Braid'),
         ([('Hair Curves Noise', dict(Distance=0.02, Scale=4.0, Shape=0.4))], 'Noise')]
    for k, (ex, t) in enumerate(V): patch(k * 0.13, ex, t)
    co = S.stage(res=(1300, 420), samples=16)
    bpy.data.objects['ground'].hide_render = True
    co.data.type = 'ORTHO'; co.data.ortho_scale = 0.8
    co.location = (0.325, -1.2, 0.12); co.rotation_euler = (math.radians(88), 0, 0)
    bpy.context.scene.render.filepath = f'{out}/use-nodes.png'; bpy.ops.render.render(write_still=True)
