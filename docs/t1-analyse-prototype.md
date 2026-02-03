# T1 — Analyse du prototype `transcriptionauto.py`

## Étapes fonctionnelles observées

1) **Configuration / variables globales**
- Chemins Google Drive (logs, CSV, audio, vidéo, output).
- Flags : `isMockActive`, `segment_length_sec`, modèles Whisper.

2) **Téléchargement YouTube (pytube)**
- Lecture d’un CSV `playlists.csv` : chaque ligne = `playlist_url, playlist_title?`.
- Pour chaque playlist :
  - Récupère la liste des URLs vidéos.
  - Télécharge **audio** (`.m4a`) + **vidéo** (`.mp4`).
- Stocke dans :
  - `audio_base_path/<playlist_title>/<playlist_title>-episode{index}.m4a`
  - `video_base_path/<playlist_title>/<playlist_title>-episode{index}.mp4`
- **État CSV** `files_list.csv` : lignes `[path, downloaded, segmented, transcribed]`.
  - `write_to_file()` crée/maj la ligne.
- **Logs** : `log.txt` avec timestamp.

3) **Segmentation audio (ffmpeg)**
- `ffprobe` lit la durée du fichier audio.
- Découpe par segments de `segment_length_sec` (60s).
- Sorties : `segmentation/<last_folder_name>/<fileName>/<fileName>_part_{n}.m4a`
- Update état CSV : `segmented=true` pour audio + vidéo associée.
- Logs : `log_segmentation.txt`.

4) **Transcription Whisper (CLI)**
- Installe `openai-whisper`.
- `transcribe_audio_shell()` exécute :
  - `whisper <file> --language Arabic --model large-v3-turbo --output_dir <output>`
- Logs par fichier : `log_file_<segment>.txt`.
- Mode mock : transcrit un sous-ensemble de segments.

5) **Regroupement SRT**
- Parcourt les `.srt` par ordre de `part_n`.
- Décale les timestamps par offset (multiple de `segment_length_sec`).
- Rénumérote toutes les entrées.
- Écrit un fichier final : `<fileName>sous-titres_complets.srt`.

## Comportement à conserver en V1
- Chemins Drive par défaut identiques.
- Téléchargement audio+vidéo via `pytube`.
- CSV d’état `files_list.csv`.
- Segmentation via `ffmpeg`.
- Transcription via `openai-whisper` CLI.
- Merge SRT (offset + renumérotation).
- Logs séparés (global + segmentation + transcription par segment).

## Points sensibles / à stabiliser
- `pytube` peut être fragile.
- Les flags CSV sont en `true/false` (string), parfois `TRUE` (incohérence).
- Le lien audio/vidéo est basé sur remplacement d’extension.
- Gestion d’erreur simple (log + CSV).

## DoD T1
- ✅ Fonctionnalités listées.
- ✅ Comportement à conserver explicité.
