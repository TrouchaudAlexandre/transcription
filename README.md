# Transcription Pipeline V1

Pipeline Python pour transcrire des playlists YouTube avec Whisper, execute principalement sur Google Colab avec stockage sur Google Drive monte.

## Perimetre V1
- Source: YouTube playlists (`pytube`).
- Segmentation: `ffmpeg` / `ffprobe`.
- Transcription: `openai-whisper` (CLI `whisper`).
- Merge SRT: fusion + recalage temporel + renumerotation.
- Etat: CSV `path,downloaded,segmented,transcribed`.

## Arborescence utile
- Code: `src/transcription/`
- Runner Colab: `colab/runner-colab.md`
- Config exemple: `.env.example`
- Documentation utilisateur: `docs/documentation-utilisateur.md`

## Prerequis
### Local
- Python 3.10+
- `ffmpeg` et `ffprobe` dans `PATH`
- Dependance Python:
  - `python-dotenv`
  - `pytube`
  - `openai-whisper`

Installation rapide:
```bash
python -m pip install --upgrade pip
python -m pip install python-dotenv pytube openai-whisper
```

### Colab
Utiliser `colab/runner-colab.md` (2 cellules).

## Configuration
1. Copier l'exemple:
```bash
cp .env.example .env
```
2. Adapter les chemins dans `.env`.

Variables principales:
- `PLAYLIST_CSV`
- `FILES_LIST_CSV`
- `LOG_PATH`
- `AUDIO_BASE_PATH`
- `VIDEO_BASE_PATH`
- `SEGMENTATION_ROOT`
- `TRANSCRIPTION_ROOT`
- `OUTPUT_ROOT`
- `SEGMENT_LENGTH_SECONDS`
- `WHISPER_MODEL`
- `WHISPER_LANGUAGE`

## Format attendu de `PLAYLIST_CSV`
Chaque ligne:
```csv
playlist_url,playlist_title_optionnel
```
Exemple:
```csv
https://www.youtube.com/playlist?list=XXXX,ma_playlist
```

## Execution
Depuis la racine du repo:

### 1) Download
```bash
PYTHONPATH=src python -m transcription.cli.main --step download
```

### 2) Segment
```bash
PYTHONPATH=src python -m transcription.cli.main --step segment
```

### 3) Transcribe
```bash
PYTHONPATH=src python -m transcription.cli.main --step transcribe
```

### 4) Merge
```bash
PYTHONPATH=src python -m transcription.cli.main --step merge
```

## Sorties
- Audio/Video telecharges:
  - `<AUDIO_BASE_PATH>/<playlist>/<playlist>-episodeN.m4a`
  - `<VIDEO_BASE_PATH>/<playlist>/<playlist>-episodeN.mp4`
- Segments audio:
  - `<SEGMENTATION_ROOT>/<playlist>/<audio_filename>/<audio_stem>_part_N.ext`
- Transcriptions brutes (whisper):
  - `<TRANSCRIPTION_ROOT>/<playlist>/<audio_filename>/`
- SRT fusionne:
  - `<OUTPUT_ROOT>/<playlist>/<audio_stem>_sous-titres_complets.srt`
- Etat:
  - `FILES_LIST_CSV`

## Reprise et idempotence
- `download` skippe les fichiers deja telecharges (etat + presence disque).
- `segment` traite seulement `downloaded=true` et `segmented=false`.
- `transcribe` traite seulement `segmented=true` et `transcribed=false`.
- `merge` lit les SRT disponibles; pas d'etat supplementaire en V1.

## Tests
Lancer tous les tests:
```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Depannage
- `Runtime error: pytube is required...`
  - Installer: `pip install pytube`
- `Subprocess failed ... ffmpeg`
  - Installer `ffmpeg` / `ffprobe`
- `Command not found: whisper`
  - Installer `openai-whisper`
- `shell-init: error retrieving current directory` en Colab
  - Cause: suppression de `/content/transcription` alors que la session est deja dans ce dossier.
  - Fix: faire `os.chdir("/content")` avant de supprimer/recloner le projet (deja gere dans `colab/runner-colab.md`).

## Limites V1
- Transcription sequentielle (pas de parallelisme).
- Pas de brique traduction.
- Pas de stockage Drive API (montage Drive uniquement).
