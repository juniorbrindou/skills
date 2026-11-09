---
name: brind-build
description: Met la branche principale à jour avec le remote, puis, après accord explicite, construit le projet et le publie en production. À utiliser quand l'utilisateur dit "build", "/brind-build", "mets en prod", "déploie", "publie le site".
---

# Build et mise en production

L'utilisateur autorise ce skill à toucher la production, mais **chaque lancement redemande l'accord** avant de construire et de publier.

## 1. Mettre la branche principale à jour

1. Repérer la branche principale : `git symbolic-ref refs/remotes/origin/HEAD`, sinon `main`, sinon `master`.
2. `git fetch origin`, puis comparer avec `git rev-list --left-right --count <principale>...origin/<principale>`.
3. Se placer sur la branche principale. Si le dépôt a des modifications non commitées, ne rien écraser : le dire et s'arrêter (l'utilisateur peut lancer `/brind-publier`).
4. Selon l'écart :
   - **À jour** : continuer.
   - **En retard** : `git pull --ff-only`.
   - **En avance** (commits locaux non poussés) : `git push origin <principale>`, sans `--force`.
   - **Divergée** : `git pull --rebase`. Si des conflits apparaissent, les résoudre quand le bon résultat est évident (modifications sans recouvrement de sens) ; sinon `git rebase --abort`, expliquer le conflit en deux lignes et s'arrêter. Pousser ensuite.
5. Vérifier que `git status` est propre et que local et remote pointent sur le même commit. Sinon s'arrêter.

## 2. Demander l'accord

Avant tout build, demander via AskUserQuestion : « Construire et publier en production ? » en rappelant le commit (`git log --oneline -1`) et ce qui sera mis à jour. Sans réponse positive, s'arrêter après l'étape 1.

## 3. Construire et publier

Chercher la procédure du projet, dans cet ordre : `CLAUDE.md` / `README.md`, `scripts/deploy.sh`, workflow CI (`.github/workflows/deploy.yml`). Utiliser le script du projet plutôt qu'une commande de build brute : un build direct peut écrire dans le répertoire servi.

- Projet `admin` (Angular) : `bash scripts/deploy.sh` (configuration production, publie après build réussi et vérifie que `/admin/` répond 200).
- Si un déploiement automatique part du push (workflow CI), le dire plutôt que de publier une seconde fois à la main.

## 4. Rapport

Deux lignes : commit publié, résultat de la vérification (code HTTP). Si une étape échoue, citer l'erreur telle quelle et dire dans quel état est la production.

## Interdits

- Jamais `pm2 restart` : bloqué pour l'agent, c'est à l'utilisateur de le lancer. Si le projet en a besoin (API), donner la commande et s'arrêter.
- Jamais `loaddata initial_roles` en production.
- Jamais de `--force`, jamais de commit de `backups/`.
