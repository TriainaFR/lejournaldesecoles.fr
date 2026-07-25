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

## SEO / GEO

Le site est pensé pour le référencement classique **et** la citation par les moteurs IA (GEO) : HTML sémantique, bloc « réponse » extractible, tableaux de classement natifs, FAQ structurée, données datées et méthodologie publique.
