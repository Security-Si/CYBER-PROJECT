# Rapport Blue Team — Conception, sécurisation et remédiation (1ère personne)

Auteur (Blue Team) : **Tristan Hardouin**  
Projet : **Cyber Challenge — Façade Moodle / SaaS** (SSI 2025–2026)  
Âge / profil : **22 ans**, niveau débutant en sécurité web (mais motivé)  
Équipe : Keis Aissaoui • Tristan Hardouin  
À compléter : filière / école / année universitaire.

## 0) Ce que j’ai fait (résumé)
Dans ce projet, mon objectif côté Blue Team c’était de :
- construire une application qui ressemble à une petite plateforme (login + “workspace”) ;
- laisser un mode **vulnérable** pour que la Red Team puisse attaquer ;
- puis proposer un mode **secure** où je corrige les failles et je montre que les attaques “simples” ne passent plus.

Pour ne pas me perdre, je me suis appuyé sur la checklist `docs/vulnerabilites.md` (c’est notre liste de failles).

## 1) Périmètre (ce que je couvre)
### 1.1 Application
- Backend : Flask (Python) + SQLite.
- Front : HTML (Jinja2) + assets statiques.
- Pages / endpoints : `/login`, `/dashboard`, `/courses`, `/agenda`, `/messages`, `/profile`, `/search`, `/api/users`, `/admin/users`.
- Deux modes :
  - `APP_MODE=vuln`
  - `APP_MODE=secure`

### 1.2 Ce que je ne couvre pas
Je reste sur un projet pédagogique, donc :
- pas d’intégration Stripe réelle (billing = démo) ;
- pas de MFA/SSO ;
- pas de monitoring avancé (SIEM etc.) ;
- pas de base “prod” persistante si on déploie en serverless avec SQLite.

## 2) Choix techniques (expliqués simplement)
J’ai gardé des choix simples, parce que le but c’est la compréhension :
- Flask : je trouve ça clair pour lire les routes et comprendre les failles.
- SQLite : facile à lancer et à seed, pratique en projet.
- Un script d’init DB : `scripts/init_db.py` pour avoir toujours les mêmes données.
- Deux modes : je peux comparer “avant/après” sans changer de projet.

## 3) Stratégie de défense (mode secure)
Quand je passe en `secure`, je pars du principe : “je corrige le plus important d’abord”.

### 3.1 Objectifs (ce que je veux empêcher)
- injection SQL sur le login ;
- XSS (stockée + réfléchie) ;
- CSRF sur les formulaires ;
- lecture de données d’autres utilisateurs (IDOR) ;
- redirections externes (open redirect) ;
- fuite d’infos sur l’API / l’admin ;
- brute-force sur le login.

### 3.2 Contre‑mesures que j’active en `secure`
Je liste ici ce que j’ai mis (ou ce que le mode secure fait) :
- **Requêtes paramétrées** au login (plus de concat SQL).
- **Hash de mot de passe** + vérification (au lieu du mot de passe en clair).
- **CSRF token** obligatoire sur les requêtes d’écriture.
- **Rate‑limit** basique sur `/login` (429 après trop d’essais).
- **Anti open‑redirect** : `next` doit être un chemin interne.
- **Durcissement cookies de session** : `HttpOnly` + `SameSite`.
- **Headers sécurité** : CSP, X-Frame-Options, nosniff, etc.
- **Contrôle d’accès** : IDOR corrigée sur les messages, admin/API restreints au rôle `teacher`.

## 4) Comment je relie les failles à ma checklist
Pour que ce soit clair, je mappe directement la checklist `docs/vulnerabilites.md` :

### A) Injections & redirections
- (1) SQLi login : corrigée en `secure` (requête paramétrée).
- (2) Open redirect : corrigée en `secure` (validation de `next`).

### B) XSS
- (4) XSS stockée notes : en `secure` le contenu est échappé.
- (5) XSS stockée bio : en `secure` le contenu est échappé.
- (6) XSS réfléchie search : en `secure` le contenu est échappé.
- (7)/(20) headers/CSP : présents en `secure` (défense en profondeur).

### C) Auth & sessions
- (10) brute-force : rate‑limit en `secure`.
- (11) session : je nettoie la session au login en `secure`.
- (12) cookies : plus stricts en `secure`.

### D) Access control
- (13) IDOR messages : en `secure` je filtre par `user_id`.
- (14)/(15)/(18)/(19) admin + API : en `secure` je limite l’accès et je réduis les infos renvoyées.

## 5) Comment j’ai validé (en tant que débutant)
Je n’ai pas fait un pentest “pro”, mais j’ai fait du concret :

### 5.1 Tests automatisés
J’ai utilisé les tests `pytest` pour vérifier que :
- une attaque passe en `vuln`,
- et qu’elle ne passe plus en `secure`.

### 5.2 Tests manuels
Je rejoue les scénarios décrits dans :
- `docs/demo.md`
- `docs/vulnerabilites.md`

Exemples :
- SQLi sur `/login` ;
- XSS sur `/search`, `/agenda`, `/profile` ;
- IDOR sur `/messages/<id>` ;
- CSRF en envoyant un POST sans token en `vuln`.

## 6) Ce que je ferais pour aller “plus prod”
Si je devais rendre ça vraiment déployable :
- mettre une DB externe (Postgres) au lieu de SQLite serverless ;
- ajouter un vrai rate-limit partagé (Redis) ;
- sécuriser la gestion des secrets (`SECRET_KEY` obligatoire, rotation) ;
- logs d’audit minimal sur login/admin ;
- CSP plus stricte si on ajoute des scripts externes.
