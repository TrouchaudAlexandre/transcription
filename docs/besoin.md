# Besoin — Projet de transcription vidéo

## Contexte
Le prototype actuel est un notebook Google Colab (`temp/transcriptionauto.py`) qui télécharge des vidéos/audio YouTube, segmente l’audio, transcrit avec Whisper, puis regroupe les SRT. Il fonctionne mais manque de modularité, de paramétrage, et d’architecture propre.

## Objectif
Construire une brique **exclusivement dédiée à la transcription** (pas de traduction dans cette V1), réutilisable et extensible, tout en conservant le comportement fonctionnel actuel.

## Portée V1
- Utiliser **Google Colab** pour l’exécution (puissance GPU requise par Whisper), avec la possibilité de **cloner le repo GitHub et lancer un exécutable** (CLI Python) depuis Colab.
- La source actuelle est **YouTube via une playlist** (évolutif vers d’autres sources plus tard).
- Le stockage cible est le **point de montage Google Drive** (`/content/drive/...`).
- Le format de sortie doit **rester identique au code existant** (transcriptions, SRT, logs, structure de dossiers).
- La configuration se fait via un **fichier `.env`** (valeurs par défaut), surchargeable par **arguments CLI**.

## Exigences fonctionnelles
- Télécharger les contenus YouTube (audio + vidéo) via `pytube`.
- Enregistrer l’état des fichiers (téléchargé/segmenté/transcrit) pour permettre la reprise.
- Segmenter l’audio via `ffmpeg`.
- Transcrire via **OpenAI Whisper (openai-whisper)**.
- Regrouper les segments SRT en un fichier final.
- Produire des logs clairs et exploitables.

## Exigences non fonctionnelles
- Architecture modulaire (future extension vers d’autres sources ou moteurs de transcription).
- Paramétrage clair via `.env` + CLI.
- Scripts simples à exécuter sur Colab (runner minimaliste).
- Code lisible, documenté et testable (même si tests V1 limités).

## Hors périmètre V1
- Traduction (brique ultérieure).
- Migration vers d’autres moteurs de transcription (préparer l’extensibilité uniquement).
- Stockage Drive via API (on reste sur le montage `/content/drive`).
