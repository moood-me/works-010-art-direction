"""Edge loops of a quad mesh: the clean rings an artist laid round the eyes and the mouth."""
import numpy as np
from collections import defaultdict


class Quads:
    def __init__(self, P):
        self.P = [list(p) for p in P]
        self.ef = defaultdict(list); self.ve = defaultdict(set)
        for fi, p in enumerate(self.P):
            for k in range(len(p)):
                a, b = p[k], p[(k + 1) % len(p)]
                e = (min(a, b), max(a, b)); self.ef[e].append(fi); self.ve[a].add(e); self.ve[b].add(e)

    def next_edge(self, a, b):
        """the edge leaving b that continues a→b straight across a valence-4 vertex"""
        es = self.ve[b]
        if len(es) != 4: return None
        e0 = (min(a, b), max(a, b)); f0 = set(self.ef[e0])
        for e in es:
            if e == e0: continue
            if not (set(self.ef[e]) & f0): return e[0] if e[1] == b else e[1]
        return None

    def loop(self, a, b, maxn=400):
        L = [a, b]
        while len(L) < maxn:
            c = self.next_edge(L[-2], L[-1])
            if c is None: return L, False
            if c == L[0]: return L, True
            L.append(c)
        return L, False

    def neighbours(self, v):
        return [e[0] if e[1] == v else e[1] for e in self.ve[v]]
