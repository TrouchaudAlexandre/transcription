# Architecture — V1 (POO & Design Patterns)

## Objectifs d’architecture
- Séparer clairement **domaine**, **application**, **infrastructure**.
- Respecter la **responsabilité unique** par classe/module.
- Rendre les briques **extensibles** (sources, moteurs de transcription, stockage) sans modifier le cœur.
- Favoriser l’injection de dépendances et la testabilité.

## Vue d’ensemble (layers)

### 1) Domaine (`domain/`)
- Contient les **entités** et **interfaces** fondamentales.
- Aucun accès direct aux APIs externes, ni à l’IO.

### 2) Application (`application/`)
- Orchestration des **use cases** (pipeline download → segment → transcribe → merge).
- Utilise les interfaces du domaine, reçoit des implémentations via injection.

### 3) Infrastructure (`infrastructure/`)
- Implémentations concrètes : YouTube (pytube), Whisper, ffmpeg, filesystem, logs.

### 4) Interface (`cli/`)
- Point d’entrée CLI + chargement `.env` + paramètres.

## Patterns principaux

### Strategy
- Permet de **changer de source** (YouTube, autre) ou de **moteur de transcription** sans toucher au pipeline.
- Exemple : `TranscriptionEngine` + `WhisperEngine`.

### Factory
- Centralise la création des services en fonction de la config.
- Exemple : `EngineFactory` qui retourne l’implémentation Whisper.

### Template Method / Pipeline
- La chaîne d’exécution est standardisée (download → segment → transcribe → merge) mais chaque étape peut être remplacée.

### Adapter
- Encapsule des APIs externes (pytube, ffmpeg, whisper CLI).
- Le domaine interagit avec des interfaces propres.

### Repository (léger)
- Abstraction d’accès aux fichiers d’état (CSV) et logs.

## Arborescence cible

```
src/
  transcription/
    cli/
      main.py
    application/
      pipeline.py
      use_cases/
        download.py
        segment.py
        transcribe.py
        merge.py
    domain/
      models/
        media.py
        transcript.py
      interfaces/
        source.py
        segmenter.py
        engine.py
        storage.py
        state_repo.py
        logger.py
    infrastructure/
      sources/
        youtube_pytube.py
      transcription/
        whisper_engine.py
      segmentation/
        ffmpeg_segmenter.py
      storage/
        filesystem_storage.py
      state/
        csv_state_repo.py
      logging/
        file_logger.py
    config/
      settings.py
```

## Principes POO appliqués
- **Encapsulation** : chaque classe encapsule un comportement (ex: `WhisperEngine`).
- **Responsabilité unique** : chaque module a un rôle précis (download, segment, transcribe, merge).
- **Dépendances inversées** : le pipeline dépend d’interfaces (`domain/interfaces`).
- **Extensibilité** : ajout de source ou moteur = nouvelle classe infra sans modifier le cœur.

## Flux principal (pipeline)
1. Charger la config (`settings.py`) depuis `.env` + CLI.
2. Instancier les implémentations (Factory).
3. Exécuter les use cases dans l’ordre :
   - Download
   - Segmentation
   - Transcription
   - Merge SRT
4. Écrire logs et mise à jour d’état.

## État et reprise
- CSV d’état (`state_repo`) conserve pour chaque fichier :
  - téléchargé / segmenté / transcrit.
- Chaque use case consulte l’état pour skip/relancer.

## Points d’extension futurs
- **Sources** : ajouter un `OtherSourceAdapter`.
- **Transcription engines** : ajouter `FasterWhisperEngine` ou API externe.
- **Stockage** : ajouter un backend Drive API ou S3.

