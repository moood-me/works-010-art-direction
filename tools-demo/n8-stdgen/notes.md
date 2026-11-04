# Н8 — StdGEN: 3D from one picture

**What and why.** Н5 found StdGEN (He et al., CVPR 2025; code and weights Apache-2.0, github.com/hyz317/StdGEN,
huggingface.co/hyz317/StdGEN) but could not run it: it needs an NVIDIA GPU. Pavel gave a Hugging Face token and
asked to run it on a budget GPU there, briefly, with auto-sleep, and paused afterwards; then to run one figure from
each style of `styles/`.

**How, to repeat it.**
- The authors' Space `hyz317/StdGEN` was duplicated (private) to `completelyreal/StdGEN` through the Hub API
  (`POST /api/spaces/hyz317/StdGEN/duplicate` with hardware and `sleepTimeSeconds: 300`).
- Two fixes to the copy so it starts today: `python_version: "3.10"` in its README (its wheels are cp310; the Hub now
  defaults to 3.13) and `pydantic==2.10.6` in requirements.txt (gradio 5.20 breaks on newer pydantic).
- Hardware: L4 (24 GB) ran out of memory at reconstruction (needs ~11 GB more); L40S had no capacity; A100 (80 GB)
  worked. About 3 minutes per picture after the models load (~15 minutes after each start).
- `tools/run_stdgen.py name…` (gradio_client, token from a local `.env` outside the repository) runs the four stages
  on `in/<name>.png` and saves the A-pose, six views and the meshes; `tools/turn.py` (Blender 4.5, Cycles CPU) renders
  the whole refined mesh from four sides; `tools/all.sh` does all and tiles the sheets.
- Afterwards the Space was paused (`POST /api/spaces/completelyreal/StdGEN/pause`).

**Seen.** Shape from all sides guessed right; body, clothes, hair separate; but blotchy colour, holes in sleeves,
smeared faces, a bald back of the head on Тим. The symbolic silhouette (С6) failed at reconstruction (empty mesh).

**Second try (Pavel: if the five are poor, try to fix one or two before running the rest).** Tim and Anya (С1) re-rendered from their SVG with the background removed, cropped to a white square like the authors' examples, run with seeds 52/50 and 7/11. Anya improved (whole hair, fewer holes); Tim kept a bald, blotchy back of the head. Not good enough to call good 3D, so the remaining styles were not run. The Space is paused.

**Normal mode on the remaining seven styles (Pavel: see how the model does without per-character fixes).** One figure per style С6–С12, background removed for all by rembg (isnet-general-use) and put into a white square; `run_many.py` runs them one by one so a failure doesn't stop the rest. All seven reconstructed; С11's rubber-hose Tim lost his legs, С6's silhouette gives nothing to build. The Space was paused after.
