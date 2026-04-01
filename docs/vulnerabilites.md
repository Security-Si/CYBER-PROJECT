# Vulnérabilités — Checklist structurée (20)

Ce document liste **20 failles** (niveau simple → moyen) groupées par catégories, avec :
- **Où** (endpoint / zone)
- **Impact**
- **Démo rapide (PoC)** pour reproduire
- **Attendu en `secure`**

> Périmètre : uniquement cette application de démo.

---

## A) Injections & redirections

### 1) SQL Injection — bypass login
- **Où** : `POST /login` (mode `vuln`)
- **Impact** : authentification sans mot de passe
- **PoC** : username `x' OR 1=1 -- ` / password `x`
- **Attendu en `secure`** : échec (requête paramétrée + hash)

### 2) Open Redirect — paramètre `next`
- **Où** : `GET/POST /login?next=...` (mode `vuln`)
- **Impact** : redirection vers un domaine externe (phishing)
- **PoC** : `/login?next=https://example.com` puis login
- **Attendu en `secure`** : redirection forcée vers un chemin interne

### 3) Validation insuffisante (injection “logique”)
- **Où** : `POST /profile`, `POST /agenda` (mode `vuln`)
- **Impact** : données inattendues, comportements non prévus
- **PoC** : champs vides / très longs / caractères spéciaux
- **Attendu en `secure`** : requêtes rejetées (400)

---

## B) XSS (Cross‑Site Scripting)

### 4) XSS stockée — notes agenda
- **Où** : `POST /agenda` → affichage `GET /agenda` (mode `vuln`)
- **Impact** : exécution de JS à chaque visite de la page
- **PoC** :
  ```html
  <img src=x onerror=alert(1)>
  ```
- **Attendu en `secure`** : affichage échappé (`&lt;img...`)

### 5) XSS stockée — bio profil
- **Où** : `POST /profile` → affichage `GET /profile` (mode `vuln`)
- **Impact** : exécution JS sur la page profil
- **PoC** :
  ```html
  <svg onload=alert(1)>
  ```
- **Attendu en `secure`** : affichage échappé

### 6) XSS réfléchie — recherche
- **Où** : `GET /search?q=...` (mode `vuln`)
- **Impact** : exécution JS à l’ouverture du lien
- **PoC** : `/search?q=<img src=x onerror=alert(1)>`
- **Attendu en `secure`** : contenu échappé

### 7) Défense navigateur absente (CSP) en `vuln`
- **Où** : réponses HTTP (mode `vuln`)
- **Impact** : XSS plus simple à exploiter (pas de CSP)
- **PoC** : vérifier headers dans DevTools → Network
- **Attendu en `secure`** : header `Content-Security-Policy` présent

---

## C) Authentification & sessions

### 8) Mots de passe en clair (DB)
- **Où** : table `users.password_plain`
- **Impact** : compromission totale si fuite DB
- **PoC** : consulter `/admin/users` (mode `vuln`)
- **Attendu en `secure`** : secrets masqués dans l’UI + API limitée

### 9) “Le secret est dans le HTML” (DevTools / Inspect)
- **Où** : `GET /login` (mode `vuln`)
- **Impact** : identifiants de test exposés via le code source HTML
- **PoC** : Inspecter → onglet Elements → chercher “Comptes de test”
- **Attendu en `secure`** : le bloc n’apparaît pas

### 10) Bruteforce / rate‑limit absent en `vuln`
- **Où** : `POST /login`
- **Impact** : essais illimités
- **PoC** : enchaîner rapidement des logins invalides
- **Attendu en `secure`** : `429 Too Many Requests` après N essais

### 11) Fixation/rotation de session insuffisante
- **Où** : workflow login (mode `vuln`)
- **Impact** : risque de session fixation
- **PoC** : comparer le comportement session avant/après login
- **Attendu en `secure`** : `session.clear()` au login

### 12) Cookies non durcis en `vuln`
- **Où** : cookie de session
- **Impact** : exposition via XSS/JS, attaques cross‑site
- **PoC** : vérifier attributs du cookie (Application/Storage)
- **Attendu en `secure`** : `HttpOnly` + `SameSite=Lax`

---

## D) Broken Access Control (IDOR / BOLA)

### 13) IDOR — lecture de messages par ID
- **Où** : `GET /messages/<id>` (mode `vuln`)
- **Impact** : lecture de données d’un autre compte (si IDs devinables)
- **PoC** : changer l’ID dans l’URL (1, 2, 3…)
- **Attendu en `secure`** : message non accessible (404/403)

### 14) Contrôle d’accès admin trop permissif
- **Où** : `GET /admin/users` (mode `vuln`)
- **Impact** : accès à des données internes
- **PoC** : login `student` puis ouvrir `/admin/users`
- **Attendu en `secure`** : réservé au rôle `teacher` (403)

### 15) Endpoint API sensible
- **Où** : `GET /api/users`
- **Impact** : fuite de données en JSON
- **PoC** : ouvrir `/api/users` connecté
- **Attendu en `secure`** : accès `teacher` + champs limités

### 16) Contrôle d’accès cours (inscription)
- **Où** : `GET /courses/<id>`
- **Impact** : accès à un cours non autorisé (selon données)
- **PoC** : tester différents IDs de cours
- **Attendu en `secure`** : 403 si non inscrit

---

## E) CSRF

### 17) CSRF sur actions POST (mode `vuln`)
- **Où** : `POST /agenda`, `POST /profile`, `POST /logout`
- **Impact** : actions déclenchables à l’insu de l’utilisateur
- **PoC** : soumettre un POST sans token (via curl / form externe)
- **Attendu en `secure`** : 400 si token CSRF absent/invalide

---

## F) Exposition de données & erreurs

### 18) Exposition de secrets via UI (admin)
- **Où** : `/admin/users` (mode `vuln`)
- **Impact** : fuite de credentials de test (password_plain)
- **PoC** : ouvrir la page admin en `vuln`
- **Attendu en `secure`** : secrets cachés

### 19) Exposition de secrets via API (JSON)
- **Où** : `/api/users` (mode `vuln`)
- **Impact** : fuite en clair via JSON
- **PoC** : ouvrir l’endpoint en `vuln`
- **Attendu en `secure`** : champs sensibles absents

### 20) Manque de durcissement HTTP en `vuln`
- **Où** : headers HTTP (mode `vuln`)
- **Impact** : surface d’attaque augmentée (clickjacking/XSS/…)
- **PoC** : inspecter headers dans DevTools
- **Attendu en `secure`** : `X-Frame-Options`, `nosniff`, `CSP`, etc.

---

## Annexes (références dans le projet)
- Démo rapide : `docs/demo.md`
