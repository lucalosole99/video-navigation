import argparse
from pathlib import Path
import csv
import cv2

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}

def video_info(path: Path):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration_s = (frame_count / fps) if fps > 0 else 0.0
    cap.release()
    return fps, frame_count, w, h, duration_s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw_root", default="data/raw")
    ap.add_argument("--out_csv", default="data/processed/metadata/videos.csv")
    args = ap.parse_args()

    PROJECT_ROOT = Path(__file__).resolve().parents[1]  # .../video-navigation
    raw_root = PROJECT_ROOT / "data" / "raw"
    out_csv = Path(args.out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    if not raw_root.exists():
        raise FileNotFoundError(f"raw_root not found: {raw_root.resolve()}")

    videos = [p for p in raw_root.rglob("*")
              if p.is_file() and p.suffix.lower() in VIDEO_EXTS]
    videos.sort()

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["dataset", "relpath", "fps", "frames", "width", "height", "duration_s"])
        for v in videos:
            info = video_info(v)
            if info is None:
                print(f"WARNING: cannot open {v}")
                continue
            # dataset = prima cartella sotto raw_root
            rel = v.relative_to(raw_root)
            dataset = rel.parts[0] if len(rel.parts) > 0 else ""
            fps, frames, w, h, dur = info
            wr.writerow([dataset, rel.as_posix(), f"{fps:.3f}", frames, w, h, f"{dur:.3f}"])

    print(f"Scanned {len(videos)} video(s)")
    print(f"Wrote: {out_csv.resolve()}")

if __name__ == "__main__":
    main()