# P2-T6 - Validation deterministe du format SRT

## Objectif
Verifier qu'un segment SRT traduit reste structurellement compatible avec le segment source avant de l'accepter comme valide.

## Livrables
- `src/transcription/domain/interfaces/srt_validator.py`
- `src/transcription/infrastructure/translation/srt_validator.py`
- branchement du validateur dans `TranslateUseCase`
- tests unitaire dedies

## Regles de validation
- meme nombre de blocs
- memes index de blocs
- memes timecodes
- texte traduit non vide
- blocs complets et bien formes

## Comportement
- si la validation echoue :
  - le segment est considere en echec
  - aucun `translated=true` global n'est pose
  - la relance reste possible

## DoD
- ✅ validation structurelle branchee
- ✅ segments invalides rejetes
- ✅ tests dedies ajoutes
