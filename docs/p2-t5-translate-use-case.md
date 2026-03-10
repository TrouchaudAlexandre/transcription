# P2-T5 - Brique translate

## Objectif
Traduire les segments SRT source deja produits par la transcription, avec reprise fine par segment et mise a jour du suivi global `translated`.

## Livrables
- `src/transcription/application/translate_use_case.py`
- `src/transcription/application/run_translate.py`
- branchement CLI sur `--step translate`
- tests de use case et de wiring

## Comportement
- selectionne les audios eligibles :
  - `downloaded=true`
  - `segmented=true`
  - `transcribed=true`
  - `translated=false`
- lit les segments SRT source depuis :
  - `TRANSCRIPTION_ROOT/<playlist>/<audio_filename>/`
- ecrit les segments traduits dans :
  - `TRANSLATION_ROOT/<playlist>/<audio_filename>/`
- skippe un segment deja traduit si le fichier de sortie existe deja
- marque `translated=true` uniquement si tous les segments sont correctement produits

## Parametrage de contexte
- langue source : `WHISPER_LANGUAGE`
- variante source : `SOURCE_VARIANT`
- langue cible : `TARGET_LANGUAGE`
- contexte libre : `TRANSLATION_CONTEXT`

## Limites a ce stade
- pas encore de validation structurelle stricte du SRT traduit
- pas encore de merge final des sous-titres traduits

## DoD
- ✅ `--step translate` disponible
- ✅ reprise par segment implemente
- ✅ mise a jour `translated=true` implemente
