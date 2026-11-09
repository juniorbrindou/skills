---
name: brind-embellir
description: Améliore l'UI, l'UX, la responsivité et l'intuitivité d'une page ou d'un composant à partir d'une URL, d'un nom de fichier ou d'une capture d'écran. À utiliser quand l'utilisateur dit "embellir", "/brind-embellir", "cette page n'est pas belle", "améliore le design de ...".
---

# Embellir une page ou un composant

Entrée : une URL, un nom de fichier ou une capture d'écran (un seul suffit). Rien d'autre n'est à demander.

## Postulat

Le design de cette page ou de ce composant n'est pas beau. Il faut l'améliorer sur quatre points :

1. **UI** : hiérarchie visuelle, typographie, espacements, couleurs, états.
2. **UX** : l'utilisateur final comprend la page d'un coup d'œil, avec le maximum d'information utile dès le premier regard.
3. **Responsivité** : correct du téléphone au grand écran, sans défilement horizontal parasite.
4. **Intuitivité** : chaque action est nommée en clair et au bon endroit ; aucune explication n'est nécessaire.

Le résultat final doit être **élégant et beau**, pas seulement correct.

## Étapes

1. **Charger le skill `frontend-design`** avec l'outil Skill, avant toute proposition ou modification. Ses principes (direction esthétique, typographie, restriction, auto-critique) s'appliquent à tout ce qui suit.
2. **Retrouver la cible** :
   - capture d'écran : la lire, puis chercher dans le code le composant qui l'affiche (textes visibles, titres, libellés) ;
   - nom de fichier : le lire en entier, avec son gabarit et ses styles ;
   - URL : la route correspond à un composant du projet ; le retrouver dans le routage. Ne pas ouvrir de page protégée à la place de l'utilisateur.
3. **Comprendre le contexte du projet** : charte existante (jetons de couleur, composants partagés, `doc/Design/`, CLAUDE.md). S'y plier : l'amélioration reste cohérente avec le reste de l'application, elle ne crée pas un second style.
4. **Diagnostiquer en une demi-douzaine de points** (pas un rapport) : ce qui gêne l'utilisateur final, ce qui est caché, ce qui est répété, ce qui casse sur mobile.
5. **Appliquer directement dans le code** du composant, sauf si l'utilisateur a demandé une proposition d'abord. Garder la logique métier, les données et les routes intactes ; ne changer que ce qui est affiché. Pour une simple proposition, produire une maquette visuelle avant de toucher au code.
6. **Vérifier** : le build passe ; si un navigateur ou un serveur de développement est disponible, contrôler le rendu à environ 375 px, 768 px et 1280 px ; sinon dire que le rendu n'a pas été vu.

## Règles

- Textes en français, à la forme que l'utilisateur final reconnaît (jamais le vocabulaire du système), actions en verbe d'action : « Valider », « Rejeter ».
- Information clé visible sans cliquer : statut, montant, date, ce qui attend une décision.
- Accessibilité de base : contraste suffisant, focus visible, couleur jamais seule porteuse d'information, animations coupées si `prefers-reduced-motion`.
- Pas de nouvelle dépendance sans nécessité.

## Réponse finale

Court : ce qui a changé pour l'utilisateur final (3 à 5 puces), ce qui reste à vérifier (rendu non vu, point à arbitrer). Pas de commit, pas de déploiement : ils se font avec `/brind-publier` et `/brind-build`.
