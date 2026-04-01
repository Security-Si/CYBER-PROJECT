# Projet SSI — Cyber Challenge (Façade Moodle / SaaS)

Ce dépôt contient une mini “façade Moodle” avec **deux modes** :
- `vuln` : volontairement vulnérable (XSS, auth faible, SQLi, open redirect).
- `secure` : corrections et contre-mesures (validation/échappement, requêtes paramétrées, hash MDp, CSRF, rate‑limit basique).

## Prérequis
- Python 3.9+

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Initialiser la base
```bash
python scripts/init_db.py
```

Identifiants de démo :
- `student` / `password123`
- `teacher` / `Password!2026`

## Lancer l’app
Mode vulnérable :
```bash
APP_MODE=vuln python run.py
```

Mode sécurisé :
```bash
APP_MODE=secure python run.py
```

Puis ouvrir `http://127.0.0.1:5000`.

## Déploiement (Vercel)
Ce projet peut tourner sur Vercel via une fonction Python (`api/index.py`) + `vercel.json`.

Limites importantes :
- SQLite sur Vercel est **éphémère** (stockée dans `/tmp`) : les données peuvent disparaître entre 2 exécutions.
- Pour une “vraie prod”, préférer une DB externe (Postgres) + une plateforme type Render/Fly/Railway.

Déployer :
```bash
npm i -g vercel
vercel
vercel --prod
```

Variables d’environnement Vercel recommandées :
- `APP_MODE=secure`
- `SECRET_KEY=...` (obligatoire en prod)

## Pages
- `/` : landing page (marketing)
- `/pricing` : plans
- `/features` : fonctionnalités
- `/dashboard` : dashboard (KPIs + accès rapide)
- `/courses` : cours + annonces
- `/agenda` : calendar + notes (XSS stockée en `vuln`)
- `/messages` : inbox (IDOR en `vuln` sur `/messages/<id>`)
- `/org` : organization (démo)
- `/billing` : billing (démo)
- `/settings` : settings (démo)

## Scraping (optionnel, éthique)
Un script est fourni pour **scraper** un Moodle public (respect `robots.txt`, délai entre requêtes).
```bash
python scripts/scrape_moodle.py --base-url https://moodle.example.edu
```
Les fichiers sont sauvegardés dans `scraped/`.

## Docs (rapports)
- `docs/blue-team-report.md`
- `docs/red-team-report.md`
- `docs/demo.md`
- `docs/vulnerabilites.md`
# CYBER-Project
