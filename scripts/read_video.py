import cv2
import sys
from pathlib import Path
from datetime import datetime


def read_video(video_path: str, save_annotated: bool = False, loop: bool = True):
    """
    Legge e visualizza un video con OpenCV.
    Controlli:
    - SPAZIO: Pausa/Play
    - Q o ESC: Esci
    - S: Salva frame corrente (in outputs/frames/)
    """

    # --- Percorsi progetto ---
    project_root = Path(__file__).resolve().parents[1]
    outputs_dir = project_root / "outputs"
    frames_dir = outputs_dir / "frames"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Risolvi path video (accetta anche relativo)
    video_path = Path(video_path)
    if not video_path.is_absolute():
        # prova relativo alla root progetto
        candidate = project_root / video_path
        if candidate.exists():
            video_path = candidate

    if not video_path.exists():
        print(f"Errore: file video non trovato: {video_path}")
        return False

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Errore: impossibile aprire il video {video_path}")
        return False

    # Info video
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 0
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0

    fontScale = max(0.8, width / 1500)        # 3840 -> ~2.56
    thickness = max(2, int(width / 1000))     # 3840 -> 3


    # Fallback FPS se non valido
    if not fps or fps <= 0:
        fps = 25.0  # fallback ragionevole su Windows

    duration_sec = (total_frames / fps) if total_frames > 0 else 0.0

    print("=" * 60)
    print("INFORMAZIONI VIDEO")
    print("=" * 60)
    print(f"Path: {video_path}")
    print(f"Risoluzione: {width}x{height}")
    print(f"FPS: {fps:.2f}")
    print(f"Frame totali: {total_frames if total_frames > 0 else 'N/D'}")
    if duration_sec > 0:
        print(f"Durata: {duration_sec:.2f} secondi")
    else:
        print("Durata: N/D")
    print("=" * 60)
    print("\nControlli:")
    print("- SPAZIO: Pausa/Play")
    print("- Q o ESC: Esci")
    print("- S: Salva frame corrente (in outputs/frames/)")
    print("=" * 60)

    # Output video annotato (opzionale)
    writer = None
    out_path = None
    if save_annotated and width > 0 and height > 0:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = outputs_dir / f"annotated_{ts}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # generalmente OK su Windows
        writer = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))
        if not writer.isOpened():
            print("[WARN] Impossibile creare VideoWriter. Continuo senza salvare il video annotato.")
            writer = None
            out_path = None

    frame_count = 0
    paused = False
    last_frame = None  # per poter salvare frame anche in pausa

    window_name = "Video Test - Navigazione Assistita"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 960, 540)


    while True:
        if not paused:
            ret, frame = cap.read()

            if not ret:
                if loop:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    frame_count = 0
                    continue
                else:
                    break

            frame_count += 1
            last_frame = frame
        else:
            # in pausa mostriamo l'ultimo frame valido
            if last_frame is None:
                # pausa premuta prima di leggere un frame: leggi il primo
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1
                last_frame = frame

            frame = last_frame

        # Overlay informazioni
        info_frame = frame.copy()

        if total_frames > 0:
            cv2.putText(
                info_frame,
                f"Frame: {frame_count}/{total_frames}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                fontScale,
                (0, 255, 0),
                thickness,
                cv2.LINE_AA,
            )
        else:
            cv2.putText(
                info_frame,
                f"Frame: {frame_count}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                fontScale,
                (0, 255, 0),
                thickness,
                cv2.LINE_AA,
            )

        cv2.putText(
            info_frame,
            f"Time: {frame_count / fps:.2f}s",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale,
            (0, 255, 0),
            thickness,
            cv2.LINE_AA,
        )

        if paused:
            cv2.putText(
                info_frame,
                "PAUSED",
                (max(10, width // 2 - 90), max(40, height // 2)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 0, 255),
                3,
                cv2.LINE_AA,
            )

        # Mostra il frame
        cv2.imshow(window_name, info_frame)

        # Salva video annotato (solo se non in errore)
        if writer is not None:
            writer.write(info_frame)

        # Gestione input tastiera
        wait_ms = int(1000 / fps) if not paused else 0
        key = cv2.waitKey(wait_ms) & 0xFF

        if key == ord("q") or key == 27:  # Q o ESC
            break
        elif key == ord(" "):  # SPAZIO
            paused = not paused
            print("Pausa" if paused else "Riproduzione")
        elif key == ord("s"):  # S
            if last_frame is None:
                print("[WARN] Nessun frame disponibile da salvare.")
                continue
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = frames_dir / f"frame_{frame_count:06d}_{ts}.jpg"
            cv2.imwrite(str(filename), last_frame)
            print(f"Frame salvato: {filename}")

    # Cleanup
    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()


    print("\nVideo chiuso correttamente.")
    if out_path is not None:
        print(f"✅ Video annotato salvato in: {out_path}")
    
    return True


if __name__ == "__main__":
    print("Test OpenCV per progetto Navigazione Assistita")
    print("=" * 50)

    while True:
        video_path = input("\nInserisci il percorso del video (o 'q' per uscire): ").strip()
        if video_path.lower() == "q":
            break

        ok = read_video(video_path)
        if ok:
            break  # video gestito correttamente, esci
        else:
            print("Percorso non valido o video non apribile. Riprova.")
