# Phase 2 - Besoin fonctionnel traduction

## Contexte
La V1 couvre le pipeline suivant :
- download
- segment
- transcribe
- merge

La phase 2 ajoute une brique de traduction en capitalisant sur l'existant. L'objectif n'est pas de retraduire un SRT final global, mais de reutiliser les segments deja produits et transcrits afin de mieux controler le volume envoye au modele, les reprises sur erreur et le cout.

## Objectif
Ajouter un pipeline de traduction qui produit, pour chaque audio/video :
- un sous-titre final dans la langue source
- un sous-titre final dans une langue cible passee en parametre

## Principe fonctionnel retenu
- La traduction se fait a partir des segments issus de la segmentation/transcription.
- Chaque segment traduit est stocke individuellement.
- Une fois tous les segments traduits, ils sont fusionnes dans un fichier final global, comme pour la transcription source.
- Le reporting d'avancement doit etre etendu pour suivre la traduction et eviter les retraitements inutiles.

## Exigences fonctionnelles
- Introduire une nouvelle etape `translate` dans le pipeline.
- Traduire chaque segment SRT individuellement via un moteur IA parametrable.
- Utiliser un modele GPT recent pour la premiere implementation.
- Conserver les timecodes inchanges pendant la traduction.
- Conserver la structure SRT bloc par bloc.
- Permettre la reprise sur erreur :
  - un segment deja traduit ne doit pas etre retraduit
  - un audio n'est marque comme traduit que si tous ses segments sont valides
- Produire un fichier SRT final traduit par audio.
- Conserver le fichier SRT final source deja produit par la V1.

## Exigences de reporting
- Etendre le fichier d'etat CSV avec une nouvelle colonne `translated`.
- Conserver la logique actuelle de reprise basee sur :
  - l'etat global par audio dans le CSV
  - la presence des artefacts reels sur disque pour la reprise fine
- Journaliser l'avancement de la traduction segment par segment :
  - start
  - done
  - skip
  - failed

## Exigences non fonctionnelles
- Respecter l'architecture existante (domain / application / infrastructure / cli).
- Garder une conception modulaire pour changer de moteur de traduction plus tard.
- Eviter les appels IA inutiles grace au controle des segments deja traites.
- Garder un pipeline robuste, simple a relancer et a diagnostiquer.

## Hors perimetre de la phase 2
- Traduction multi-langues simultanee dans une meme execution
- Post-edition humaine
- Systeme multi-agent complet
- Verification linguistique avancee par un second LLM

## Decision de conception cle
- La traduction doit partir des segments, pas du sous-titre final fusionne.
- Le merge traduit doit reutiliser la logique de fusion SRT existante.
