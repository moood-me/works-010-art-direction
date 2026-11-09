"""check_four — after a change in the shared code: draw every picture of the first four again (SVG only, in a
temporary folder) and compare with svg/. Prints the names that differ; nothing in svg/ or pics/ is touched.

    python3 tools/check_four.py
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
subprocess.run = lambda *a, **k: None      # no rendering
import build

NEW = ("marat", "kira", "cast6")
kept = build.SVG
build.SVG = tempfile.mkdtemp()
bad = []
for k, fn in build.JOBS.items():
    if any(n in k for n in NEW):
        continue
    fn()
    with open(os.path.join(build.SVG, k + ".svg")) as a, open(os.path.join(kept, k + ".svg")) as b:
        if a.read() != b.read():
            bad.append(k)
print("changed:", ", ".join(bad) if bad else "nothing — the four are as they were")
sys.exit(1 if bad else 0)
