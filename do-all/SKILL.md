---
name: do-all
description: Chaîne complète sans rien redemander — commiter, fusionner, supprimer les branches fusionnées (local et remote), builder, déployer, vérifier l'adresse publique. À utiliser quand l'utilisateur dit "do all", "fais tout", "fait tout", "/do-all".
---

# Do all

« Do all » = toute la chaîne d'un coup, **sans redemander** : l'utilisateur a donné son accord par ce mot (définition du 2026-10-28). Ne s'arrêter que sur un blocage réel.

## Chaîne

1. **Inventaire.** Pour chaque dépôt touché (api, admin, mobile, dely…) : `git status`, `git branch -a`, branches non fusionnées. Ne jamais embarquer ce qui traîne dans le répertoire de travail d'une autre session.
2. **Commiter** ce qui est en cours sur sa branche (jamais de trailer `Co-Authored-By`, jamais de mention d'assistant), puis pousser la branche.
3. **Fusionner** les branches de travail dans la branche principale du dépôt : API `master`, admin `master`, app PDV `sandbox` puis `main` en avance rapide, app coursier `main`. Conflit de `CHANGELOG.md` : recomposer la section de la version à la main, ne jamais écraser du code par `-X ours`.
4. **Journal, version, tag** (à chaque déploiement, sans qu'on le demande) :
   - relire les commits depuis la dernière version, une phrase par changement visible sous `## [À venir]`, puis renommer en `[X.Y.Z] — AAAA-MM-JJ` et recréer un `[À venir]` vide ;
   - API : `"VERSION"` dans `config/settings/base.py` + tag `vX.Y.Z` ; admin : `package.json` et `package-lock.json` (CRLF : éditer en binaire) ; apps : `version: X.Y.Z+N` du `pubspec.yaml`, `N` +1 sans jamais être réutilisé ;
   - pas de 1.x avant la prod, aucun chemin de serveur dans les journaux, « coursier » et jamais « livreur ».
5. **Vérifier avant de construire :** `flutter analyze` et tests des zones touchées pour les apps ; `pytest` des zones touchées pour l'API (recette : `PYTHONPATH=/tmp/te-libs DATABASE_URL=postgres://<utilisateur>:<mot de passe>@127.0.0.1:5432/<base> .venv/bin/python -m pytest …`) ; `makemigrations --check` avec `DJANGO_SETTINGS_MODULE=config.settings.testing`.
6. **Builder et déployer tout ce qui a changé** (« il faut toujours tout déployer ») :
   - API : `sudo -n bash scripts/deploy.sh` (migrer avant de redémarrer, beat compris) ;
   - admin : `bash scripts/deploy.sh` ;
   - APK : `ANDROID_HOME=/opt/android-sdk flutter build apk --release --obfuscate --split-debug-info=build/symbols/<version>` depuis le dossier de l'app, copie dans `/var/www/float/downloads/` (`pdv-sandbox-<v>.apk` ou `driver-sandbox-<v>.apk`), retrait de l'ancien, puis `mobile-version.json` (avec `sha256`) ou `livreur-version.json`. Jamais de `*-latest.apk`.
7. **Vérifier ce qui est servi** avant de dire « en ligne » : API (`/api/salepoints/` → 401, `/api/schema/` annonce la version, processus pm2 en ligne), admin (`/admin/` → 200 et le texte changé présent dans le fichier servi), APK (206 sur `-r 0-99`, fichier de version public, empreinte du fichier servi égale à celle du JSON).
8. **Pousser** la branche principale et les tags ; contrôler que local et remote pointent sur le même commit.
9. **Supprimer les branches fusionnées**, en local et en remote, jamais `main`, `master`, `sandbox` : `git branch --merged` puis `git branch -d` et `git push origin --delete`. Les branches non fusionnées d'autres chantiers restent ; les citer.

## Interdits

- Ne jamais commiter `backups/` ; ne jamais lancer `loaddata initial_roles` en production ; pas de `--force`.
- Écran front : contrôler à 375 px quand l'étape l'exige.

## Réponse finale

Courte, par dépôt : version publiée, ce qui a été vérifié sur l'adresse publique, branches supprimées, ce qui n'a pas été vu sur un vrai téléphone. Rien de plus.
