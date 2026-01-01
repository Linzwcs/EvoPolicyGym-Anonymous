# /// script
# requires-python = ">=3.12"
# dependencies = ["Markdown==3.8.2"]
# ///
"""Build a static review website using local assets and relative links."""

from __future__ import annotations

import html
import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit

import markdown

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "site" / "pages"


def relative(target: Path, page: Path) -> str:
    return Path(os.path.relpath(target, page.parent)).as_posix()


def frame(title: str, content: str, page: Path, *, document: bool = True) -> str:
    home = relative(ROOT / "index.html", page)
    docs = relative(OUTPUT / "docs" / "index.html", page)
    review = relative(OUTPUT / "REVIEW.html", page)
    css = relative(ROOT / "site" / "style.css", page)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer">
<meta name="author" content="Anonymous Authors"><meta name="description" content="Anonymous review artifact for executable policy evolution in interactive environments.">
<title>{html.escape(title)} · EvoPolicyGym</title><link rel="stylesheet" href="{css}"></head>
<body><header><nav aria-label="Main navigation"><a class="brand" href="{home}">EvoPolicyGym</a><div class="navlinks"><a href="{docs}">Documentation</a><a href="{home}#environments">Environments</a><a href="{review}">Review guide</a></div></nav></header>
<main class="{'doc' if document else 'landing'}">{content}</main>
<footer><span>EvoPolicyGym · v0.3.0 · Anonymous Authors</span><span>Static review materials · No analytics</span></footer></body></html>'''


def main() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    sources = [ROOT / p for p in ("README.md", "REVIEW.md", "ARCHITECTURE.md", "CONTRIBUTING.md", "SECURITY.md")]
    sources.extend((ROOT / "docs").glob("*.md"))
    sources.extend(p for p in (ROOT / "environments").rglob("*.md") if not {"vendor", ".venv"}.intersection(p.parts))
    sources.extend((ROOT / "skills").rglob("*.md"))
    pages = {p.resolve(): OUTPUT / p.relative_to(ROOT).with_suffix(".html") for p in sources}

    for source, target in pages.items():
        text = source.read_text()
        text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
        rendered = markdown.markdown(text, extensions=["fenced_code", "tables", "toc"])

        def link(match: re.Match[str], source: Path = source, target: Path = target) -> str:
            attribute, value = match.groups()
            parsed = urlsplit(html.unescape(value))
            if parsed.scheme or parsed.netloc or value.startswith("#"):
                return match.group(0)
            path = (source.parent / unquote(parsed.path)).resolve()
            if path.is_dir() and (path / "README.md").exists():
                path = path / "README.md"
            destination = pages.get(path, path)
            href = relative(destination, target)
            if parsed.fragment:
                href += "#" + parsed.fragment
            return f'{attribute}="{html.escape(href, quote=True)}"'

        rendered = re.sub(r'(href|src)="([^"]+)"', link, rendered)
        title = re.search(r"^# (.+)$", text, re.M)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(frame(title.group(1) if title else source.stem.replace("-", " ").title(), rendered, target))

    projects = [p for p in (ROOT / "environments").rglob("pyproject.toml") if not {"vendor", ".venv"}.intersection(p.parts)]
    collections = sorted({p.relative_to(ROOT / "environments").parts[0] for p in projects})
    names = {"ale": "Arcade Learning Environment", "arcprize": "ARC-AGI-3", "atcoder": "AtCoder AHC", "codechef": "CodeChef Challenges", "crafter": "Crafter", "dm_control": "DeepMind Control Suite", "gymnasium": "Gymnasium", "gymnasium_robotics": "Gymnasium Robotics", "highway_env": "HighwayEnv", "jackdaw": "Balatro / Jackdaw", "jumanji": "Jumanji", "metaworld": "MetaWorld", "minigrid": "MiniGrid & BabyAI", "nle": "NetHack Learning Environment", "robosuite": "robosuite", "stable_retro": "Stable-Retro", "vizdoom": "ViZDoom"}
    items = []
    for key in collections:
        readme = ROOT / "environments" / key / "README.md"
        if not readme.exists():
            readme = min((ROOT / "environments" / key).rglob("README.md"), key=lambda p: (len(p.parts), str(p)))
        href = pages[readme.resolve()].relative_to(ROOT).as_posix()
        items.append(f'<li><a href="{href}">{html.escape(names.get(key, key))}</a></li>')
    catalog = "\n".join(items)
    content = (ROOT / "site" / "home.html").read_text().replace("@@COUNT@@", str(len(projects))).replace("@@CATALOG@@", catalog)
    (ROOT / "index.html").write_text(frame("Policy evolution", content, ROOT / "index.html", document=False))
    print(f"Built homepage and {len(pages)} documentation pages; {len(projects)} Benchmark distributions.")


if __name__ == "__main__":
    main()
