import torch, anny, time
t=time.time()
m = anny.Anny(phenotypes="all", local_changes="default")
print('load', time.time()-t)
print(m.phenotype_labels)
lc = m.local_change_labels if hasattr(m,'local_change_labels') else None
print(type(lc), len(lc) if lc else None)
print(list(lc)[:400] if lc else [a for a in dir(m) if 'local' in a])
print(m.template_vertices.shape, m.faces.shape)
