# Phase 2 - Choix techniques traduction

## Strategie generale
- Reutiliser le pipeline V1 existant.
- Inserer une etape `translate` entre `transcribe` et `merge` ou, plus precisement, ajouter un second flux de merge pour les sorties traduites.
- Reprendre le meme modele d'execution que `transcribe` :
  - traitement par segment
  - logs par segment
  - reprise fine sur artefacts deja presents

## Source de travail
- La traduction repose sur les fichiers segmentes transcrits.
- Le fichier d'entree de la traduction est un SRT segmentaire.
- Le fichier final global traduit est obtenu par fusion apres traduction de tous les segments.

## Moteur de traduction
- Interface dediee : `TranslationEngine`.
- Premiere implementation : moteur OpenAI avec un modele GPT recent et parametrable.
- Le moteur doit etre remplaçable plus tard sans impacter les use cases.

## Validation de format
- La verification du format SRT ne doit pas etre geree par un "agent" LLM en V1.
- Elle doit etre essentiellement deterministe :
  - nombre de blocs identique
  - index coherents
  - timecodes preserves
  - texte non vide
- En cas d'echec de validation, le segment est considere comme echoue et doit pouvoir etre relance.

## Gestion d'etat
- Le CSV d'etat actuel est conserve.
- Ajout d'une colonne `translated`.
- Le boolen `translated` represente l'etat global d'un audio.
- La reprise fine reste determinee par la presence de fichiers segments traduits sur disque.

## Stockage recommande
- Sous-titres source :
  - conserver strictement le chemin deja utilise en V1
  - `TRANSCRIPTION_ROOT/<playlist>/<audio_filename>/`
  - objectif : reutiliser sans migration les transcriptions et segments deja produits
- Sous-titres traduits :
  - `TRANSLATION_ROOT/<playlist>/<audio_filename>/`
- Sous-titre final source :
  - `OUTPUT_ROOT/<playlist>/<audio_stem>_sous-titres_complets.srt`
- Sous-titre final traduit :
  - `OUTPUT_ROOT/<playlist>/<audio_stem>_<target_language>_sous-titres_complets.srt`

## Configuration a ajouter
- `TRANSLATION_ROOT`
- `TARGET_LANGUAGE`
- `TRANSLATION_MODEL`
- `OPENAI_API_KEY`
- optionnel :
  - `SOURCE_LANGUAGE`
  - `TRANSLATION_PROMPT_VERSION`

## Contrainte de compatibilite V1
- La phase 2 ne doit pas modifier l'emplacement des sous-titres source existants.
- La traduction doit lire directement dans `TRANSCRIPTION_ROOT` tel qu'il est utilise aujourd'hui.
- Aucune migration des artefacts V1 ne doit etre necessaire pour activer la phase 2.

## Position sur le multi-agent
- Non retenu pour la V1 phase 2.
- Raisons :
  - complexite de mise en oeuvre plus forte
  - cout plus eleve
  - debuggage plus difficile
  - valeur faible par rapport a un pipeline simple avec validation deterministe
- Choix recommande :
  - 1 moteur IA de traduction
  - 1 validateur technique non-LLM
  - 1 strategie de retry si validation KO
