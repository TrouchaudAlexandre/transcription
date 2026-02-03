# T2 — Architecture modulaire (POO + patterns)

## Découpage en couches

### Domaine (`domain`)
- Entités et interfaces, **sans dépendances externes**.
- Exemples : `MediaItem`, `AudioSegment`, `TranscriptArtifact`.
- Interfaces : `MediaSource`, `AudioSegmenter`, `TranscriptionEngine`, `StateRepository`, `Logger`, `Storage`.

### Application (`application`)
- Orchestration des **use cases**.
- Un pipeline explicite : `download → segment → transcribe → merge`.
- Use cases dédiés par étape.

### Infrastructure (`infrastructure`)
- Adaptateurs concrets :
  - YouTube via `pytube`.
  - Segmentation via `ffmpeg`.
  - Transcription via `openai-whisper` CLI.
  - Stockage local/montage Drive.
  - Repo d’état CSV.
  - Logs fichiers.

### Interface (`cli`)
- Point d’entrée CLI.
- Chargement `.env` + surcharge par arguments.

## Patterns retenus

- **Strategy** : changer de source ou moteur de transcription sans modifier le pipeline.
- **Factory** : création centralisée des implémentations en fonction de la config.
- **Adapter** : encapsuler `pytube`, `ffmpeg`, `whisper`.
- **Pipeline / Template Method** : enchaînement standardisé des étapes.
- **Repository (léger)** : abstraction du CSV d’état.

## Arborescence cible (V1)

```
src/
  transcription/
    cli/
    application/
      pipeline.py
      use_cases/
    domain/
      models/
      interfaces/
    infrastructure/
      sources/
      segmentation/
      transcription/
      storage/
      state/
      logging/
    config/
```

## Règles de conception
- **SRP** : 1 classe = 1 responsabilité.
- **DIP** : pipeline dépend des interfaces, pas des implémentations.
- **Extensibilité** : ajout d’une source/moteur = nouvelle classe infra.

## DoD T2
- ✅ Architecture validée (couches + patterns).
- ✅ Arborescence cible définie.
