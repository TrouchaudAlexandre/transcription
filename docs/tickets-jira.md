# Tickets JIRA — Sprint V1 (minimaliste)

## EPIC: Transcription pipeline V1

### T1 — Analyser le prototype et définir le périmètre fonctionnel
- **Description**: Relire le notebook Colab `transcriptionauto.py` et lister les étapes exactes (download, segmentation, transcription, merge SRT, logs, CSV d’état).
- **DoD**: Liste validée des fonctionnalités à conserver à l’identique.

### T2 — Concevoir l’architecture modulaire
- **Description**: Définir les modules (config, sources, download, segmentation, transcription, merge, logs, state).
- **DoD**: Diagramme simple + arborescence cible des fichiers.

### T3 — Mettre en place la config `.env` + CLI
- **Description**: Charger la config par défaut depuis `.env`, surchargeable par arguments CLI.
- **DoD**: CLI fonctionnelle avec `--help` clair.

### T4 — Implémenter la brique download YouTube
- **Description**: Télécharger audio + vidéo via `pytube` et gérer l’état dans un CSV.
- **DoD**: Téléchargement reproductible + reprise possible.

### T5 — Implémenter la segmentation audio
- **Description**: Découper l’audio via `ffmpeg`, générer les segments, mettre à jour l’état.
- **DoD**: Segments générés, logs écrits, état mis à jour.

### T6 — Implémenter la transcription Whisper
- **Description**: Lancer Whisper sur chaque segment (séquentiel V1), logs par fichier.
- **DoD**: Transcriptions générées dans les dossiers attendus.

### T7 — Regrouper les SRT
- **Description**: Recomposer un SRT final en recalant les timestamps et en renumérotant.
- **DoD**: SRT final conforme au prototype.

### T8 — Runner Colab minimal
- **Description**: Créer un script Colab pour cloner le repo et lancer le CLI avec `.env`.
- **DoD**: Runner exécutable en 1–2 cellules.

### T9 — Documentation d’utilisation
- **Description**: Expliquer l’installation, le paramétrage et l’exécution (local + Colab).
- **DoD**: README clair + exemples d’exécution.
