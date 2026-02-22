# T6 - Brique transcription Whisper

## Objectif
Implementer la transcription via `openai-whisper` (CLI) sur les segments issus de T5, avec mise a jour de l'etat CSV.

## Livrables
- `src/transcription/domain/interfaces/transcription_engine.py`
- `src/transcription/infrastructure/transcription/whisper_engine.py`
- `src/transcription/application/transcribe_use_case.py`
- `src/transcription/application/run_transcribe.py`
- CLI: ajout de `--step transcribe`

## Comportement
- Selectionne uniquement les fichiers audio avec:
  - `downloaded=true`
  - `segmented=true`
  - `transcribed=false`
- Recherche d'abord les segments dans:
  - `<SEGMENTATION_ROOT>/<playlist_folder>/<audio_filename>/`
- Si segments presents: transcription de chaque segment (sequentielle).
- Sinon: transcription du fichier audio source (fallback).
- Sortie Whisper dans:
  - `<TRANSCRIPTION_ROOT>/<playlist_folder>/<audio_filename>/`
- Mise a jour `files_list.csv`:
  - audio transcrit -> `transcribed=true`
  - video associee (`.mp4`) transcrite aussi si presente dans l'etat.

## Gestion d'erreur
- Si `whisper` echoue, erreur loggee et traitement continue sur les autres fichiers.
- La CLI intercepte:
  - `FileNotFoundError` (commande manquante)
  - `CalledProcessError` (echec subprocess)

## DoD T6
- ✅ Transcription Whisper implementee.
- ✅ Mise a jour `transcribed=true` dans l'etat CSV.
- ✅ `--step transcribe` disponible en CLI.
