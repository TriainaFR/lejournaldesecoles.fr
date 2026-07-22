#!/usr/bin/env node
/**
 * Soumission IndexNow pour lejournaldesecoles.fr
 *
 *   npm run indexnow                  → soumet toutes les URL du sitemap
 *   npm run indexnow -- --new         → soumet les URL modifiées depuis le dernier envoi
 *   npm run indexnow -- <url> [<url>] → soumet uniquement ces URL
 *   npm run indexnow -- --dry         → affiche ce qui serait envoyé, sans rien envoyer
 *
 * Un seul appel suffit : l'API IndexNow partage la soumission entre tous les
 * moteurs partenaires (Bing - donc Copilot, qui s'appuie sur l'index Bing -,
 * Yandex, Seznam, Naver). Google ne participe pas à IndexNow : pour lui, la
 * découverte passe par le sitemap et la Search Console.
 */
import { readFile, readdir, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const RACINE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const HOTE = "lejournaldesecoles.fr";
const SITE = `https://${HOTE}`;
const SUIVI = path.join(RACINE, "scripts", ".indexnow-state.json");

const args = process.argv.slice(2);
const dryRun = args.includes("--dry");
const nouveautes = args.includes("--new");
const urlsManuelles = args.filter((a) => a.startsWith("http"));

/** Retrouve le fichier de clé IndexNow (32 caractères hexadécimaux) à la racine. */
async function trouverCle() {
  const fichiers = await readdir(RACINE);
  const cle = fichiers.find((f) => /^[0-9a-f]{32}\.txt$/i.test(f));
  if (!cle) {
    throw new Error(
      "Clé IndexNow introuvable à la racine du dépôt (fichier <clé>.txt attendu).\n" +
      "   Générer une clé : node -e \"console.log(require('crypto').randomBytes(16).toString('hex'))\"\n" +
      "   puis créer un fichier <clé>.txt contenant cette clé, et le déployer."
    );
  }
  return cle.replace(/\.txt$/i, "");
}

/** Extrait les <loc> du sitemap local. */
async function urlsDuSitemap() {
  const xml = await readFile(path.join(RACINE, "sitemap.xml"), "utf8");
  return [...xml.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/g)].map((m) => m[1]);
}

/** Empreinte du contenu déployé de chaque page, pour repérer les modifications. */
async function empreintes(urls) {
  const { createHash } = await import("node:crypto");
  const etat = {};
  for (const url of urls) {
    const chemin = url.replace(SITE, "").replace(/^\/|\/$/g, "");
    const fichier = chemin === "" ? "index.html" : path.join(chemin, "index.html");
    const complet = path.join(RACINE, fichier);
    if (existsSync(complet)) {
      etat[url] = createHash("sha1").update(await readFile(complet)).digest("hex").slice(0, 12);
    }
  }
  return etat;
}

async function main() {
  const cle = await trouverCle();
  const toutes = await urlsDuSitemap();
  let urls = urlsManuelles.length ? urlsManuelles : toutes;

  // --new : ne garder que les pages dont le contenu a changé depuis le dernier envoi
  const etatActuel = await empreintes(toutes);
  if (nouveautes && !urlsManuelles.length) {
    let precedent = {};
    if (existsSync(SUIVI)) precedent = JSON.parse(await readFile(SUIVI, "utf8"));
    urls = toutes.filter((u) => etatActuel[u] && etatActuel[u] !== precedent[u]);
    if (!urls.length) {
      console.log("Aucune page modifiée depuis la dernière soumission. Rien à envoyer.");
      return;
    }
  }

  const horsSite = urls.filter((u) => !u.startsWith(SITE));
  if (horsSite.length) throw new Error(`URL hors du domaine ${HOTE} :\n   ${horsSite.join("\n   ")}`);

  console.log(`IndexNow · ${urls.length} URL à soumettre pour ${HOTE}`);
  urls.forEach((u) => console.log("   " + u.replace(SITE, "") || "   /"));

  if (dryRun) {
    console.log("\n--dry : rien n'a été envoyé.");
    return;
  }

  // Vérifie que le fichier de clé est bien servi en production avant de soumettre.
  const verif = await fetch(`${SITE}/${cle}.txt`, { headers: { "User-Agent": "LeJournalDesEcoles-IndexNow" } });
  const contenu = (await verif.text()).trim();
  if (!verif.ok || contenu !== cle) {
    throw new Error(`Le fichier de clé ${SITE}/${cle}.txt n'est pas servi correctement (statut ${verif.status}). Déployez-le avant de soumettre.`);
  }

  const reponse = await fetch("https://api.indexnow.org/indexnow", {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify({ host: HOTE, key: cle, keyLocation: `${SITE}/${cle}.txt`, urlList: urls }),
  });

  const messages = {
    200: "OK - URL acceptées.",
    202: "Accepté - URL reçues, validation de la clé en cours.",
    400: "Requête invalide (format du corps JSON).",
    403: "Clé refusée : le fichier de clé ne correspond pas.",
    422: "URL refusées : elles ne correspondent pas au domaine, ou la clé est incohérente.",
    429: "Trop de soumissions : réessayez plus tard.",
  };
  const libelle = messages[reponse.status] || "Réponse inattendue.";

  if (reponse.status === 200 || reponse.status === 202) {
    await writeFile(SUIVI, JSON.stringify(etatActuel, null, 2) + "\n", "utf8");
    console.log(`\n✓ ${reponse.status} · ${libelle}`);
    console.log("  Relayé aux moteurs partenaires : Bing (et Copilot, qui s'appuie sur son index), Yandex, Seznam, Naver.");
    console.log("  Rappel : Google ne participe pas à IndexNow (sitemap + Search Console).");
  } else {
    console.error(`\n✗ ${reponse.status} · ${libelle}`);
    console.error("  " + (await reponse.text()).slice(0, 300));
    process.exitCode = 1;
  }
}

main().catch((e) => {
  console.error("✗ " + e.message);
  process.exitCode = 1;
});
