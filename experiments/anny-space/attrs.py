import torch, anny
m = anny.Anny(phenotypes="all", local_changes="default", extrapolate_phenotypes=True)
for k,v in m.named_buffers():
    if v.dim()>0 and v.shape[0] in (13718,) or 'weight' in k or 'bone' in k: print(k, tuple(v.shape))
print(getattr(m,'bone_labels',None))
