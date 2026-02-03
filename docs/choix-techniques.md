# Choix techniques — V1

## Langage et exécution
- **Python** (exécution principale).
- **Google Colab** comme environnement d’exécution pour la V1 (GPU requis par Whisper).

## Configuration
- Fichier `.env` comme source de configuration par défaut.
- Surcharge possible via **arguments CLI**.

## Source vidéo/audio
- **YouTube via `pytube`** pour la V1.
- Support principal : **playlists** (évolutif vers d’autres sources plus tard).

## Transcription
- **OpenAI Whisper (openai-whisper)** pour la V1.
- Le choix est motivé par la stabilité du modèle et la compatibilité immédiate avec Colab.
- Préparation d’une couche d’abstraction pour permettre de substituer le moteur plus tard.

## Segmentation audio
- **ffmpeg** pour découper les fichiers audio en segments réguliers.

## Stockage
- Écriture via le **montage Google Drive** : `/content/drive/...`.
- Pas d’intégration API Drive pour la V1.

## Sorties
- **Comportement identique** au prototype actuel :
  - Fichiers de transcription par segment.
  - Fichier SRT final combiné.
  - Logs par étape.

## Lancement depuis Colab
- Un petit script/runner Colab clone le dépôt GitHub et lance le CLI.

## Extensibilité prévue
- Abstraction des sources (YouTube aujourd’hui, autres plus tard).
- Abstraction des moteurs de transcription (Whisper aujourd’hui, autres plus tard).
- Pipeline par étapes (download → segment → transcribe → merge).
