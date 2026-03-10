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
- Dependances Python (a finaliser dans les prochains tickets): `python-dotenv`, `yt-dlp`, `openai-whisper`.

Installation rapide:
```bash
pip install python-dotenv yt-dlp
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
- `TRANSLATION_CONTEXT`
- `TRANSLATION_PROMPT_VERSION`
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

Important: au stade actuel, les etapes `download`, `segment`, `transcribe` et `merge` sont implementees.
Si `yt-dlp` n'est pas installe, la CLI retourne une erreur explicite sur `download`.
Les parametres de traduction sont exposes en configuration pour preparer la phase 2, mais l'etape `translate` n'est pas encore implementee.
`WHISPER_LANGUAGE` reste la langue source de reference pour la future traduction.
Le CSV d'etat est en cours d'evolution phase 2 pour ajouter le suivi global `translated` tout en restant compatible avec les anciens fichiers.
Le moteur GPT de traduction est maintenant present dans le code, mais pas encore branche dans la CLI.
Le moteur de traduction est pense pour etre interchangeable par provider via une factory (`openai` pour l'instant, extensible ensuite a `mistral`, `gemini`, etc.).
La future traduction pourra etre contextualisee avec `SOURCE_VARIANT` (ex: `tunisian_arabic`) et `TRANSLATION_CONTEXT`.
La traduction valide maintenant la structure SRT avant d'accepter un segment traduit.

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
- Journalise chaque segment individuellement (`start`, `done`, `skip`, `failed`).
- En cas d'echec partiel, les segments deja transcrits sont detectes et skippes au relancement.

## Merge SRT (T7)
Commande:
```bash
PYTHONPATH=src python -m transcription.cli.main \
  --step merge \
  --files-list-csv "/content/drive/MyDrive/Colab Notebooks/ressource/files_list.csv" \
  --transcription-root "/content/drive/MyDrive/Colab Notebooks/creation/transcription" \
  --output-root "/content/drive/MyDrive/Colab Notebooks/creation/resultat" \
  --segment-length-seconds 60
```

Comportement:
- Trie les `.srt` par `part_n`.
- Recale les timestamps avec l'offset de segment (`segment_length_seconds`).
- Renumerote les entrees.
- Produit un fichier final par audio:
  - `<OUTPUT_ROOT>/<playlist>/<audio_stem>_sous-titres_complets.srt`

## Runner Colab (T8)
Un runner minimal en 2 cellules est disponible ici:
- `colab/runner-colab.md`

Etapes:
1. Cellule 1: monte Drive, clone le repo, installe dependances.
2. Cellule 2: copie `.env.example` vers `.env`, puis execute `download -> segment -> transcribe -> merge`.

Fichier de configuration type:
- `.env.example`

## Documentation principale
Le guide principal d'utilisation est maintenant dans:
- `README.md`

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
- T4: ajout de la brique download YouTube (`yt-dlp`) avec reprise via `files_list.csv` et option CLI `--step download`.
- Etape qualite: ajout des tests unitaires et mesure de couverture >= 60%.
- T5: ajout de la brique segmentation audio (`ffmpeg`) avec option CLI `--step segment`.
- T6: ajout de la brique transcription Whisper avec option CLI `--step transcribe`.
- T7: ajout de la brique merge SRT avec option CLI `--step merge`.
- T8: ajout du runner Colab minimal et du fichier `.env.example`.
- T9: ajout de `README.md` avec guide complet d'utilisation (local + Colab + troubleshooting).
- P2-T2: ajout des parametres de configuration necessaires a la future brique de traduction.
- P2-T4: ajout de l'interface de traduction et du moteur OpenAI/GPT, non encore branche a une etape CLI.
- P2-T5: ajout de la brique `translate` avec reprise par segment, provider configurable, `SOURCE_VARIANT` et `TRANSLATION_CONTEXT`.
- P2-T6: ajout d'une validation deterministe du format SRT traduit avant acceptation d'un segment.
