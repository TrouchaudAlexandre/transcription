# T5 - Brique segmentation audio

## Objectif
Implementer la segmentation audio via `ffmpeg` en se basant sur l'etat CSV et en permettant la reprise.

## Livrables
- `src/transcription/domain/interfaces/audio_segmenter.py`
- `src/transcription/infrastructure/segmentation/ffmpeg_segmenter.py`
- `src/transcription/application/segment_use_case.py`
- `src/transcription/application/run_segment.py`
- CLI: ajout de `--step segment`

## Comportement
- Selectionne uniquement les fichiers audio avec:
  - `downloaded=true`
  - `segmented=false`
  - extension audio supportee (`.mp3`, `.wav`, `.m4a`, `.flac`, `.aac`)
- Segmente avec `ffprobe` (duree) + `ffmpeg` (decoupage).
- Dossier de sortie:
  - `<SEGMENTATION_ROOT>/<playlist_folder>/<audio_filename>/`
- Nom des segments:
  - `<audio_stem>_part_<n><extension>`
- Met a jour `files_list.csv`:
  - audio segmente -> `segmented=true`
  - video associee (`.mp4`) segmentee aussi si presente dans l'etat

## Gestion d'erreur
- Si `ffmpeg`/`ffprobe` echoue, erreur loggee et traitement continue sur les autres fichiers.
- La CLI intercepte les erreurs subprocess et affiche un message actionnable.

## DoD T5
- ✅ Segmentation implementee via `ffmpeg`.
- ✅ Mise a jour d'etat CSV implementee.
- ✅ `--step segment` disponible en CLI.
