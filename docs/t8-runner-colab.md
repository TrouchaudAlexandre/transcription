# T8 - Runner Colab minimal

## Objectif
Fournir un runner simple pour Google Colab qui clone le repo GitHub et execute les etapes CLI.

## Livrables
- `.env.example`
- `colab/runner-colab.md` (2 cellules pretes a executer)

## Comportement
- Cellule 1:
  - monte Drive
  - clone le repo
  - installe dependances Python et `ffmpeg`
- Cellule 2:
  - copie `.env.example` vers `.env`
  - execute les etapes V1:
    - `download`
    - `segment`
    - `transcribe`
    - `merge`

## DoD T8
- ✅ Runner Colab en 2 cellules disponible.
- ✅ Utilisation basee sur la CLI du projet.
