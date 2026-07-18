#!/usr/bin/env python3
"""Génère les pages de rubrique du Journal des Écoles à partir du registre
assets/articles.json. À relancer après chaque publication d'article :

    python3 scripts/build-rubriques.py

Le HTML produit est entièrement statique (listes d'articles incluses) :
aucun rendu client, condition de base pour être lu par les crawlers IA.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://lejournaldesecoles.fr"

RUBRIQUES = {
    "classements": {
        "nav": "Classements",
        "h1": "Classements",
        "title": "Classements des écoles supérieures — Le Journal des Écoles",
        "meta": "Tous les classements du Journal des Écoles : écoles de commerce, d'ingénieurs, de design et de communication, croisés avec notre Indice ROI exclusif.",
        "desc": "Tous les classements du Journal des Écoles : commerce, ingénieurs, design, communication. Des palmarès croisés (SIGEM, Figaro Étudiant, L'Étudiant, Financial Times, QS) complétés par notre Indice ROI exclusif — le coût réel des études rapporté au salaire de sortie.",
        "index": True,
    },
    "commerce": {
        "nav": "Commerce",
        "h1": "Commerce & Management",
        "title": "Écoles de commerce & management — Le Journal des Écoles",
        "meta": "Écoles de commerce : classements SIGEM, L'Étudiant et Financial Times, frais des PGE, salaires de sortie, admissions BCE/Ecricome et alternance.",
        "desc": "Écoles de commerce et de management : classements SIGEM, L'Étudiant et Financial Times, frais des programmes grande école, salaires de sortie, admissions BCE et Ecricome, alternance. Les enquêtes de la rédaction, sourcées école par école.",
        "index": True,
    },
    "ingenieurs": {
        "nav": "Ingénieurs",
        "h1": "Ingénieurs",
        "title": "Écoles d'ingénieurs — Le Journal des Écoles",
        "meta": "Écoles d'ingénieurs : palmarès Figaro, L'Étudiant et DAUR, accréditation CTI, salaires CGE, concours Mines-Télécom, Centrale-Supélec, X-ENS et voies post-bac.",
        "desc": "Écoles d'ingénieurs : palmarès Figaro Étudiant, L'Étudiant et DAUR croisés, accréditation CTI, salaires CGE, concours Mines-Télécom, Centrale-Supélec et X-ENS, et les voies post-bac (INSA, universités de technologie, réseau Polytech).",
        "index": True,
    },
    "design-architecture": {
        "nav": "Design &amp; Archi",
        "h1": "Design & Architecture",
        "title": "Écoles de design & d'architecture — Le Journal des Écoles",
        "meta": "Écoles de design et d'architecture : palmarès Figaro et QS, ENSAD, ENSCI, Boulle, Camondo, admissions avec portfolio et Indice ROI public/privé.",
        "desc": "Écoles de design et d'architecture : palmarès Figaro Étudiant et classement mondial QS, fiches ENSAD, ENSCI, Boulle et Camondo, admissions avec portfolio, prépas MANAA et notre Indice ROI public/privé.",
        "index": True,
    },
    "communication": {
        "nav": "Communication",
        "h1": "Communication & Médias",
        "title": "Écoles de communication & médias — Le Journal des Écoles",
        "meta": "Écoles de communication : CELSA, ISCOM, EFAP, Sup de Pub — palmarès Figaro, masters Eduniversal, débouchés RP, digital et événementiel.",
        "desc": "Écoles de communication et de médias : CELSA, ISCOM, EFAP, Sup de Pub — palmarès Figaro Étudiant, masters classés par Eduniversal, admissions et débouchés en relations presse, communication digitale, publicité et événementiel.",
        "index": True,
    },
    "rh-gestion": {
        "nav": "RH &amp; Gestion",
        "h1": "RH & Gestion",
        "title": "RH & gestion — Le Journal des Écoles",
        "meta": "Ressources humaines et gestion : masters RH, droit social et management — les classements et parcours de la rédaction arrivent.",
        "desc": "Ressources humaines, gestion et management : masters RH, droit social, paie et administration des entreprises. Les premières enquêtes et classements de la rédaction sur cette filière arrivent.",
        "index": False,
        "empty": "Les premières enquêtes de la rédaction sur les filières RH et gestion sont en préparation. En attendant, explorez nos classements déjà publiés — ou abonnez-vous à « L'Amphi » pour être prévenu de leur sortie.",
    },
    "metiers": {
        "nav": "Métiers",
        "h1": "Métiers & Parcours",
        "title": "Métiers & parcours — Le Journal des Écoles",
        "meta": "Parcours métiers : du bac au premier poste, salaires de sortie et itinéraires d'excellence en finance, ingénierie et création.",
        "desc": "Du bac au premier poste : itinéraires d'excellence, salaires de sortie et voies d'accès vers la finance, l'ingénierie, la création et les médias. Les fiches métiers détaillées de la rédaction arrivent.",
        "index": False,
        "empty": "Les fiches métiers détaillées sont en préparation. Découvrez déjà les parcours d'excellence présentés en une — de la prépa ECG à la banque d'affaires, de la prépa MP au bureau d'études — ou explorez nos classements par filière.",
    },
}

NAV_ORDER = ["classements", "commerce", "ingenieurs", "design-architecture", "communication", "rh-gestion", "metiers"]

PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{meta}">{robots}
  <link rel="canonical" href="{site}/{slug}/">
  <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Le Journal des Écoles">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{meta}">
  <meta property="og:url" content="{site}/{slug}/">
  <meta property="og:image" content="{site}{ogimg}">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Hanken+Grotesk:ital,wght@0,300..700;1,300..700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/jde.css?v=3">

  <script type="application/ld+json">
{jsonld}
  </script>
</head>
<body>

  <!-- ================= TOP BAR ================= -->
  <div class="topbar">
    <div class="wrap">
      <span class="edition"><span id="edition-date">Samedi 18 juillet 2026</span><span class="ed-label"><i>◆</i>Édition digitale</span></span>
      <span class="tagline-top">Commerce&nbsp;· Ingénieurs&nbsp;· Design&nbsp;· Communication&nbsp;· RH</span>
      <a href="/#newsletter">S’abonner à la newsletter</a>
    </div>
  </div>

  <!-- ================= MASTHEAD (compact) ================= -->
  <header class="masthead">
    <div class="wrap">
      <div class="masthead-side">
        <b>France</b>
        Le média des études supérieures
      </div>
      <div class="brand">
        <p style="font-family:var(--serif);font-weight:700;color:var(--ink);line-height:.95;letter-spacing:.02em;text-transform:uppercase;">
          <a href="/" aria-label="Le Journal des Écoles — accueil">
            <span style="display:block;font-size:clamp(1.3rem,2.6vw,2rem);">Le Journal</span>
            <span style="display:block;font-size:clamp(1.7rem,3.4vw,2.65rem);letter-spacing:.03em;">des Écoles</span>
          </a>
        </p>
        <p class="tagline">Classements · Écoles · Masters · Métiers</p>
      </div>
      <div class="masthead-side right">
        <b>Fondé en 2026</b>
        Indépendant &amp; sans concession
      </div>
    </div>
  </header>

  <!-- ================= NAVIGATION ================= -->
  <nav class="nav" id="nav" aria-label="Navigation principale">
    <div class="wrap">
      <a class="nav-mono" href="/" aria-label="Le Journal des Écoles — accueil">J<em>D</em>E</a>
      <ul>
{navitems}
      </ul>
      <button class="search" type="button" id="search-open" aria-label="Rechercher" aria-haspopup="dialog">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.8-3.8"/></svg>
        <span>Rechercher</span>
      </button>
    </div>
  </nav>

  <main>
    <!-- ================= EN-TÊTE DE RUBRIQUE ================= -->
    <div class="rubrique-head">
      <div class="wrap">
        <nav class="breadcrumb" style="font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-soft);display:flex;flex-wrap:wrap;gap:.55em;margin-bottom:1.6rem;" aria-label="Fil d’Ariane">
          <a href="/">Accueil</a><i style="font-style:normal;color:var(--gold);">◆</i>
          <span>{h1_plain}</span>
        </nav>
        <span class="kicker">Rubrique</span>
        <h1>{h1}</h1>
        <p class="desc">{desc}</p>
      </div>
    </div>

    <!-- ================= ARTICLES ================= -->
    <section class="art-list" aria-label="Derniers articles de la rubrique">
      <div class="wrap">
{contenu}
      </div>
    </section>

    <!-- ================= NEWSLETTER ================= -->
    <section class="news" id="newsletter" aria-label="Newsletter">
      <div class="wrap">
        <div>
          <span class="kicker">La newsletter du Journal des Écoles</span>
          <h2>«&nbsp;L’Amphi&nbsp;», chaque jeudi matin</h2>
          <p class="sub">Classements, décryptages et conseils d’orientation, résumés en cinq minutes de lecture. Rien d’autre, promis.</p>
        </div>
        <div>
          <form action="#" method="post">
            <label class="sr-only" for="nl-email">Votre adresse e-mail</label>
            <input id="nl-email" type="email" name="email" placeholder="Votre adresse e-mail" required>
            <button type="submit">Je m’abonne</button>
          </form>
          <p class="rgpd">Un e-mail par semaine, zéro publicité déguisée. Désinscription en un clic, conformément au RGPD.</p>
        </div>
      </div>
    </section>
  </main>

  <!-- ================= FOOTER ================= -->
  <footer>
    <div class="foot-main">
      <div class="wrap">
        <div class="foot-brand">
          <p class="mono" aria-hidden="true">J<em>D</em>E</p>
          <p>Le média français des études supérieures. Classements exigeants, parcours décryptés et conseils d’orientation, écrits par une rédaction indépendante.</p>
          <p class="sig">Scientia potentia est.</p>
        </div>
        <nav aria-label="Univers">
          <h4>Univers</h4>
          <ul>
            <li><a href="/commerce/">Commerce &amp; Management</a></li>
            <li><a href="/ingenieurs/">Ingénieurs</a></li>
            <li><a href="/design-architecture/">Design &amp; Architecture</a></li>
            <li><a href="/communication/">Communication &amp; Médias</a></li>
            <li><a href="/rh-gestion/">RH &amp; Gestion</a></li>
          </ul>
        </nav>
        <nav aria-label="Classements et guides">
          <h4>Classements &amp; guides</h4>
          <ul>
            <li><a href="/classement-meilleures-ecoles-communication-france/">Écoles de communication</a></li>
            <li><a href="/classement-meilleures-ecoles-design-france/">Écoles de design</a></li>
            <li><a href="/classement-meilleures-ecoles-ingenieurs-france/">Écoles d’ingénieurs</a></li>
            <li><a href="/classement-meilleures-ecoles-commerce-france/">Écoles de commerce</a></li>
            <li><a href="/top-10-grandes-ecoles-commerce-hec-essec-escp/">HEC, ESSEC, ESCP&nbsp;: le trio</a></li>
            <li><a href="/metiers/">Parcours métiers</a></li>
          </ul>
        </nav>
        <nav aria-label="Le Journal">
          <h4>Le Journal</h4>
          <ul>
            <li><a href="/notre-histoire/">À propos &amp; rédaction</a></li>
            <li><a href="/classement-meilleures-ecoles-commerce-france/#methodologie">Méthodologie des classements</a></li>
            <li><a href="/notre-histoire/#independance">Charte éditoriale</a></li>
            <li><a href="/contact-partenariats/">Contact &amp; partenariats</a></li>
            <li><a href="/#">Mentions légales</a></li>
            <li><a href="/#">Politique de confidentialité</a></li>
          </ul>
        </nav>
      </div>
    </div>
    <div class="foot-bottom">
      <div class="wrap">
        <span>© 2026 Le Journal des Écoles — Tous droits réservés</span>
        <span class="soc">
          <a href="#">Instagram</a>
          <a href="#">TikTok</a>
          <a href="#">LinkedIn</a>
          <a href="#">YouTube</a>
        </span>
        <span class="indep">Média indépendant&nbsp;: aucune école ne rémunère sa place dans nos classements.</span>
      </div>
    </div>
  </footer>

  <!-- ================= RECHERCHE (overlay) ================= -->
  <div class="search-overlay" id="search-overlay" role="dialog" aria-modal="true" aria-label="Recherche">
    <button class="close" type="button" id="search-close"><i>✕</i> Fermer</button>
    <div class="inner">
      <span class="kicker">Rechercher sur Le Journal des Écoles</span>
      <form action="/recherche/" method="get" role="search">
        <label class="sr-only" for="search-input">Votre recherche</label>
        <input id="search-input" type="search" name="q" placeholder="Une école, un master, un métier…" autocomplete="off">
        <button type="submit" class="sr-only">Rechercher</button>
      </form>
      <p class="hint"><b>Entrée</b> pour rechercher — <b>Échap</b> pour fermer</p>
      <ul class="live-results" id="live-results"></ul>
      <div class="sug">
        <span>Recherches populaires</span>
        <a href="/recherche/?q=classement+écoles+de+commerce">Classement écoles de commerce</a>
        <a href="/recherche/?q=Polytechnique">Polytechnique</a>
        <a href="/recherche/?q=CELSA">CELSA</a>
        <a href="/recherche/?q=ROI">Indice ROI</a>
        <a href="/recherche/?q=alternance">Alternance</a>
      </div>
    </div>
  </div>

  <script src="/assets/search.js?v=3"></script>
  <script src="/assets/site.js?v=3" defer></script>
  <script>
    (function(){{
      var nav = document.getElementById('nav');
      var onScroll = function(){{ nav.classList.toggle('scrolled', window.scrollY > 220); }};
      window.addEventListener('scroll', onScroll, {{ passive:true }});
      onScroll();
    }})();
    (function(){{
      var overlay = document.getElementById('search-overlay');
      var openBtn = document.getElementById('search-open');
      var closeBtn = document.getElementById('search-close');
      var input = document.getElementById('search-input');
      function open(){{ overlay.classList.add('open'); document.body.style.overflow='hidden'; setTimeout(function(){{ input.focus(); }}, 80); }}
      function close(){{ overlay.classList.remove('open'); document.body.style.overflow=''; openBtn.focus(); }}
      openBtn.addEventListener('click', open);
      closeBtn.addEventListener('click', close);
      document.addEventListener('keydown', function(e){{ if(e.key === 'Escape' && overlay.classList.contains('open')) close(); }});
      JDESearch.bindOverlay(input, document.getElementById('live-results'));
    }})();
  </script>
</body>
</html>
"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build():
    articles = json.loads((ROOT / "assets/articles.json").read_text(encoding="utf-8"))
    for slug, r in RUBRIQUES.items():
        arts = [a for a in articles if slug in a["rubriques"]]
        h1_plain = r["h1"]
        url = f"{SITE}/{slug}/"

        # — contenu : liste d'articles ou état vide
        if arts:
            rows = []
            for a in arts:
                rows.append(f"""        <article class="art-row">
          <a class="thumb" href="{a['url']}" aria-hidden="true" tabindex="-1">
            <img loading="lazy" src="{a['image']}" alt="{esc(a['alt'])}" width="800" height="500">
          </a>
          <div>
            <span class="cat">{esc(a['cat'])}</span>
            <h2><a href="{a['url']}">{esc(a['title'])}</a></h2>
            <p class="excerpt">{esc(a['excerpt'])}</p>
            <p class="meta">Par Charlotte Montant<i>◆</i><time datetime="{a['date']}">{a['dateLabel']}</time><i>◆</i>Lecture {a['minutes']} min</p>
          </div>
        </article>""")
            contenu = "\n".join(rows)
            ogimg = arts[0]["image"]
        else:
            others = "\n            ".join(
                f'<a href="/{s}/">{RUBRIQUES[s]["h1"]}</a>'
                for s in NAV_ORDER if s != slug and RUBRIQUES[s]["index"]
            )
            contenu = f"""        <div class="rubrique-empty">
          <p>{esc(r['empty'])}</p>
          <div class="sug">
            {others}
            <a href="/#parcours">Les parcours en une</a>
          </div>
        </div>"""
            ogimg = "/assets/img/bibliotheque-ancienne-grandes-ecoles.webp"

        # — navigation avec onglet actif
        navitems = "\n".join(
            f'        <li><a href="/{s}/"{" aria-current=\"page\"" if s == slug else ""}>{RUBRIQUES[s]["nav"]}</a></li>'
            for s in NAV_ORDER
        )

        # — JSON-LD : CollectionPage + Breadcrumb + ItemList
        graph = [
            {
                "@type": "CollectionPage",
                "@id": f"{url}#page",
                "url": url,
                "name": r["h1"],
                "description": r["desc"],
                "inLanguage": "fr-FR",
                "isPartOf": {"@id": f"{SITE}/#website"},
                "publisher": {"@id": f"{SITE}/#organization"},
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{url}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE}/"},
                    {"@type": "ListItem", "position": 2, "name": r["h1"]},
                ],
            },
        ]
        if arts:
            graph[0]["mainEntity"] = {"@id": f"{url}#liste"}
            graph.append({
                "@type": "ItemList",
                "@id": f"{url}#liste",
                "name": f"Derniers articles — {r['h1']}",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": a["title"], "url": f"{SITE}{a['url']}"}
                    for i, a in enumerate(arts)
                ],
            })
        jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph},
                            ensure_ascii=False, indent=2)
        jsonld = "\n".join("  " + line for line in jsonld.splitlines())

        html = PAGE.format(
            title=esc(r["title"]), meta=esc(r["meta"]),
            robots="" if r["index"] else '\n  <meta name="robots" content="noindex, follow">',
            site=SITE, slug=slug, ogimg=ogimg, jsonld=jsonld,
            navitems=navitems, h1=r["h1"], h1_plain=h1_plain, desc=r["desc"],
            contenu=contenu,
        )
        out = ROOT / slug / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"  /{slug}/ — {len(arts)} article(s){' (noindex)' if not r['index'] else ''}")


if __name__ == "__main__":
    build()
    print("Pages de rubrique générées ✓")
