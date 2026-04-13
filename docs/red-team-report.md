# Rapport Red Team — Pentest (mode `APP_MODE=vuln`)

Auteur (Red Team) : **Keis Aissaoui**  
Projet : **Cyber Challenge — Façade Moodle / SaaS** (SSI 2025–2026)  
Âge / profil : **22 ans**, débutant en pentest (j’apprends en faisant)  
Équipe : Keis Aissaoui • Tristan Hardouin  
À compléter : filière / école / année universitaire.

---

## Table des matières
1. Résumé & périmètre  
2. Méthodologie (reconnaissance → tests → PoC)  
3. Résultats (11 vulnérabilités)  
4. Priorisation (risque)  
5. Recommandations  
6. Annexes  

---

## 1) Résumé (ce que j’ai trouvé)
Sur le mode `APP_MODE=vuln`, j’ai réussi à identifier **11 vulnérabilités** (simples à moyennes), dont plusieurs exploitables immédiatement : SQLi sur le login, XSS (stockée + réfléchie), IDOR sur les messages, CSRF, open redirect et exposition de données via pages/API.

Je détaille ci‑dessous comment je les ai trouvées “de l’extérieur”, avec des PoC reproductibles.

### 1.1 Périmètre
- Mode testé : `APP_MODE=vuln`
- Pages : `/login`, `/dashboard`, `/courses`, `/agenda`, `/messages`, `/profile`, `/search`
- Endpoints sensibles : `/admin/users`, `/api/users`

### 1.2 Hypothèses de départ
- L’objectif est pédagogique : certaines failles sont **volontaires**.
- Les tests sont réalisés uniquement sur l’application de démo.

---

## 2) Comment j’ai abordé le test (en mode étudiant)
Je ne suis pas pentester pro, donc j’ai fait “simple mais efficace” :
- je navigue comme un utilisateur normal ;
- j’ouvre DevTools (Network / Storage) ;
- je teste les trucs classiques : paramètres, formulaires, IDs dans l’URL ;
- je note ce qui marche, et j’écris un PoC facile à rejouer.

Je me suis basé sur `docs/vulnerabilites.md` pour avoir une liste claire des failles à chercher.

### 2.1 Reconnaissance (ce que j’ai vu rapidement)
Je vois surtout :
- `/login` (formulaire),
- `/dashboard` (après login),
- `/courses`, `/agenda`, `/messages`, `/profile`, `/search`.

### 2.2 Indices “de l’extérieur”
Ce que je vérifie direct :
- Est‑ce que l’app réaffiche ce que je tape (souvent XSS) ?
- Est‑ce qu’il y a des IDs dans l’URL (souvent IDOR) ?
- Est‑ce qu’il y a un paramètre `next` au login (souvent open redirect) ?
- Est‑ce qu’il y a des endpoints admin/api devinables (`/admin`, `/api`) ?

---

## 3) Résultats — 11 vulnérabilités (détails & PoC)
> Tous les PoC ci‑dessous sont pour l’app de démo uniquement.

### 3.1 Tableau récapitulatif (rapide)
| ID | Vulnérabilité | Endpoint | Gravité (estimation) |
|---:|---|---|---|
| V1 | SQL Injection (auth bypass) | `POST /login` | Critique |
| V2 | Open Redirect | `/login?next=...` | Moyenne |
| V3 | XSS réfléchie | `GET /search?q=...` | Élevée |
| V4 | XSS stockée (notes) | `POST/GET /agenda` | Critique |
| V5 | XSS stockée (bio) | `POST/GET /profile` | Élevée |
| V6 | IDOR messages | `GET /messages/<id>` | Élevée |
| V7 | CSRF (POST) | `POST /agenda|/profile|/logout` | Élevée |
| V8 | Data exposure (API) | `GET /api/users` | Moyenne |
| V9 | Broken access control (admin) | `GET /admin/users` | Élevée |
| V10 | Secrets en clair (UI admin) | `GET /admin/users` | Critique |
| V11 | Bruteforce possible | `POST /login` | Moyenne |

### 3.2 Détails vulnérabilité par vulnérabilité

#### V1 — SQLi login (bypass)
- **Je l’ai trouvé comment** : sur un login je tente des strings SQL classiques.
- **Où** : `POST /login` (mode `vuln`)
- **PoC** :
  - Username : `x' OR 1=1 -- `
  - Password : `x`
- **Ce que j’observe** : je suis redirigé vers `/dashboard` sans avoir le vrai mdp.
- **Impact (en mots simples)** : je peux rentrer comme si j’avais un compte.
- **Fix attendu** : requête paramétrée + hash (mode `secure`).

#### V2 — Open redirect (phishing)
- **Je l’ai trouvé comment** : j’ai vu le paramètre `next` au login.
- **Où** : `/login?next=...` (mode `vuln`)
- **PoC** : ouvrir `/login?next=https://example.com`, se connecter, et regarder la redirection.
- **Impact** : après login, on peut envoyer la victime ailleurs (phishing).
- **Fix attendu** : accepter uniquement un chemin interne (mode `secure`).

#### V3 — XSS réfléchie sur `/search`
- **Je l’ai trouvé comment** : page de recherche = souvent reflet de ce qu’on tape.
- **Où** : `GET /search?q=...` (mode `vuln`)
- **PoC** : `/search?q=<img src=x onerror=alert(1)>`
- **Impact** : exécution JS juste en ouvrant le lien.
- **Fix attendu** : échapper la sortie + CSP (mode `secure`).

#### V4 — XSS stockée sur les notes (`/agenda`)
- **Je l’ai trouvé comment** : formulaire “notes” → je poste du HTML et je recharge la page.
- **Où** : `POST /agenda` puis `GET /agenda` (mode `vuln`)
- **PoC** :
  ```html
  <img src=x onerror=alert(1)>
  ```
- **Impact** : ça s’exécute à chaque fois qu’on ouvre l’agenda.
- **Fix attendu** : ne jamais rendre “safe” un input utilisateur (mode `secure`).

#### V5 — XSS stockée sur la bio (`/profile`)
- **Je l’ai trouvé comment** : champ “bio” → je tente une balise simple.
- **Où** : `POST /profile` puis `GET /profile` (mode `vuln`)
- **PoC** :
  ```html
  <svg onload=alert(1)>
  ```
- **Impact** : exécution persistante sur la page profil.
- **Fix attendu** : échappement + validation longueur (mode `secure`).

#### V6 — IDOR sur les messages (`/messages/<id>`)
- **Je l’ai trouvé comment** : l’URL a un ID numérique, donc j’incrémente.
- **Où** : `GET /messages/<id>` (mode `vuln`)
- **PoC** : je teste `/messages/1`, puis `/messages/2`, etc.
- **Impact** : je peux lire un message qui n’est pas à moi si l’ID existe.
- **Fix attendu** : filtrer avec `AND user_id = ?` (mode `secure`).

#### V7 — CSRF sur les POST
- **Je l’ai trouvé comment** : je regarde si un token CSRF existe dans les formulaires.
- **Où** : `POST /agenda`, `POST /profile`, `POST /logout` (mode `vuln`)
- **PoC** : envoyer un POST sans token (curl / petit HTML externe) et constater que ça marche.
- **Impact** : actions possibles “à l’insu” de l’utilisateur si sa session est active.
- **Fix attendu** : token obligatoire (mode `secure`).

#### V8 — Exposition de données via `/api/users` (endpoint JSON)
- **Je l’ai trouvé comment** : j’ai testé des URLs classiques `/api/users`.
- **Où** : `GET /api/users`
- **PoC** : ouvrir l’URL connecté.
- **Impact** : fuite de données en JSON (utilisateurs/roles + parfois champs sensibles en `vuln`).
- **Fix attendu** : contrôle d’accès strict + limiter les champs (mode `secure`).

#### V9 — Contrôle d’accès faible sur `/admin/users`
- **Je l’ai trouvé comment** : j’ai essayé des URLs évidentes `/admin/users`.
- **Où** : `GET /admin/users` (mode `vuln`)
- **PoC** : se connecter puis ouvrir `/admin/users`.
- **Impact** : exposition d’informations internes (liste utilisateurs, rôles…).
- **Fix attendu** : réserver au rôle admin/teacher (mode `secure`).

#### V10 — Exposition de mots de passe de test (via UI admin)
- **Je l’ai trouvé comment** : sur `/admin/users`, je regarde si des champs sensibles apparaissent.
- **Où** : `/admin/users` (mode `vuln`)
- **PoC** : observer l’affichage d’un champ type `password_plain`.
- **Impact** : fuite directe de credentials de test.
- **Fix attendu** : ne jamais exposer ce champ ; le retirer/masquer (mode `secure`).

#### V11 — Bruteforce possible (absence de rate‑limit en `vuln`)
- **Je l’ai trouvé comment** : je fais plusieurs tentatives de login en boucle.
- **Où** : `POST /login` (mode `vuln`)
- **PoC** : enchaîner des logins invalides rapidement et constater l’absence de blocage.
- **Impact** : attaque par force brute / dictionnaire facilitée.
- **Fix attendu** : rate‑limit / verrouillage temporaire (mode `secure`).

---

## 4) Priorités (si je devais corriger en premier)
Si je devais conseiller la Blue Team :
1) SQLi login
2) XSS stockée
3) IDOR
4) CSRF
5) Open redirect + endpoints qui exposent trop d’infos

---

## 5) Ce que je recommande (simple et concret)
- Mettre `APP_MODE=secure` pour tout déploiement public.
- Garder `SECRET_KEY` fort et stable en prod.
- Bloquer `/admin/users` et `/api/users` (RBAC) + réduire les champs renvoyés.
- Échapper toutes les sorties utilisateur (et éviter tout rendu “safe”).
- CSRF sur toutes les actions d’écriture.
- Rate‑limit robuste (idéalement partagé) sur login.

---

## 6) Annexes
- Checklist : `docs/vulnerabilites.md`
- Démo rapide : `docs/demo.md`
