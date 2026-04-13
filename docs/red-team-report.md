# Rapport Red Team — Pentest (mode vuln) (1ère personne)

Auteur (Red Team) : **Keis Aissaoui**  
Projet : **Cyber Challenge — Façade Moodle / SaaS** (SSI 2025–2026)  
Âge / profil : **22 ans**, débutant en pentest (j’apprends en faisant)  
Équipe : Keis Aissaoui • Tristan Hardouin  
À compléter : filière / école / année universitaire.

## 0) Comment j’ai abordé le test (en mode étudiant)
Je ne suis pas pentester pro, donc j’ai fait “simple mais efficace” :
- je navigue comme un utilisateur normal ;
- j’ouvre DevTools (Network / Storage) ;
- je teste les trucs classiques : paramètres, formulaires, IDs dans l’URL ;
- je note ce qui marche, et j’écris un PoC facile à rejouer.

Je me suis basé sur `docs/vulnerabilites.md` pour avoir une liste claire des failles à chercher.

## 1) Reconnaissance (ce que j’ai vu rapidement)
### 1.1 Pages visibles
Je vois surtout :
- `/login` (formulaire),
- `/dashboard` (après login),
- `/courses`, `/agenda`, `/messages`, `/profile`, `/search`.

### 1.2 Indices “de l’extérieur”
Ce que je vérifie direct :
- Est‑ce que l’app réaffiche ce que je tape (souvent XSS) ?
- Est‑ce qu’il y a des IDs dans l’URL (souvent IDOR) ?
- Est‑ce qu’il y a un paramètre `next` au login (souvent open redirect) ?
- Est‑ce qu’il y a des endpoints admin/api devinables (`/admin`, `/api`) ?

## 2) Vulnérabilités que j’ai réussies à exploiter (PoC)
> Tous les PoC ci‑dessous sont pour l’app de démo uniquement.

### 2.1 SQLi login (bypass)
- **Je l’ai trouvé comment** : sur un login je tente des strings SQL classiques.
- **Où** : `POST /login` (mode `vuln`)
- **PoC** :
  - username : `x' OR 1=1 -- `
  - password : `x`
- **Ce que j’observe** : je suis redirigé vers `/dashboard` sans avoir le vrai mdp.
- **Impact (en mots simples)** : je peux rentrer comme si j’avais un compte.
- **Fix attendu** : requête paramétrée + hash (mode `secure`).

### 2.2 Open redirect (phishing)
- **Je l’ai trouvé comment** : j’ai vu le paramètre `next` au login.
- **Où** : `/login?next=...` (mode `vuln`)
- **PoC** : ouvrir `/login?next=https://example.com`, se connecter, et regarder la redirection.
- **Impact** : après login, on peut envoyer la victime ailleurs (phishing).
- **Fix attendu** : accepter uniquement un chemin interne (mode `secure`).

### 2.3 XSS réfléchie sur `/search`
- **Je l’ai trouvé comment** : page de recherche = souvent reflet de ce qu’on tape.
- **Où** : `GET /search?q=...` (mode `vuln`)
- **PoC** : `/search?q=<img src=x onerror=alert(1)>`
- **Impact** : exécution JS juste en ouvrant le lien.
- **Fix attendu** : échapper la sortie + CSP (mode `secure`).

### 2.4 XSS stockée sur les notes (`/agenda`)
- **Je l’ai trouvé comment** : formulaire “notes” → je poste du HTML et je recharge la page.
- **Où** : `POST /agenda` puis `GET /agenda` (mode `vuln`)
- **PoC** :
  ```html
  <img src=x onerror=alert(1)>
  ```
- **Impact** : ça s’exécute à chaque fois qu’on ouvre l’agenda.
- **Fix attendu** : ne jamais rendre “safe” un input utilisateur (mode `secure`).

### 2.5 XSS stockée sur la bio (`/profile`)
- **Je l’ai trouvé comment** : champ “bio” → je tente une balise simple.
- **Où** : `POST /profile` puis `GET /profile` (mode `vuln`)
- **PoC** :
  ```html
  <svg onload=alert(1)>
  ```
- **Impact** : exécution persistante sur la page profil.
- **Fix attendu** : échappement + validation longueur (mode `secure`).

### 2.6 IDOR sur les messages (`/messages/<id>`)
- **Je l’ai trouvé comment** : l’URL a un ID numérique, donc j’incrémente.
- **Où** : `GET /messages/<id>` (mode `vuln`)
- **PoC** : je teste `/messages/1`, puis `/messages/2`, etc.
- **Impact** : je peux lire un message qui n’est pas à moi si l’ID existe.
- **Fix attendu** : filtrer avec `AND user_id = ?` (mode `secure`).

### 2.7 CSRF sur les POST
- **Je l’ai trouvé comment** : je regarde si un token CSRF existe dans les formulaires.
- **Où** : `POST /agenda`, `POST /profile`, `POST /logout` (mode `vuln`)
- **PoC** : envoyer un POST sans token (curl / petit HTML externe) et constater que ça marche.
- **Impact** : actions possibles “à l’insu” de l’utilisateur si sa session est active.
- **Fix attendu** : token obligatoire (mode `secure`).

### 2.8 Endpoint sensible `/api/users` (selon droits)
- **Je l’ai trouvé comment** : j’ai testé des URLs classiques `/api/users`.
- **Où** : `GET /api/users`
- **PoC** : ouvrir l’URL connecté.
- **Impact** : fuite de données (selon mode/champs).
- **Fix attendu** : contrôle d’accès strict + limiter les champs (mode `secure`).

## 3) Priorités (si je devais corriger en premier)
Si je devais conseiller la Blue Team :
1) SQLi login
2) XSS stockée
3) IDOR
4) CSRF
5) Open redirect + endpoints qui exposent trop d’infos

## 4) Annexes
- Checklist : `docs/vulnerabilites.md`
- Démo rapide : `docs/demo.md`
