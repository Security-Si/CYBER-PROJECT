# Rapport Blue Team — Façade Moodle (SSI 2025-2026)

Équipe : Keis Aissaoui • Tristan Hardouin  
À compléter : filière / école.

## 1) Contexte & périmètre
- Application web “façade Moodle” simplifiée : login + agenda + notes.
- Back-end simulé : Flask + SQLite.
- Deux modes : `vuln` (intentionnel) et `secure` (remédiation).

## 2) Choix techniques
- Front : templates Jinja2, CSS “Moodle-like”.
- Back : Python / Flask.
- DB : SQLite (fichier `instance/app.db`).

## 3) Vulnérabilités intégrées (mode `vuln`)
### 3.1 SQL Injection (auth)
- Cause : concaténation de chaînes dans la requête de login.
- Impact : contournement authentification.
- Exemple PoC : username `anything' OR '1'='1` + mot de passe quelconque.

### 3.2 Stored XSS (notes)
- Cause : le contenu des notes est rendu comme “safe” dans le template.
- Impact : exécution de JS au chargement de la page agenda.
- Exemple PoC : `<img src=x onerror=alert(document.domain)>`

### 3.3 Open Redirect
- Cause : paramètre `next` non validé en mode vulnérable.
- Impact : redirection vers domaine externe après login.

### 3.4 Auth faible / anti-bruteforce absent
- Aucun rate-limit en mode vulnérable.

## 4) Mesures de sécurité (mode `secure`)
- Requêtes SQL paramétrées (login).
- Hash de mots de passe + vérification via `werkzeug.security`.
- CSRF token (POST).
- Rate-limit basique (429) sur endpoint login.
- Anti open-redirect (validation du `next`).
- Durcissement cookies de session (HttpOnly, SameSite=Lax).

## 5) Tests & validation
- Scénarios : login OK/KO, tentative de SQLi, XSS, CSRF.
- Résultats attendus : vuln exploitable en `vuln`, non exploitable en `secure`.

## 6) Limites & améliorations
- CSP + headers sécurité (Content-Security-Policy, X-Frame-Options, etc.).
- Rate-limit persistant (Redis) + lockout par compte.
- HTTPS via reverse-proxy (Nginx/Caddy) + HSTS.
