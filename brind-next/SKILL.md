---
name: brind-next
description: Appelé sans contexte quand l'utilisateur a terminé un sujet et veut passer au suivant. Repère dans le code le prochain sujet le plus important pour l'application et relance le travail dessus. À utiliser quand l'utilisateur dit "next", "/brind-next", "on passe à autre chose", "j'ai fini, et maintenant ?".
---

# Passer au sujet suivant

Appelé **sans argument ni contexte**. Ne rien demander avant d'avoir regardé le projet : tout se déduit de ce qui s'y trouve.

## 1. Clore le sujet précédent

1. `git status --short` et `git log --oneline -10` : ce qui vient d'être fait, et s'il reste des modifications non commitées.
2. S'il en reste, le signaler en une ligne et proposer `/brind-publier`. Ne pas commiter soi-même.
3. Oublier le sujet précédent : on repart sur autre chose.

## 2. Repérer les candidats

Charger le skill `codebase-design` avec l'outil Skill, et appliquer son vocabulaire (modules profonds, interfaces, coutures) pour lire le projet. Chercher des sujets de trois natures :

- **Faiblesse** : module superficiel, logique dupliquée, couture au mauvais endroit, zone difficile à tester ou à parcourir.
- **Manque** : fonctionnalité annoncée mais absente (TODO, `console.log` à la place d'un comportement, écran sans destination, doc ou spec non réalisée).
- **Fragilité visible** : écran dont le rendu, la responsivité ou le parcours est faible pour l'utilisateur final.

Sources : `CLAUDE.md`, README, `doc/` et `specs/`, TODO/FIXME du code, historique git récent (les zones qui bougent beaucoup), tests manquants.

## 3. Pondérer par l'importance pour l'application

Classer chaque candidat selon ce que l'application **sert d'abord** : ce que ses utilisateurs finaux font tous les jours, ce qui touche l'argent, l'authentification ou les données de production, ce qui bloque d'autres écrans. Un défaut sur un parcours central passe avant une amélioration de confort sur un écran rare.

Ne retenir que les 3 premiers, chacun en une ligne : le sujet, pourquoi il compte pour l'application, la première action concrète.

## 4. Relancer

Présenter les 3 sujets et demander lequel lancer (AskUserQuestion, le premier recommandé). Dès la réponse :

- sujet de design d'interface → appliquer le skill `brind-embellir` ;
- sujet de structure du code → continuer avec `codebase-design` ;
- autre sujet → commencer par la première action annoncée.

## Règles

- Réponse courte : pas de rapport, les trois sujets et la question.
- Ne rien modifier avant que l'utilisateur ait choisi.
- Rien de destructeur, rien en production : commit, publication et déploiement restent à `/brind-publier` et `/brind-build`.
