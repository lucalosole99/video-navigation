# Copilot Instructions for video-navigation

- This repo is an early-stage video dataset tooling project, not a full ML model service.
- Primary code lives in `scripts/`; there is no package build system or test framework present.
- Use `environment.yml` as the authoritative dependency source. The project expects Python 3.10 and a Conda environment.

## Project structure

- `scripts/read_video.py` - interactive OpenCV video preview and frame saving tool. Saves snapshots to `outputs/frames/`.
- `scripts/frame_extractor.py` - frame extraction CLI for a single video or batch from `data/raw/personal_dataset/`. Writes to `data/processed/frames/<video_name>/`.
- `scripts/dataset_report.py` - scans `data/raw/` for videos and writes metadata CSV to `data/processed/metadata/videos.csv`.
- `scripts/data_visualizer.py` - inspects extracted image data in `data/processed/frames/` and displays grids or random samples.
- `data/raw/` stores source videos; `data/processed/frames/` stores extracted image datasets.

## Workflow notes

- Setup with Conda:
  - `conda env create -f environment.yml`
  - `conda activate video_nav`
- Run tools from repository root.
- `scripts/` scripts are interactive and expect console input; preserve the interactive menu style when editing.

## Important conventions

- Path handling is project-root centric: scripts resolve `Path(__file__).resolve().parents[1]`.
- `frame_extractor.py` treats video sources under `data/raw/personal_dataset/` and outputs frame folders under `data/processed/frames/`.
- `dataset_report.py` uses `raw_root = PROJECT_ROOT / "data" / "raw"` and writes `data/processed/metadata/videos.csv`.
- `data_visualizer.py` expects each video to be a subfolder in `data/processed/frames/` containing `.jpg` or `.png` frames.
- The codebase uses OpenCV for all image/video I/O and display, with `cv2.waitKey()` to handle keyboard interaction.

## What to avoid

- Do not invent a build/test system; there are no existing scripts or configs for CI / unit tests.
- Do not assume a packaging layer such as `setup.py` or `pyproject.toml` exists.
- Keep changes aligned with current exploratory/data-inspection tooling rather than introducing a production service architecture.

## Helpful examples

- Use `python scripts/read_video.py` to verify video loading and frame overlay behavior.
- Use `python scripts/frame_extractor.py` to validate dataset extraction semantics and output folder naming.
- Use `python scripts/dataset_report.py --out_csv data/processed/metadata/videos.csv` to refresh metadata after adding new raw videos.
- Use `python scripts/data_visualizer.py` to inspect dataset structure and sample frames visually.

## Known limitations

- No automated tests or CI configuration exist in this repository.
- All scripts are interactive CLI tools, so changes should preserve user prompts and keyboard-driven flow.
- There is no packaging layer (`setup.py`, `pyproject.toml`, or `requirements.txt`); dependency management is via `environment.yml`.
- The code is focused on data inspection and frame extraction, not on production model serving or training pipelines.
