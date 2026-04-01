from __future__ import annotations

import argparse
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def is_allowed_by_robots(base_url: str, path: str) -> bool:
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        r = requests.get(robots_url, timeout=10)
    except requests.RequestException:
        return False

    if r.status_code >= 400:
        return False

    # Parse ultra-basique: on respecte "Disallow:" sans gestion fine des user-agents.
    disallows = []
    for line in r.text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith("disallow:"):
            rule = line.split(":", 1)[1].strip()
            disallows.append(rule)

    for rule in disallows:
        if rule == "/":
            return False
        if rule and path.startswith(rule):
            return False
    return True


def fetch(base_url: str, path: str, out_dir: Path, delay_s: float) -> None:
    if not is_allowed_by_robots(base_url, path):
        raise SystemExit(f"robots.txt interdit la récupération de {path} sur {base_url}")

    url = urljoin(base_url, path)
    print(f"GET {url}")
    r = requests.get(url, timeout=15, headers={"User-Agent": "SSI-CyberChallenge-Scraper/1.0"})
    r.raise_for_status()
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = re.sub(r"[^a-zA-Z0-9_.-]+", "_", path.strip("/")) or "index"
    (out_dir / f"{filename}.html").write_text(r.text, encoding="utf-8")
    time.sleep(delay_s)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scraping basique (éthique) de pages Moodle publiques.")
    parser.add_argument("--base-url", required=True, help="Ex: https://moodle.example.edu")
    parser.add_argument("--out", default="scraped", help="Dossier de sortie")
    parser.add_argument("--delay", type=float, default=1.5, help="Délai (s) entre requêtes")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SystemExit("base-url invalide (attendu http(s)://...)")

    out_dir = Path(args.out)
    fetch(base_url, "/login/index.php", out_dir, args.delay)
    fetch(base_url, "/calendar/view.php", out_dir, args.delay)

    # Bonus: extraire les <link rel=stylesheet> depuis la page login et télécharger les CSS (si autorisé).
    login_html = (out_dir / "login_index.php.html").read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(login_html, "html.parser")
    css_links = []
    for link in soup.find_all("link"):
        if (link.get("rel") or [""])[0].lower() == "stylesheet" and link.get("href"):
            css_links.append(link["href"])

    css_dir = out_dir / "css"
    css_dir.mkdir(parents=True, exist_ok=True)
    for href in css_links[:6]:
        css_url = urljoin(base_url, href)
        path = urlparse(css_url).path or "/"
        if not is_allowed_by_robots(base_url, path):
            print(f"SKIP robots: {css_url}")
            continue
        try:
            print(f"GET {css_url}")
            r = requests.get(css_url, timeout=15, headers={"User-Agent": "SSI-CyberChallenge-Scraper/1.0"})
            if r.status_code >= 400:
                continue
            name = re.sub(r"[^a-zA-Z0-9_.-]+", "_", Path(path).name or "style.css")
            (css_dir / name).write_text(r.text, encoding="utf-8")
            time.sleep(args.delay)
        except requests.RequestException:
            continue

    print(f"OK: {out_dir}/")


if __name__ == "__main__":
    main()

