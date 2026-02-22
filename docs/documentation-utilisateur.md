# Documentation utilisateur

## Objectif
Ce projet automatise la transcription de videos YouTube (playlist) avec Whisper, en execution Colab, avec stockage sur Google Drive monte.

## Perimetre V1
- Source: playlist YouTube.
- Transcription: `openai-whisper`.
- Stockage: point de montage `/content/drive/...`.
- Configuration: `.env` + surcharge CLI.
- Hors perimetre: traduction.

## Prerequis
- Google Colab.
- Drive monte dans Colab.
- Python 3.10+.
- Outils systeme: `ffmpeg`.
- Dependances Python (a finaliser dans les prochains tickets): `python-dotenv`, `pytube`, `openai-whisper`.

Installation rapide:
```bash
pip install python-dotenv pytube
```

## Configuration
Les valeurs par defaut sont dans `src/transcription/config/settings.py`.

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
- `USE_MOCK`

## Utilisation CLI (etat actuel)
Point d'entree:
- `src/transcription/cli/main.py`

Commande type (depuis la racine du projet):
```bash
PYTHONPATH=src python -m transcription.cli.main \
  --step download \
  --playlist-csv /content/drive/MyDrive/Colab\ Notebooks/ressource/playlists.csv \
  --files-list-csv /content/drive/MyDrive/Colab\ Notebooks/ressource/files_list.csv
```

Commande type (robuste, meme hors racine du projet):
```bash
PYTHONPATH=/home/20104112/Documents/Perso/project/transcription/src \
/home/20104112/Documents/Perso/project/transcription/.venv/bin/python \
  -m transcription.cli.main \
  --step download \
  --playlist-csv "/content/drive/MyDrive/Colab Notebooks/ressource/playlists.csv" \
  --files-list-csv "/content/drive/MyDrive/Colab Notebooks/ressource/files_list.csv"
```

Important: au stade actuel (T6), les etapes `download`, `segment` et `transcribe` sont implementees.
Si `pytube` n'est pas installe, la CLI retourne une erreur explicite sur `download`.

## Workflow cible (une fois toutes les briques V1 terminees)
1. Download des medias de playlist.
2. Segmentation audio.
3. Transcription Whisper.
4. Fusion SRT.

## Segmentation (T5)
Commande:
```bash
PYTHONPATH=src python -m transcription.cli.main \
  --step segment \
  --files-list-csv "/content/drive/MyDrive/Colab Notebooks/ressource/files_list.csv" \
  --segmentation-root "/content/drive/MyDrive/Colab Notebooks/ressource/segmentation"
```

Prerequis systeme:
- `ffmpeg`
- `ffprobe`

Comportement:
- Segmente les fichiers audio `downloaded=true` et `segmented=false`.
- Met a jour l'etat CSV en `segmented=true` (audio et video associee si presente).

## Transcription (T6)
Commande:
```bash
PYTHONPATH=src python -m transcription.cli.main \
  --step transcribe \
  --files-list-csv "/content/drive/MyDrive/Colab Notebooks/ressource/files_list.csv" \
  --segmentation-root "/content/drive/MyDrive/Colab Notebooks/ressource/segmentation" \
  --transcription-root "/content/drive/MyDrive/Colab Notebooks/creation/transcription" \
  --whisper-model "large-v3-turbo" \
  --language "Arabic"
```

Prerequis:
- `whisper` installe en CLI (package `openai-whisper`).
- `ffmpeg` / `ffprobe` disponibles.

Comportement:
- Transcrit les segments audio issus de la segmentation.
- Si aucun segment n'est trouve, transcrit le fichier audio source.
- Met a jour l'etat CSV en `transcribed=true` (audio et video associee si presente).

## Tests
Commande:
```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Mesure de couverture (stdlib `trace`):
```bash
PYTHONPATH=src python -m trace --count --summary -C /tmp/tracecov --module unittest discover -s tests
```

Etat actuel: couverture superieure a 60% (mesure locale: modules `src/transcription/*` couverts a 100% par `trace`).

## Maintenance obligatoire de cette documentation
Cette page doit etre mise a jour a chaque ticket valide.

Checklist minimale par ticket:
- Ajouter ce qui change pour l'utilisateur (nouvelle commande, nouveau parametre, nouveau comportement).
- Mettre a jour les prerequis si necessaire.
- Mettre a jour la section "Utilisation CLI" avec un exemple executable.
- Preciser ce qui est operationnel vs en cours.

## Historique des mises a jour
- T3: ajout de la configuration `.env` + surcharge CLI, sans pipeline branche.
- T4: ajout de la brique download YouTube (`pytube`) avec reprise via `files_list.csv` et option CLI `--step download`.
- Etape qualite: ajout des tests unitaires et mesure de couverture >= 60%.
- T5: ajout de la brique segmentation audio (`ffmpeg`) avec option CLI `--step segment`.
- T6: ajout de la brique transcription Whisper avec option CLI `--step transcribe`.
