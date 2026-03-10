# Phase 2 - Architecture traduction

## Extension du pipeline
Pipeline cible apres phase 2 :
1. download
2. segment
3. transcribe
4. translate
5. merge-source
6. merge-translated

## Nouvelles briques

### Domaine
- `domain/interfaces/translation_engine.py`
- optionnel si necessaire :
  - `domain/interfaces/srt_validator.py`

### Application
- `application/translate_use_case.py`
- `application/run_translate.py`
- evolution de `merge_use_case.py` pour permettre :
  - merge source
  - merge traduit

### Infrastructure
- `infrastructure/translation/openai_translation_engine.py`
- `infrastructure/validation/srt_validator.py` si on extrait un validateur concret

## Responsabilites recommandees

### `TranslateUseCase`
- selectionne les audios eligibles :
  - `transcribed=true`
  - `translated=false`
- localise les segments SRT source
- traduit chaque segment unitairement
- valide le format du segment traduit
- journalise chaque segment
- marque `translated=true` seulement si tous les segments sont valides

### `TranslationEngine`
- recoit un segment SRT
- produit un segment SRT traduit
- n'applique aucune logique metier de reprise ou de validation globale

### `SrtValidator`
- verifie la conformite du fichier traduit par rapport au segment source
- doit rester deterministe en V1

### `MergeUseCase`
- doit etre generalise pour travailler sur une racine configurable
- permet de fusionner :
  - les SRT source
  - les SRT traduits

## Reuse de l'existant
- Reprendre le pattern de `TranscribeUseCase` :
  - traitement par segment
  - skip des artefacts deja presentes
  - reprise apres echec partiel
- Reprendre la logique de `MergeUseCase` pour la fusion finale
- Etendre `CsvStateRepository` pour lire/ecrire la colonne `translated`

## Evolution du CSV d'etat
Etat actuel :
- `path`
- `downloaded`
- `segmented`
- `transcribed`

Etat cible :
- `path`
- `downloaded`
- `segmented`
- `transcribed`
- `translated`

## Decision sur le multi-agent
- Architecture non multi-agent en phase 2.
- Justification :
  - la valeur principale est dans la robustesse du pipeline, pas dans l'orchestration de plusieurs LLM
  - la validation de format doit etre non-LLM
  - un second agent de verification serait une surcouche prematuree
