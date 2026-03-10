# P2-T4 - Moteur de traduction GPT

## Objectif
Ajouter une brique de traduction abstraite et une premiere implementation OpenAI/GPT, sans encore brancher l'etape `translate` dans la CLI.

## Livrables
- `src/transcription/domain/interfaces/translation_engine.py`
- `src/transcription/infrastructure/translation/openai_translation_engine.py`
- `src/transcription/infrastructure/translation/translation_engine_factory.py`
- `tests/test_openai_translation_engine.py`

## Contrat de l'interface
- entree :
  - contenu SRT d'un segment
  - langue source
  - langue cible
- sortie :
  - contenu SRT traduit

## Comportement attendu du moteur GPT
- utiliser l'API OpenAI via `responses.create`
- preserver la structure SRT
- ne pas modifier les timestamps
- ne retourner que du contenu SRT
- rejeter une reponse vide
- integrer si presents :
  - `SOURCE_VARIANT`
  - `TRANSLATION_CONTEXT`

## Parametrage de contexte
- `WHISPER_LANGUAGE` reste la langue source generale
- `SOURCE_VARIANT` permet de preciser un dialecte ou registre, par exemple `tunisian_arabic`
- `TRANSLATION_CONTEXT` permet d'ajouter des consignes libres de contexte metier/culturel

Le moteur doit utiliser ces informations dans le prompt sans les rendre obligatoires.

## Orientation d'architecture
- usage d'un pattern `Strategy` via `TranslationEngine`
- usage d'une `Factory` pour choisir le provider depuis la configuration
- implementation disponible :
  - `openai`
- providers vises a terme :
  - `mistral`
  - `gemini`

## Limites
- pas encore de validation de format structurelle
- pas encore de branchement CLI/use case `translate`

## DoD
- ✅ interface de traduction introduite
- ✅ moteur OpenAI/GPT implemente
- ✅ tests unitaire du moteur ajoutes
