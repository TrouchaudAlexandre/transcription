# Transcription Pipeline

Pipeline Python pour transcrire et traduire des playlists YouTube, execute principalement sur Google Colab avec stockage sur Google Drive monte.

## Perimetre actuel
- Source: YouTube playlists (`yt-dlp`).
- Segmentation: `ffmpeg` / `ffprobe`.
- Transcription: `openai-whisper` (CLI `whisper`).
- Traduction: provider configurable, implementations `openai` et `gemini` disponibles.
- Merge SRT: fusion + recalage temporel + renumerotation.
- Etat: CSV `path,downloaded,segmented,transcribed,translated`.

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
  - `yt-dlp`
  - `openai-whisper`
  - `openai`
  - `google-genai` pour Gemini

Installation rapide:
```bash
python -m pip install --upgrade pip
python -m pip install python-dotenv yt-dlp openai-whisper openai google-genai
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
- `TRANSLATION_ROOT`
- `OUTPUT_ROOT`
- `SEGMENT_LENGTH_SECONDS`
- `WHISPER_MODEL`
- `WHISPER_LANGUAGE`
- `SOURCE_VARIANT`
- `TARGET_LANGUAGE`
- `TRANSLATION_PROVIDER`
- `TRANSLATION_MODEL`
- `TRANSLATION_API_KEY`
- `TRANSLATION_MAX_RETRIES`
- `TRANSLATION_RETRY_BASE_DELAY_SECONDS`
- `TRANSLATION_CONTEXT`
- `TRANSLATION_PROMPT_VERSION`

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

Logs:
- progression par segment (`start`, `done`, `skip`, `failed`)
- relance possible sans retraiter les segments deja transcrits

### 4) Translate
```bash
PYTHONPATH=src python -m transcription.cli.main --step translate
```

Notes:
- utilise `WHISPER_LANGUAGE` comme langue source generale
- utilise `SOURCE_VARIANT` pour preciser un dialecte, par exemple `tunisian_arabic`
- utilise `TRANSLATION_CONTEXT` pour injecter du contexte metier/culturel libre
- par defaut, la traduction utilise `gemini-2.5-flash-lite`
- les appels retry uniquement sur erreurs transitoires (`429`, `408`, `409`, `5xx`, timeout/connexion)
- `TRANSLATION_PROVIDER` accepte `openai` et `gemini`
- le preset par defaut vise le free tier Gemini
- pour un mode qualite OpenAI, utiliser `TRANSLATION_PROVIDER=openai` et `TRANSLATION_MODEL=gpt-5-mini`

### 5) Merge
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
- Traductions segmentaires:
  - `<TRANSLATION_ROOT>/<playlist>/<audio_filename>/`
- SRT fusionnes:
  - `<OUTPUT_ROOT>/<playlist>/<audio_stem>_sous-titres_complets.srt`
  - `<OUTPUT_ROOT>/<playlist>/<audio_stem>_<target_language>_sous-titres_complets.srt`
- Etat:
  - `FILES_LIST_CSV`

## Reprise et idempotence
- `download` skippe les fichiers deja telecharges (etat + presence disque).
- `segment` traite seulement `downloaded=true` et `segmented=false`.
- `transcribe` traite seulement `segmented=true` et `transcribed=false`.
- `translate` traite seulement `transcribed=true` et `translated=false`.
- `merge` produit le SRT source et, si disponible, le SRT traduit.

## Tests
Lancer tous les tests:
```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Depannage
- `Runtime error: yt-dlp is required...`
  - Installer: `pip install yt-dlp`
- `Subprocess failed ... ffmpeg`
  - Installer `ffmpeg` / `ffprobe`
- `Command not found: whisper`
  - Installer `openai-whisper`
- `Runtime error: openai package is required for GPT translation`
  - Installer `openai`
- `Runtime error: google-genai package is required for Gemini translation`
  - Installer `google-genai`
- `shell-init: error retrieving current directory` en Colab
  - Cause: suppression de `/content/transcription` alors que la session est deja dans ce dossier.
  - Fix: faire `os.chdir("/content")` avant de supprimer/recloner le projet (deja gere dans `colab/runner-colab.md`).

## Limites actuelles
- Transcription et traduction sequentielles.
- Providers de traduction disponibles: `openai`, `gemini`.
- Pas de stockage Drive API (montage Drive uniquement).
