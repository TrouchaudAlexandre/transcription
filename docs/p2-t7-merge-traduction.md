# P2-T7 - Merge des SRT traduits

## Objectif
Generaliser la logique de merge pour produire aussi le sous-titre final dans la langue cible.

## Livrables
- generalisation de `MergeUseCase`
- `run_merge` execute deux passes :
  - merge source
  - merge traduit

## Comportement
- merge source :
  - lit dans `TRANSCRIPTION_ROOT`
  - produit `<audio_stem>_sous-titres_complets.srt`
- merge traduit :
  - lit dans `TRANSLATION_ROOT`
  - ne traite que les audios `translated=true`
  - produit `<audio_stem>_<target_language>_sous-titres_complets.srt`

## DoD
- ✅ deux SRT finaux produits
- ✅ logique de merge mutualisee
- ✅ tests ajoutes
