---
name: optimiser-requetes
description: Route ou écran lent, « beaucoup de requêtes », chargement qui traîne, squelettes qui restent, N+1, réponses souvent vides. À charger aussi dès qu'on crée ou modifie une route de lecture de l'API ayFloat ou un écran qui l'appelle. Mesure d'abord (requêtes SQL et appels réseau), puis corrige sans casser le contrat JSON.
---

# Optimiser les requêtes (ayFloat)

Objectif du projet : plus d'un million d'utilisateurs, plus de 1 000 requêtes simultanées. Un N+1 ou une écriture dans un GET compte même si la route est rapide seule.

## 1. Mesurer avant de toucher

- **App :** lister chaque appel réseau de l'écran à l'ouverture (route, quand, combien de fois, doublons, appels refaits à chaque retour d'onglet, appels dont la réponse est vide ou 0).
- **API :** compter les requêtes SQL et le temps, route par route, sur un PDV réel (serveur de dev : lecture et appels réels permis, base de dev). Référence : « Aristide SARL » `a2a33ea6-acff-4ef8-b0ab-652b0a9bd329` (~1 300 échanges). `CaptureQueriesContext` dans un shell Django (`DJANGO_SETTINGS_MODULE=config.settings.production`).
- Noter « avant » : nombre d'appels réseau, requêtes SQL, ms.

## 2. Les causes qui reviennent

- PDV rechargé en entier (prefetchs) à chaque route : charger léger.
- N+1 dans un sérialiseur : `select_related` / `prefetch_related`, ou annotation.
- Agrégats faits en Python : les passer en SQL (`Count`, `Sum`, `filter=Q(...)`), fusionner les agrégats.
- Plusieurs routes pour un seul écran : une route agrégée.
- Écran qui charge tout au démarrage (onglets en `IndexedStack`) ou à chaque changement : charger à la première visite, cache court.
- Calculs lancés quand il n'y a rien (période sans demande) : sortir tôt.
- Liste non bornée : borner (dates, pagination, curseur).
- Écriture dans un GET.

## 3. Corriger sans casser

- Le contrat JSON existant reste valable : l'ancienne app doit continuer à marcher. On ajoute une route ou un champ ; l'app neuve se replie sur les anciennes routes si la nouvelle répond 404.
- Cache court (60 s) seulement pour une lecture sans effet de bord, clé par PDV et période.
- Comparer l'ancien et le nouveau JSON sur un cas réel avant de conclure.
- Index seulement s'il est indispensable (migration).

## 4. Garder le résultat

- Test qui plafonne les requêtes : soit une constante pour une route stable, soit, mieux, « même nombre de requêtes avec N et 2N lignes » (modèle : `apps/salepoints/tests/test_network_capacity.py`).
- Mettre « avant / après » dans le rapport : appels réseau, requêtes SQL, ms.
- Ordre de livraison : l'API d'abord, l'APK ensuite.
