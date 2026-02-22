# T4 - Brique download YouTube

## Objectif
Implementer le telechargement audio/video depuis playlists YouTube avec persistance d'etat CSV pour reprise.

## Livrables
- `src/transcription/domain/interfaces/media_source.py`
- `src/transcription/domain/interfaces/state_repository.py`
- `src/transcription/domain/interfaces/logger.py`
- `src/transcription/domain/models/media.py`
- `src/transcription/infrastructure/sources/youtube_pytube_source.py`
- `src/transcription/infrastructure/state/csv_state_repository.py`
- `src/transcription/infrastructure/logging/file_logger.py`
- `src/transcription/application/download_use_case.py`
- `src/transcription/application/run_download.py`
- CLI branchee sur `--step download`

## Comportement
- Lit `PLAYLIST_CSV` (format: `playlist_url,playlist_title_optionnel`).
- Pour chaque video:
  - telecharge audio (`.m4a`) et video (`.mp4`) via `pytube`.
  - range dans:
    - `<AUDIO_BASE_PATH>/<playlist>/<playlist>-episode{n}.m4a`
    - `<VIDEO_BASE_PATH>/<playlist>/<playlist>-episode{n}.mp4`
- Met a jour `FILES_LIST_CSV` avec 4 colonnes:
  - `path,downloaded,segmented,transcribed`
- Reprise:
  - si etat `downloaded=true` pour audio+video et fichiers presents, la video est skippee.

## Limites connues
- Pas de retry reseau sur echec `pytube`.
- L'etape `download` est la seule active via CLI en T4.

## DoD T4
- ✅ Download audio/video implemente.
- ✅ Etat CSV implemente.
- ✅ Reprise via skip implemente.
