# Heads: face mesh fitted to a drawn form

Each head drawn as one smooth solid read off its picture (`py/target.py`, numbers in `py/chars.py`), then Anny's head laid onto it (`py/build.py`): landmarks moved by one smooth warp, points put on the drawn surface and spread evenly; topology, bones and weights kept; lids and lip line cut along mesh edges. `py/fit.py` overlays the drawn outline and landmarks on each reference. State of work: 7 of 14 heads, none exact yet.
