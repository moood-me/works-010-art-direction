"""Run run_stdgen.py on each argument separately, so one failure doesn't stop the rest."""
import subprocess, sys
for a in sys.argv[1:]:
    r = subprocess.run([sys.executable, 'run_stdgen.py', a], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    print(a, 'OK' if r.returncode == 0 else 'FAILED', lines[-1] if lines else '', flush=True)
