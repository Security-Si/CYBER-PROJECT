# Rapport Red Team — Pentest (mode vuln)

Auteur (Red Team) : **Keis Aissaoui**  
Projet : **Cyber Challenge — Façade Moodle / SaaS** (SSI 2025–2026)  
Équipe : Keis Aissaoui • Tristan Hardouin  
À compléter : filière / école / année universitaire.

## 0) Résumé exécutif
Le pentest vise à identifier des vulnérabilités web classiques sur le **mode `APP_MODE=vuln`** et à fournir :
- des preuves de concept (PoC) reproductibles ;
- une estimation d’impact ;
- des recommandations de remédiation.

Les vulnérabilités attendues sont listées dans `docs/vulnerabilites.md`. Ce rapport documente celles qui sont exploitables et comment les trouver “de l’extérieur”.

## 1) Portée et méthodologie
### 1.1 Portée
- Application web locale (ou déployée) — pages : `/login`, `/dashboard`, `/courses`, `/agenda`, `/messages`, `/profile`, `/search`.
- Endpoints sensibles : `/admin/users`, `/api/users`.

### 1.2 Méthodologie (pragmatique)
1) Reconnaissance : navigation + DevTools (Network/Storage), endpoints évidents, paramètres.
2) Tests rapides : injections, XSS, contrôles d’accès, CSRF, redirections.
3) Exploitation : PoC minimal + observation d’impact.
4) Recommandations : fix “root cause” + défense en profondeur.

## 2) Reconnaissance (observations)
### 2.1 Surfaces d’attaque
- Formulaires : login (`/login`), notes (`/agenda`), profil (`/profile`).
- Paramètres : `next` (login), `q` (search), IDs dans les URLs (`/messages/<id>`, `/courses/<id>`).
- Pages “administration” non listées dans la navbar (mais devinables) : `/admin/users`, `/api/users`.

### 2.2 Indices externes utiles
- Cookies session présents après login.
- Réponses HTML réaffichant des entrées utilisateur (notes/bio/search).
- Endpoints JSON (`/api/users`) faciles à tester.

## 3) Vulnérabilités confirmées (avec PoC)

> Convention : les PoC ci-dessous sont à lancer **uniquement** contre cette application de démo.

### VULN‑01 — SQL Injection (bypass login)
- **Référence checklist** : (1)
- **Endpoint** : `POST /login`
- **Impact** : accès au workspace sans mot de passe, élévation de privilèges possible selon la première ligne retournée.
- **PoC** :
  - Username : `x' OR 1=1 -- `
  - Password : `x`
- **Résultat observé** : redirection vers `/dashboard`.
- **Recommandation** : requêtes paramétrées + hash (déjà appliqué en mode secure).

### VULN‑02 — Open Redirect (paramètre next)
- **Référence checklist** : (2)
- **Endpoint** : `/login?next=...`
- **Impact** : phishing (redirection vers site externe après authentification).
- **PoC** :
  1) ouvrir `/login?next=https://example.com`
  2) se connecter
  3) observer la redirection externe
- **Recommandation** : autoriser uniquement des chemins relatifs (déjà appliqué en secure).

### VULN‑03 — XSS réfléchie (`/search`)
- **Référence checklist** : (6)
- **Endpoint** : `GET /search?q=...`
- **Impact** : exécution JS à l’ouverture d’un lien (attaque par partage d’URL).
- **PoC** : `/search?q=<img src=x onerror=alert(1)>`
- **Recommandation** : échapper la sortie + CSP (secure).

### VULN‑04 — XSS stockée (notes agenda)
- **Référence checklist** : (4)
- **Endpoint** : `POST /agenda` puis `GET /agenda`
- **Impact** : exécution JS persistante (vol de session si cookies accessibles, actions à la place de la victime, etc.).
- **PoC** (dans une note) :
  ```html
  <img src=x onerror=alert(1)>
  ```
- **Recommandation** : ne jamais rendre “safe” du contenu utilisateur ; conserver l’échappement.

### VULN‑05 — XSS stockée (bio profil)
- **Référence checklist** : (5)
- **Endpoint** : `POST /profile` puis `GET /profile`
- **Impact** : exécution JS persistante sur le profil.
- **PoC** :
  ```html
  <svg onload=alert(1)>
  ```
- **Recommandation** : échappement strict + validation longueur.

### VULN‑06 — IDOR (lecture messages par ID)
- **Référence checklist** : (13)
- **Endpoint** : `GET /messages/<id>`
- **Impact** : lecture de données d’un autre utilisateur si l’attaquant devine un ID existant.
- **PoC** :
  1) se connecter
  2) ouvrir `/messages/1`
  3) remplacer l’ID dans l’URL (`/messages/2`, `/messages/3`, …)
  4) constater l’accès à un message non destiné à l’utilisateur courant
- **Recommandation** : filtrer par `user_id` (secure).

### VULN‑07 — CSRF (actions POST)
- **Référence checklist** : (17)
- **Endpoints** : `POST /agenda`, `POST /profile`, `POST /logout`
- **Impact** : actions déclenchées à l’insu de l’utilisateur (si session active).
- **PoC** : envoyer un POST sans token (curl / page HTML externe) et observer que la requête passe en `vuln`.
- **Recommandation** : token CSRF obligatoire (secure).

### VULN‑08 — Exposition de données (UI + API)
- **Références checklist** : (14), (15), (18), (19), (8)
- **Endpoints** : `GET /admin/users`, `GET /api/users`
- **Impact** : fuite d’informations (utilisateurs, rôles, champs sensibles selon mode).
- **PoC** : ouvrir `/api/users` connecté ; ouvrir `/admin/users` si accessible.
- **Recommandation** : contrôle d’accès strict + limiter les champs renvoyés (secure).

## 4) Synthèse des risques
### 4.1 Priorités
1) **SQLi login** : accès complet à l’application.
2) **XSS (stored/reflected)** : exécution de code côté client.
3) **IDOR** : brèche de confidentialité.
4) **CSRF** : actions non voulues.
5) **Open redirect / data exposure** : phishing + fuite d’infos.

## 5) Recommandations (actionnables)
- Forcer `APP_MODE=secure` pour tout déploiement public.
- `SECRET_KEY` fort et stable (rotation si fuite).
- Contrôles d’accès “deny by default” (admin/API).
- Validation stricte entrées + échappement sorties (pas de rendu “safe”).
- Mettre un vrai rate-limit partagé (Redis) si déploiement multi‑instance.
- Ajouter journalisation minimale des tentatives d’attaque (login, accès admin, erreurs 4xx/5xx).

## 6) Annexes (preuves)
- Liste complète : `docs/vulnerabilites.md`
- Scénarios rapides : `docs/demo.md`
