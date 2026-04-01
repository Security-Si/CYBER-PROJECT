# Démo (attaque & défense)

Ces PoC sont destinés **uniquement** à cette application de démo en local.

## Lancer
```bash
APP_MODE=vuln python run.py
```

## 1) SQLi (bypass login) — mode `vuln`
- Username : `x' OR 1=1 -- `
- Password : `x`

## 2) Stored XSS — mode `vuln`
Après login, ajouter une note avec :
```html
<img src=x onerror="alert('XSS')">
```

## 3) XSS réfléchie — mode `vuln`
Ouvrir :
`/search?q=<img src=x onerror=alert(1)>`

## 4) IDOR — mode `vuln`
Ouvrir un message par ID :
`/messages/1`, `/messages/2`, etc.  
(En mode `vuln`, pas de vérification du propriétaire.)

## 5) Open redirect — mode `vuln`
Ouvrir :
`/login?next=https://example.com`

## Vérifier les corrections — mode `secure`
```bash
APP_MODE=secure python run.py
```
Attendu :
- SQLi échoue (pas de login).
- XSS est affiché échappé (`&lt;img ...`).
- Redirection externe ignorée (retour `/agenda`).
- IDOR bloqué (404/403 selon le cas).
