# Phase 2 - Tickets JIRA

## EPIC - Traduction des sous-titres

### P2-T1 - Cadrer le besoin traduction
- Description : formaliser le besoin, le perimetre, le reporting et la position sur le multi-agent.
- DoD : documents de cadrage phase 2 rediges.

### P2-T2 - Etendre la configuration
- Description : ajouter les variables de config necessaires a la traduction (`TRANSLATION_ROOT`, `TARGET_LANGUAGE`, `TRANSLATION_MODEL`, `OPENAI_API_KEY`).
- DoD : configuration chargee via `.env` et surchargeable par CLI si necessaire.

### P2-T3 - Etendre l'etat CSV
- Description : ajouter la colonne `translated` et maintenir la compatibilite avec les CSV existants.
- DoD : lecture/ecriture compatibles, migration implicite geree.

### P2-T4 - Implementer le moteur de traduction GPT
- Description : creer une interface `TranslationEngine` et une implementation OpenAI/GPT.
- DoD : un segment SRT peut etre traduit sans casser la structure attendue.

### P2-T5 - Implementer la brique `translate`
- Description : traduire les segments individuellement avec reprise segmentaire, logs fins et mise a jour d'etat globale.
- DoD : `--step translate` fonctionnel.

### P2-T6 - Implementer la validation de format SRT
- Description : verifier qu'un segment traduit respecte la structure du segment source.
- DoD : segments invalides rejetes, logs explicites, relance possible.

### P2-T7 - Generaliser le merge pour les SRT traduits
- Description : reutiliser la logique de merge pour produire un fichier final dans la langue cible.
- DoD : deux SRT finaux produits, source et traduit.

### P2-T8 - Mettre a jour le runner Colab
- Description : ajouter les dependances/traces d'execution liees a la traduction et l'appel a `--step translate`.
- DoD : runner Colab compatible avec la phase 2.

### P2-T9 - Ajouter tests et documentation utilisateur
- Description : couvrir la traduction et la validation, puis mettre a jour README et documentation utilisateur.
- DoD : documentation a jour, tests verts, couverture maintenue a un niveau acceptable.
