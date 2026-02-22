# T7 - Brique merge SRT

## Objectif
Assembler les SRT produits par la transcription en un SRT final par audio, avec recalage temporel et renumerotation.

## Livrables
- `src/transcription/application/merge_use_case.py`
- `src/transcription/application/run_merge.py`
- CLI: ajout de `--step merge`

## Comportement
- Selectionne les audios avec `transcribed=true`.
- Lit les SRT depuis:
  - `<TRANSCRIPTION_ROOT>/<playlist_folder>/<audio_filename>/`
- Trie les fichiers SRT par numero de part (`_part_N`).
- Pour chaque fichier:
  - applique un offset `(part-1) * SEGMENT_LENGTH_SECONDS` sur les timestamps.
  - renumerote les entrees SRT globalement.
- Ecrit le resultat dans:
  - `<OUTPUT_ROOT>/<playlist_folder>/<audio_stem>_sous-titres_complets.srt`

## Notes
- Si aucun SRT n'est trouve pour un audio, le merge est ignore et logge.
- Le merge ne modifie pas l'etat CSV (pas de colonne supplementaire en V1).

## DoD T7
- ✅ Merge SRT implemente avec offset + renumerotation.
- ✅ `--step merge` expose via la CLI.
