# Le Journal des Écoles

Média français indépendant consacré aux études supérieures : classements des écoles de commerce, d'ingénieurs, de design, d'architecture, de communication et des filières RH, parcours métiers et conseils d'orientation.

🌐 [lejournaldesecoles.fr](https://lejournaldesecoles.fr) — un média [Triaina](https://triaina.fr), marque sœur du [Journal du Vin](https://lejournalduvin.fr).

## Identité

- **Typographies** : Playfair Display (titres) · Hanken Grotesk (texte)
- **Palette** : papier porcelaine `#F6F8FA` · quadrillage cahier discret · encre nuit `#131A22` · marine `#1E4B87` · or `#A9822F`
- **Principe** : le quadrillage est un décor, jamais sous les zones de lecture

## Structure

- `index.html` — home page (statique, CSS inline, JSON-LD : NewsMediaOrganization, WebSite, ItemList, FAQPage)
- `assets/` — favicon et ressources graphiques

## Commandes

Le dépôt est **volontairement dépourvu de `package.json` versionné** : Railway le déploie comme site statique précisément parce qu'il n'y détecte aucun projet Node. Le `package.json` d'outillage existe donc en local uniquement (il est dans `.gitignore`). Pour le recréer sur une nouvelle machine :

```json
{
  "name": "lejournaldesecoles-outils", "version": "1.0.0", "private": true, "type": "module",
  "scripts": {
    "indexnow": "node scripts/indexnow.mjs",
    "indexnow:new": "node scripts/indexnow.mjs --new",
    "indexnow:dry": "node scripts/indexnow.mjs --dry",
    "rubriques": "<chemin-vers-python-3.12>/python scripts/build-rubriques.py"
  }
}
```

⚠️ **`build-rubriques.py` exige Python 3.12 ou plus** (il utilise des f-strings contenant des antislashs, refusées par les versions antérieures). Le `python3` livré avec macOS est en 3.9 et échoue avec une `SyntaxError` : il faut donc pointer le script `rubriques` vers un interpréteur récent plutôt que vers `python3`. Vérifier la version disponible avec `python3 --version`, et sur la machine de la rédaction utiliser `/Users/l.l/.claude/skills/seo/.venv/bin/python`.

| Commande | Effet |
|---|---|
| `npm run indexnow` | Soumet **toutes** les URL du sitemap à IndexNow |
| `npm run indexnow:new` | Soumet uniquement les pages **modifiées** depuis le dernier envoi |
| `npm run indexnow:dry` | Affiche ce qui serait envoyé, sans rien envoyer |
| `npm run indexnow -- <url>` | Soumet une ou plusieurs URL précises |
| `npm run rubriques` | Régénère les pages de rubrique depuis `assets/articles.json` |

Une seule soumission IndexNow alimente **Bing** (et donc **Copilot**, qui s'appuie sur l'index Bing), Yandex, Seznam et Naver. **Google n'utilise pas IndexNow** : pour lui, la découverte passe par `sitemap.xml` et la Search Console.

## Serveur et en-têtes HTTP

Railway déploie ce dépôt en site statique via **Railpack**, qui sert les fichiers avec **Caddy**. Le `Caddyfile` à la racine **remplace celui généré par défaut** : Railpack le lit, le passe dans son moteur de template puis le monte dans l'image. C'est donc le seul endroit du dépôt d'où l'on peut piloter les en-têtes de réponse, les réécritures d'URL et le cache, sans dépendre du tableau de bord Cloudflare.

Il contient aujourd'hui, en plus des réglages par défaut de Railpack (en-têtes de sécurité, compression, `try_files`, pages d'erreur) :

- les **Link headers de découverte agent** (RFC 8288) sur les documents HTML : `api-catalog`, `describedby`, `author`, `license` ;
- la réécriture de **`/.well-known/api-catalog`** vers `/api-catalog.json`, le chemin standard de la RFC 9727 que Railway ne peut pas servir en dossier caché ;
- un **`Cache-Control` court** sur les fichiers d'instructions machine.

⚠️ Deux règles à respecter en modifiant ce fichier :

1. **Ne pas remplacer la variable de racine statique** de la directive `root` par un chemin en dur : c'est Railpack qui la substitue au build.
2. **Une erreur de syntaxe fait échouer le build.** Railway conserve alors le déploiement précédent, mais il faut vérifier la production après chaque modification (`curl -D - -o /dev/null https://lejournaldesecoles.fr/`).

⚠️ **Cloudflare met `robots.txt` en cache pendant 4 heures et écrase le `Cache-Control` d'origine** (constaté le 2026-07-28 : `max-age=300` renvoyé par Caddy, `max-age=14400` servi à l'arrivée). Les autres fichiers machine, eux, ne sont pas mis en cache. Après toute modification de `robots.txt`, **purger le cache Cloudflare** (Caching → Configuration → Custom Purge sur l'URL du fichier), sinon les moteurs et les scanners continueront de lire l'ancienne version pendant quatre heures.

## SEO / GEO

Le site est pensé pour le référencement classique **et** la citation par les moteurs IA (GEO) : HTML sémantique, bloc « réponse » extractible, tableaux de classement natifs, FAQ structurée, données datées et méthodologie publique.
