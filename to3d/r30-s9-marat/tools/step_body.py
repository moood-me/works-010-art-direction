"""A step picture's model: Anny's man as it is, and fitted (clay)."""
import numpy as np
from common import load_body, CACHE
from model import part, write
B = load_body('moood-man')
fit = np.load(f'{CACHE}/body_fit.npz')
write('step-anny', [part(B['positions'], B['triangles'], B['sj'], B['sw'], 'clay')], B['joints'], B['frames'])
write('step-fit', [part(fit['V'], B['triangles'], B['sj'], B['sw'], 'clay')], fit['J'], B['frames'])
