"""A UV sphere (for the eyeballs and quick looks)."""
import numpy as np


def sphere(c, r, n=24, m=None):
    m = m or 2 * n
    th = np.linspace(0, np.pi, n); ph = np.linspace(0, 2 * np.pi, m, endpoint=False)
    X = np.array([[np.sin(t) * np.cos(p), np.cos(t), np.sin(t) * np.sin(p)] for t in th for p in ph]) * r + c
    F = []
    for i in range(n - 1):
        for j in range(m):
            a, b = i * m + j, i * m + (j + 1) % m
            F += [(a, b, a + m), (b, b + m, a + m)]
    return X, np.array(F)
