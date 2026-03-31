# Navigazione Assistita da Video – Progetto di Tesi

## Obiettivo del progetto
L’obiettivo di questo progetto è sviluppare un sistema di **visione artificiale basato su Deep Learning** in grado di analizzare **sequenze video** (non singole immagini) per:

- comprendere la dinamica della scena
- individuare le aree percorribili (free-space)
- stimare un percorso sicuro tenendo conto di ostacoli e contesto ambientale

Il progetto è pensato per **esecuzione su dispositivi edge** (es. wearable o single-board computer), privilegiando soluzioni leggere ed efficienti.

---

## Stato attuale del progetto
**Setup e strumenti di base (completata)**

- Ambiente di sviluppo configurato con Conda (Python 3.10)
- Struttura del progetto definita
- Script OpenCV per:
  - lettura di video
  - visualizzazione frame
  - overlay di informazioni temporali
  - salvataggio di frame e video annotati
- Versionamento Git inizializzato

Il codice attuale serve come strumento di debug e ispezione dei dati video per le fasi successive.

---

## Requisiti
- Python 3.10
- Conda / Miniconda
- Sistema operativo: Windows (sviluppo), portabile su Linux

---

## Setup dell’ambiente

Per eseguire lo script è necessario installare Conda o Miniconda e creare l'ambiente.

**Creazione dell’ambiente Conda**:

conda env create -f environment.yml
conda activate video_nav

**Utilizzo dello script video**:

python scripts/read_video.py



