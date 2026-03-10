# P2-T9 - Finalisation documentation et tests

## Objectif
Clore la phase 2 avec une documentation coherente, exploitable et alignee sur l'etat reel du code.

## Livrables
- mise a jour de `README.md`
- mise a jour de `docs/documentation-utilisateur.md`
- verification de la suite de tests complete

## Points couverts
- pipeline complet : `download -> segment -> transcribe -> translate -> merge`
- nouveaux parametres de traduction :
  - `SOURCE_VARIANT`
  - `TARGET_LANGUAGE`
  - `TRANSLATION_PROVIDER`
  - `TRANSLATION_MODEL`
  - `TRANSLATION_API_KEY`
  - `TRANSLATION_CONTEXT`
- comportement de reprise sur traduction
- production des deux SRT finaux
- prerequis `openai`

## DoD
- ✅ documentation synchronisee avec le code
- ✅ tests verts
