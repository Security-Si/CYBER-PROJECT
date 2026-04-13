# Rapport Blue Team — Conception, sécurisation et remédiation

Auteur (Blue Team) : **Tristan Hardouin**  
Projet : **Cyber Challenge — Façade Moodle / SaaS** (SSI 2025–2026)  
Équipe : Keis Aissaoui • Tristan Hardouin  
À compléter : filière / école / année universitaire.

## 0) Résumé exécutif
L’objectif Blue Team est double :
1) produire une application crédible (login + workspace) avec un mode **vulnérable** exploitable pour le challenge ;
2) fournir un mode **sécurisé** (“secure”) qui corrige les failles, et démontrer que les attaques simples ne passent plus.

Les vulnérabilités et scénarios d’attaque sont centralisés dans `docs/vulnerabilites.md`.

## 1) Périmètre
### 1.1 Application
- Backend : Flask (Python) + SQLite.
- Front : templates HTML (Jinja2) + assets statiques.
- Pages principales : `/dashboard`, `/courses`, `/agenda`, `/messages`, `/profile`, `/search`, `/api/users`, `/admin/users`.
- Deux modes :
  - `APP_MODE=vuln` : surface d’attaque volontairement plus large.
  - `APP_MODE=secure` : contre‑mesures activées.

### 1.2 Hors périmètre
- Intégration de paiement réelle (Stripe) : non implémentée.
- MFA/SSO, gestion fine des logs, SIEM : non implémentés.
- Déploiement “prod durable” avec DB persistante : non couvert si serverless/SQLite éphémère.

## 2) Architecture & choix techniques
### 2.1 Choix
- **Flask** : simplicité pour routes + sessions + templates.
- **SQLite** : base légère, adaptée au prototype (seed via script).
- **Deux modes** : utile pour démontrer attaque/défense sur la même base de code.

### 2.2 Données
La base contient (simplifié) : `users`, `courses`, `enrollments`, `announcements`, `messages`, `agenda_items`, `notes`.
Les comptes de démonstration sont initialisés via `scripts/init_db.py`.

## 3) Stratégie sécurité (mode secure)
### 3.1 Objectif
Réduire les risques majeurs “web classiques” : injection, XSS, CSRF, accès non autorisé, mauvaise gestion de session, exposition de données.

### 3.2 Mesures mises en place
- **SQL paramétré** sur l’authentification.
- **Hash de mots de passe** + vérification via `werkzeug.security`.
- **CSRF** : token obligatoire sur méthodes d’écriture (POST/PUT/PATCH/DELETE).
- **Anti brute‑force** : rate‑limit basique sur `/login` (retour 429).
- **Anti open‑redirect** : `next` restreint à un chemin local (pas de domaine externe).
- **Durcissement session** : `HttpOnly`, `SameSite=Lax` (selon mode).
- **Headers de sécurité** : CSP, X-Frame-Options, nosniff, policies (défense en profondeur).
- **Contrôle d’accès** :
  - IDOR messages corrigé (filtrage par `user_id` en secure).
  - routes admin/api restreintes au rôle `teacher` en secure.

## 4) Vulnérabilités gérées (mapping vers la checklist)
Référence : `docs/vulnerabilites.md`.

### 4.1 Injections & redirections
- **SQLi login (1)** : corrigé par requêtes paramétrées + hash.
- **Open redirect (2)** : corrigé par validation stricte de `next`.

### 4.2 XSS
- **XSS stockée notes (4)** : en secure, sorties échappées.
- **XSS stockée bio (5)** : en secure, sorties échappées.
- **XSS réfléchie search (6)** : en secure, sorties échappées.
- **CSP/headers (7/21)** : ajoutés en secure pour limiter l’impact résiduel.

### 4.3 Auth / session
- **Rate‑limit (10)** : activé en secure.
- **Rotation session (11)** : `session.clear()` au login en secure.
- **Cookies (12)** : durcis en secure.

### 4.4 Contrôles d’accès
- **IDOR messages (13)** : corrigé en secure (`AND user_id = ?`).
- **Admin/API (14/15/18/19)** : restriction rôle `teacher` en secure + réduction des champs API.

## 5) Validation (tests & scénarios)
### 5.1 Tests automatisés
Des tests vérifient le différentiel `vuln` vs `secure` :
- bypass login en `vuln` ;
- open redirect neutralisé en `secure` ;
- XSS stockée (vuln) vs échappement (secure) ;
- présence landing publique (si applicable).

### 5.2 Tests manuels (checklist)
Se référer à `docs/demo.md` + `docs/vulnerabilites.md` pour rejouer :
- SQLi login ;
- XSS (reflected/stored) ;
- IDOR `/messages/<id>` ;
- CSRF sans token.

## 6) Remédiation post‑challenge (process)
Après réception du rapport Red Team :
1) reproduire les PoC en environnement local ;
2) corriger au plus proche de la cause (validation, échappement, contrôle d’accès) ;
3) retester (manuel + automatisé) ;
4) documenter : scénario, fix, risques résiduels.

## 7) Limites & pistes d’amélioration
- **HTTPS** : déployer derrière reverse proxy (Caddy/Nginx) + HSTS en prod.
- **Rate‑limit robuste** : stockage partagé (Redis) + verrouillage par compte.
- **Gestion secrets** : `SECRET_KEY` obligatoire et rotation.
- **Observabilité** : logs structurés + alerting (tentatives d’attaque).
- **CSP renforcée** : nonces/strict-dynamic si ajout de scripts.
