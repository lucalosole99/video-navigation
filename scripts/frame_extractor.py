import cv2
import os
import sys
from pathlib import Path
from datetime import datetime

class FrameExtractor:
    """
    Estrae frame singoli da video per creare un dataset statico.
    """
    
    def __init__(self, data_root="data", input_subdir="personal_dataset"):
        """
        Inizializza l'estrattore.
        
        Args:
            data_root: Directory radice del progetto (default: "data")
            input_subdir: Sottocartella in raw/ con i video (default: "personal_dataset")
        """
        self.data_root = data_root
        self.input_subdir = input_subdir
        self.raw_dir = f"{data_root}/raw/{input_subdir}"
        self.frames_dir = f"{data_root}/processed/frames"
        
        self.create_directories()
    
    
    def create_directories(self):
        """Crea le directory necessarie se non esistono."""
        import os
        
        # Stampa directory corrente di lavoro
        print(f"\n[DEBUG] Directory corrente: {os.getcwd()}")
        print(f"[DEBUG] Cerco video in: {self.raw_dir}")
        print(f"[DEBUG] Salverò frame in: {self.frames_dir}")
        
        # Verifica esistenza directory input
        if not os.path.exists(self.raw_dir):
            print(f"\n⚠️  ATTENZIONE: {self.raw_dir} non esiste!")
            print(f"   Creala con: mkdir -p {self.raw_dir}")
        else:
            print(f"✓ Directory input trovata: {self.raw_dir}")
        
        # Crea directory output
        Path(self.frames_dir).mkdir(parents=True, exist_ok=True)
        print(f"✓ Directory frames pronta: {self.frames_dir}")
    
    def get_video_info(self, video_path):
        """
        Ottiene informazioni sul video.
        
        Args:
            video_path: Percorso del video
            
        Returns:
            Dictionary con info o None se errore
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        info = {
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        return info
    
    def extract_frames(self, video_path, frame_interval=30, resize=None, 
                      max_frames=None, output_subdir=None):
        """
        Estrae frame dal video.
        
        Args:
            video_path: Percorso del video (può essere assoluto o relativo)
            frame_interval: Estrae 1 frame ogni N frame (default=30, circa 1/sec a 30fps)
            resize: Tupla (width, height) per resize, None mantiene dimensione originale
            max_frames: Numero massimo di frame da estrarre, None per tutti
            output_subdir: Sottocartella opzionale in frames/ (es. nome video)
            
        Returns:
            Dictionary con statistiche dell'estrazione
        """
        # Verifica esistenza file
        if not os.path.exists(video_path):
            print(f"Errore: file {video_path} non trovato!")
            return None
        
        # Ottieni info video
        info = self.get_video_info(video_path)
        if not info:
            print(f"Errore: impossibile aprire {video_path}")
            return None
        
        # Nome del video (senza estensione)
        video_name = Path(video_path).stem
        
        # Determina directory di output
        if output_subdir:
            output_dir = f"{self.frames_dir}/{output_subdir}"
        else:
            output_dir = f"{self.frames_dir}/{video_name}"
        
        # Pulisci la directory se esiste già (evita mix di frame vecchi e nuovi)
        if os.path.exists(output_dir):
            import shutil
            print(f"\n La cartella {output_dir} esiste già.")
            overwrite = input("Vuoi sovrascrivere? (s/n) [default=s]: ").lower()
            if overwrite == 'n':
                print("Estrazione annullata.")
                return None
            else:
                shutil.rmtree(output_dir)
                print(f"✓ Cartella precedente rimossa.")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Mostra informazioni
        print("\n" + "="*70)
        print(f"ESTRAZIONE FRAME: {video_name}")
        print("="*70)
        print(f"Video sorgente:      {video_path}")
        print(f"Output directory:    {output_dir}")
        print(f"Risoluzione:         {info['width']}x{info['height']}")
        print(f"FPS:                 {info['fps']:.2f}")
        print(f"Frame totali:        {info['total_frames']}")
        print(f"Durata:              {info['duration']:.2f} secondi")
        print(f"Intervallo:          1 frame ogni {frame_interval} frame")
        if resize:
            print(f"Resize a:            {resize[0]}x{resize[1]}")
        if max_frames:
            print(f"Limite frame:        {max_frames}")
        print("="*70)
        
        # Apri video
        cap = cv2.VideoCapture(video_path)
        
        frame_count = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Verifica limite massimo
            if max_frames and saved_count >= max_frames:
                break
            
            # Estrai solo ogni N frame
            if frame_count % frame_interval == 0:
                # Resize se richiesto
                if resize:
                    frame_resized = cv2.resize(frame, resize)
                else:
                    frame_resized = frame
                
                # Nome file con padding
                filename = f"{output_dir}/frame_{saved_count:06d}.jpg"
                
                # Salva frame con qualità alta
                cv2.imwrite(filename, frame_resized, [cv2.IMWRITE_JPEG_QUALITY, 95])
                saved_count += 1
                
                # Progresso ogni 50 frame
                if saved_count % 50 == 0:
                    percentage = (frame_count / info['total_frames']) * 100
                    print(f"Progresso: {saved_count} frame salvati ({percentage:.1f}% video processato)")
            
            frame_count += 1
        
        cap.release()
        
        # Statistiche finali
        stats = {
            "video_name": video_name,
            "video_path": video_path,
            "output_dir": output_dir,
            "original_resolution": [info['width'], info['height']],
            "resize": list(resize) if resize else None,
            "original_fps": info['fps'],
            "total_video_frames": info['total_frames'],
            "frame_interval": frame_interval,
            "frames_extracted": saved_count,
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        print("\n" + "="*70)
        print("✓ ESTRAZIONE COMPLETATA")
        print("="*70)
        print(f"Frame estratti:      {saved_count}")
        print(f"Frame processati:    {frame_count}/{info['total_frames']}")
        print(f"Directory output:    {output_dir}")
        print("="*70)
        
        return stats
    
    def batch_extract(self, video_list, **kwargs):
        """
        Estrae frame da una lista di video.
        
        Args:
            video_list: Lista di percorsi video
            **kwargs: Parametri da passare a extract_frames()
            
        Returns:
            Lista di statistiche per ogni video
        """
        results = []
        
        print(f"\n{'='*70}")
        print(f"BATCH EXTRACTION: {len(video_list)} video")
        print(f"{'='*70}")
        
        for i, video_path in enumerate(video_list, 1):
            print(f"\n[{i}/{len(video_list)}] Processando: {Path(video_path).name}")
            stats = self.extract_frames(video_path, **kwargs)
            if stats:
                results.append(stats)
        
        print(f"\n{'='*70}")
        print("✓ BATCH EXTRACTION COMPLETATA")
        print(f"{'='*70}")
        print(f"Video processati:    {len(results)}/{len(video_list)}")
        print(f"Frame totali:        {sum(s['frames_extracted'] for s in results)}")
        print(f"{'='*70}")
        
        return results


def main():
    """Funzione principale con interfaccia utente."""
    
    print("\n" + "="*70)
    print("FRAME EXTRACTOR - Progetto Navigazione Assistita")
    print("="*70)
    
    extractor = FrameExtractor()
    
    # Modalità di utilizzo
    print("\nModalità disponibili:")
    print("1. Estrai frame da un singolo video")
    print("2. Estrai frame da tutti i video in data/raw/personal_dataset/")
    
    choice = input("\nScelta (1/2): ")
    
    if choice == "1":
        # Singolo video
        if len(sys.argv) > 1:
            video_path = sys.argv[1]
        else:
            video_path = input("\nPercorso del video: ")
        
        # Configurazione
        print("\n--- Configurazione Estrazione ---")
        frame_interval = input("Intervallo frame (1=tutti, 30≈1/sec) [default=30]: ")
        frame_interval = int(frame_interval) if frame_interval else 30
        
        resize_choice = input("Vuoi fare resize? (s/n) [default=n]: ").lower()
        resize = None
        if resize_choice == 's':
            width = int(input("  Larghezza [default=640]: ") or "640")
            height = int(input("  Altezza [default=480]: ") or "480")
            resize = (width, height)
        
        max_frames = input("Max frame da estrarre [default=tutti]: ")
        max_frames = int(max_frames) if max_frames else None
        
        # Estrazione
        extractor.extract_frames(
            video_path,
            frame_interval=frame_interval,
            resize=resize,
            max_frames=max_frames
        )
    
    elif choice == "2":
        # Batch da data/raw/personal_dataset
        raw_dir = extractor.raw_dir
        
        if not os.path.exists(raw_dir):
            print(f" Directory {raw_dir} non trovata!")
            print(f"  Assicurati che esista: data/raw/personal_dataset/")
            return
        
        # Trova tutti i video
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.MP4', '.AVI', '.MOV']
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(Path(raw_dir).glob(f"*{ext}"))
        
        # Rimuovi duplicati (Windows non è case-sensitive)
        video_files = list(set(video_files))
        video_files.sort()  # Ordina per consistenza
        
        if not video_files:
            print(f"✗ Nessun video trovato in {raw_dir}")
            return
        
        print(f"\nTrovati {len(video_files)} video:")
        for i, vf in enumerate(video_files, 1):
            print(f"  {i}. {vf.name}")
        
        # Configurazione
        print("\n--- Configurazione Batch ---")
        frame_interval = input("Intervallo frame [default=30]: ")
        frame_interval = int(frame_interval) if frame_interval else 30
        
        resize_choice = input("Resize? (s/n) [default=n]: ").lower()
        resize = None
        if resize_choice == 's':
            width = int(input("  Larghezza [default=640]: ") or "640")
            height = int(input("  Altezza [default=480]: ") or "480")
            resize = (width, height)
        
        max_frames = input("Max frame per video [default=tutti]: ")
        max_frames = int(max_frames) if max_frames else None
        
        # Estrazione batch
        extractor.batch_extract(
            [str(vf) for vf in video_files],
            frame_interval=frame_interval,
            resize=resize,
            max_frames=max_frames
        )
    
    else:
        print("Scelta non valida!")


if __name__ == "__main__":
    main()