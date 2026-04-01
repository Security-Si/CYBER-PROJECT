# Rapport Red Team — Pentest simplifié (SSI 2025-2026)

Équipe : Keis Aissaoui • Tristan Hardouin  
À compléter : filière / école.

## 1) Reconnaissance
- Pages : `/login`, `/agenda`.
- Fonctionnalités : authentification, notes, agenda statique.

## 2) Vulnérabilités & exploitation (cibles en mode `vuln`)

### 2.1 Bypass authentification (SQLi)
**Point d’entrée** : POST `/login`  
**Hypothèse** : concaténation SQL côté serveur  
**PoC** :
- Username : `x' OR '1'='1`
- Password : `x`
**Résultat attendu** : authentification réussie sans connaître le mot de passe.

### 2.2 Stored XSS (notes)
**Point d’entrée** : POST `/agenda` (form “Notes personnelles”)  
**PoC** :
```html
<img src=x onerror="alert('XSS')">
```
**Impact** : exécution JS à chaque affichage de l’agenda.

### 2.3 Open redirect
**Point d’entrée** : GET `/login?next=https://attacker.example`  
**Impact** : redirection après login vers un domaine externe (phishing).

## 3) Recommandations
- SQL paramétré partout (pas seulement login).
- Échappement strict + pas de `safe` sur contenu utilisateur.
- Anti open-redirect : whitelist de paths.
- CSRF systématique sur formulaires.
- Rate-limit et/ou verrouillage temporaire après X échecs.

## 4) Preuves
- Captures d’écran, logs, requêtes HTTP, etc.
