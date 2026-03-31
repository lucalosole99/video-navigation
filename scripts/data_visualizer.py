import cv2
import os
import numpy as np
from pathlib import Path
import random

class DatasetVisualizer:
    """
    Visualizza e analizza i frame estratti dal dataset.
    """
    
    def __init__(self, frames_dir="data/processed/frames"):
        """
        Inizializza il visualizzatore.
        
        Args:
            frames_dir: Directory con i frame estratti
        """
        self.frames_dir = frames_dir
        
    def get_dataset_stats(self):
        """
        Ottiene statistiche complete sul dataset.
        
        Returns:
            Dictionary con statistiche
        """
        if not os.path.exists(self.frames_dir):
            print(f"✗ Directory {self.frames_dir} non trovata!")
            return None
        
        stats = {
            "total_videos": 0,
            "total_frames": 0,
            "videos": {}
        }
        
        # Analizza ogni sottocartella (video)
        for video_dir in Path(self.frames_dir).iterdir():
            if video_dir.is_dir():
                video_name = video_dir.name
                frames = list(video_dir.glob("*.jpg")) + list(video_dir.glob("*.png"))
                
                if frames:
                    # Leggi un frame per ottenere risoluzione
                    sample_frame = cv2.imread(str(frames[0]))
                    height, width = sample_frame.shape[:2]
                    
                    stats["videos"][video_name] = {
                        "num_frames": len(frames),
                        "resolution": (width, height),
                        "path": str(video_dir)
                    }
                    
                    stats["total_videos"] += 1
                    stats["total_frames"] += len(frames)
        
        return stats
    
    def print_stats(self):
        """Stampa statistiche del dataset in modo leggibile."""
        stats = self.get_dataset_stats()
        
        if not stats:
            return
        
        print("\n" + "="*70)
        print("STATISTICHE DATASET")
        print("="*70)
        print(f"Directory: {self.frames_dir}")
        print(f"Video totali: {stats['total_videos']}")
        print(f"Frame totali: {stats['total_frames']}")
        print("\nDettaglio per video:")
        print("-"*70)
        
        for video_name, info in stats["videos"].items():
            print(f"\n📹 {video_name}")
            print(f"   Frame: {info['num_frames']}")
            print(f"   Risoluzione: {info['resolution'][0]}x{info['resolution'][1]}")
            print(f"   Path: {info['path']}")
        
        print("\n" + "="*70)
    
    def create_grid(self, images, grid_size=None, max_images=16):
        """
        Crea una griglia di immagini.
        
        Args:
            images: Lista di immagini (array numpy)
            grid_size: Tupla (rows, cols), se None calcola automaticamente
            max_images: Numero massimo di immagini da mostrare
            
        Returns:
            Immagine griglia
        """
        if not images:
            return None
        
        # Limita numero immagini
        images = images[:max_images]
        n_images = len(images)
        
        # Calcola dimensioni griglia
        if grid_size is None:
            cols = int(np.ceil(np.sqrt(n_images)))
            rows = int(np.ceil(n_images / cols))
        else:
            rows, cols = grid_size
        
        # Dimensioni target per ogni immagine
        target_h, target_w = 300, 400
        
        # Resize tutte le immagini alle stesse dimensioni
        resized_images = []
        for img in images:
            resized = cv2.resize(img, (target_w, target_h))
            resized_images.append(resized)
        
        # Riempie con immagini nere se necessario
        while len(resized_images) < rows * cols:
            black_img = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            resized_images.append(black_img)
        
        # Crea la griglia
        grid_rows = []
        for i in range(rows):
            row_images = resized_images[i*cols:(i+1)*cols]
            grid_row = np.hstack(row_images)
            grid_rows.append(grid_row)
        
        grid = np.vstack(grid_rows)
        
        return grid
    
    def visualize_video_frames(self, video_name, max_frames=16):
        """
        Visualizza i frame di un singolo video in griglia.
        
        Args:
            video_name: Nome della cartella video
            max_frames: Massimo numero di frame da visualizzare
        """
        video_path = Path(self.frames_dir) / video_name
        
        if not video_path.exists():
            print(f"✗ Video {video_name} non trovato!")
            return
        
        # Carica tutti i frame
        frame_files = sorted(video_path.glob("*.jpg")) + sorted(video_path.glob("*.png"))
        
        if not frame_files:
            print(f"✗ Nessun frame trovato in {video_name}")
            return
        
        # Se ci sono più frame del massimo, prendine un subset uniforme
        if len(frame_files) > max_frames:
            indices = np.linspace(0, len(frame_files)-1, max_frames, dtype=int)
            frame_files = [frame_files[i] for i in indices]
        
        # Carica le immagini
        images = []
        for frame_file in frame_files:
            img = cv2.imread(str(frame_file))
            # Aggiungi numero frame sull'immagine
            frame_num = frame_file.stem.split('_')[-1]
            cv2.putText(img, f"Frame {frame_num}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            images.append(img)
        
        # Crea griglia
        grid = self.create_grid(images, max_images=max_frames)
        
        if grid is not None:
            # Ridimensiona per fit sullo schermo
            screen_h, screen_w = 900, 1600
            h, w = grid.shape[:2]
            if h > screen_h or w > screen_w:
                scale = min(screen_h/h, screen_w/w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                grid = cv2.resize(grid, (new_w, new_h))
            
            print(f"\n📹 Visualizzando: {video_name}")
            print(f"   Frame mostrati: {len(images)}/{len(frame_files)}")
            print("   Premi qualsiasi tasto per continuare...")
            
            cv2.imshow(f'Dataset Preview - {video_name}', grid)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    
    def visualize_all_videos(self, max_frames_per_video=9):
        """
        Visualizza frame da tutti i video del dataset.
        
        Args:
            max_frames_per_video: Frame da mostrare per ogni video
        """
        stats = self.get_dataset_stats()
        
        if not stats or stats["total_videos"] == 0:
            print("✗ Nessun video nel dataset!")
            return
        
        print(f"\n📺 Visualizzazione di tutti i video ({stats['total_videos']})")
        print("   Premi qualsiasi tasto per passare al video successivo...")
        print("   Premi 'q' per uscire")
        
        for video_name in stats["videos"].keys():
            self.visualize_video_frames(video_name, max_frames=max_frames_per_video)
            
            # Controlla se l'utente vuole uscire
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        cv2.destroyAllWindows()
        print("\n✓ Visualizzazione completata")
    
    def visualize_random_samples(self, n_samples=16):
        """
        Visualizza sample random dall'intero dataset.
        
        Args:
            n_samples: Numero di frame casuali da mostrare
        """
        stats = self.get_dataset_stats()
        
        if not stats or stats["total_frames"] == 0:
            print("✗ Nessun frame nel dataset!")
            return
        
        # Raccogli tutti i path dei frame
        all_frames = []
        for video_name, info in stats["videos"].items():
            video_path = Path(info["path"])
            frames = list(video_path.glob("*.jpg")) + list(video_path.glob("*.png"))
            all_frames.extend(frames)
        
        # Seleziona sample casuali
        n_samples = min(n_samples, len(all_frames))
        random_frames = random.sample(all_frames, n_samples)
        
        # Carica immagini
        images = []
        for frame_path in random_frames:
            img = cv2.imread(str(frame_path))
            # Aggiungi info sull'immagine
            video_name = frame_path.parent.name
            frame_num = frame_path.stem.split('_')[-1]
            cv2.putText(img, f"{video_name}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, f"F:{frame_num}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            images.append(img)
        
        # Crea griglia
        grid = self.create_grid(images, max_images=n_samples)
        
        if grid is not None:
            # Ridimensiona per fit sullo schermo
            screen_h, screen_w = 900, 1600
            h, w = grid.shape[:2]
            if h > screen_h or w > screen_w:
                scale = min(screen_h/h, screen_w/w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                grid = cv2.resize(grid, (new_w, new_h))
            
            print(f"\n🎲 Sample casuali: {n_samples} frame")
            print("   Premi qualsiasi tasto per chiudere...")
            
            cv2.imshow('Random Dataset Samples', grid)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    
    def compare_frame_intervals(self, video_name, frame_nums):
        """
        Confronta frame specifici per valutare il sampling.
        
        Args:
            video_name: Nome del video
            frame_nums: Lista di numeri di frame da confrontare
        """
        video_path = Path(self.frames_dir) / video_name
        
        if not video_path.exists():
            print(f"✗ Video {video_name} non trovato!")
            return
        
        images = []
        for frame_num in frame_nums:
            frame_file = video_path / f"frame_{frame_num:06d}.jpg"
            if not frame_file.exists():
                frame_file = video_path / f"frame_{frame_num:06d}.png"
            
            if frame_file.exists():
                img = cv2.imread(str(frame_file))
                cv2.putText(img, f"Frame {frame_num}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                images.append(img)
        
        if not images:
            print(f"✗ Frame non trovati!")
            return
        
        # Mostra in orizzontale
        comparison = np.hstack(images)
        
        # Ridimensiona se troppo grande
        h, w = comparison.shape[:2]
        if w > 1600:
            scale = 1600 / w
            new_w = 1600
            new_h = int(h * scale)
            comparison = cv2.resize(comparison, (new_w, new_h))
        
        print(f"\n🔍 Confronto frame: {frame_nums}")
        print("   Valuta se il sampling cattura abbastanza dettagli")
        print("   Premi qualsiasi tasto per chiudere...")
        
        cv2.imshow('Frame Comparison', comparison)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    """Menu interattivo per la visualizzazione."""
    
    print("\n" + "="*70)
    print("DATASET VISUALIZER - Analisi Frame Estratti")
    print("="*70)
    
    visualizer = DatasetVisualizer()
    
    while True:
        print("\nModalità disponibili:")
        print("1. Statistiche dataset")
        print("2. Visualizza tutti i video (griglia)")
        print("3. Visualizza video specifico")
        print("4. Sample casuali dall'intero dataset")
        print("5. Confronta frame consecutivi (valuta sampling)")
        print("0. Esci")
        
        choice = input("\nScelta: ")
        
        if choice == "1":
            visualizer.print_stats()
        
        elif choice == "2":
            max_frames = input("Frame per video [default=9]: ")
            max_frames = int(max_frames) if max_frames else 9
            visualizer.visualize_all_videos(max_frames_per_video=max_frames)
        
        elif choice == "3":
            stats = visualizer.get_dataset_stats()
            if stats and stats["total_videos"] > 0:
                print("\nVideo disponibili:")
                for i, video_name in enumerate(stats["videos"].keys(), 1):
                    print(f"  {i}. {video_name}")
                
                video_name = input("\nNome video: ")
                max_frames = input("Max frame da mostrare [default=16]: ")
                max_frames = int(max_frames) if max_frames else 16
                
                visualizer.visualize_video_frames(video_name, max_frames=max_frames)
        
        elif choice == "4":
            n_samples = input("Numero di sample [default=16]: ")
            n_samples = int(n_samples) if n_samples else 16
            visualizer.visualize_random_samples(n_samples=n_samples)
        
        elif choice == "5":
            stats = visualizer.get_dataset_stats()
            if stats and stats["total_videos"] > 0:
                print("\nVideo disponibili:")
                for i, video_name in enumerate(stats["videos"].keys(), 1):
                    print(f"  {i}. {video_name}")
                
                video_name = input("\nNome video: ")
                print("Inserisci numeri frame da confrontare (es: 0 5 10)")
                frame_nums = input("Frame: ")
                frame_nums = [int(x) for x in frame_nums.split()]
                
                visualizer.compare_frame_intervals(video_name, frame_nums)
        
        elif choice == "0":
            print("\n👋 Arrivederci!")
            break
        
        else:
            print("Scelta non valida!")


if __name__ == "__main__":
    main()