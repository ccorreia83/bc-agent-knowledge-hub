#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path.cwd()
SITE_BASE = "/bc-agent-knowledge-hub"
SKIP_DIRS = {".git", ".github", "_site", "vendor", "node_modules"}
INDEXED_DIRS = ["routing", "domains", "policies", "sources"]

def title_from(path: Path) -> str:
    stem = path.stem
    if stem.upper() == "AGENTS":
        return "Agent routing entry point"
    return stem.replace("-", " ").replace("_", " ").strip().title()

def has_front_matter(text: str) -> bool:
    return text.startswith("---\n") or text.startswith("---\r\n")

def add_front_matter(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if has_front_matter(text):
        return False
    rel = path.relative_to(ROOT).as_posix()
    description = f"Business Central agent knowledge hub page: {rel}"
    front = (
        "---\n"
        "layout: default\n"
        f"title: \"{title_from(path)}\"\n"
        f"description: \"{description}\"\n"
        "---\n\n"
    )
    path.write_text(front + text, encoding="utf-8")
    return True

def markdown_files(folder: Path):
    return sorted(
        [p for p in folder.rglob("*.md") if not any(part in SKIP_DIRS for part in p.parts)],
        key=lambda p: p.as_posix().lower(),
    )

def page_url(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("").as_posix()
    if rel.lower().endswith("/index"):
        rel = rel[:-6].rstrip("/")
    return f"{SITE_BASE}/{rel}/" if rel and path.stem.lower() == "index" else f"{SITE_BASE}/{rel}.html"

def link_to(path: Path, from_dir: Path) -> str:
    target = path.relative_to(from_dir).as_posix()
    return f"[{title_from(path)}]({target})"

def write_folder_index(folder: Path) -> None:
    index = folder / "index.md"
    files = [p for p in markdown_files(folder) if p != index]
    lines = [
        "---",
        "layout: default",
        f'title: "{folder.name.replace("-", " ").title()} catalog"',
        f'description: "Navigable catalog for {folder.name} content in the Business Central Agent Knowledge Hub."',
        "---",
        "",
        f"# {folder.name.replace('-', ' ').title()}",
        "",
        "This page exposes every document in this section through normal HTML links so that users and knowledge crawlers can discover the complete routing catalog.",
        "",
    ]
    if files:
        for p in files:
            rel = p.relative_to(folder).as_posix()
            lines.append(f"- [{title_from(p)}]({rel})")
    else:
        lines.append("No documents are currently published in this section.")
    lines.extend(["", "[Back to the Knowledge Hub](../index.md)", ""])
    index.write_text("\n".join(lines), encoding="utf-8")

def strip_front_matter(text: str) -> str:
    if not has_front_matter(text):
        return text
    parts = text.split("---", 2)
    return parts[2].lstrip() if len(parts) == 3 else text

def write_consolidated_knowledge() -> None:
    candidates = []
    agents = ROOT / "AGENTS.md"
    if agents.exists():
        candidates.append(agents)
    for name in INDEXED_DIRS:
        folder = ROOT / name
        if folder.is_dir():
            candidates.extend(p for p in markdown_files(folder) if p.name.lower() != "index.md")

    lines = [
        "---",
        "layout: default",
        'title: "Complete Business Central Agent Knowledge"',
        'description: "Single crawlable page containing agent routing, domains, evidence policies and source catalogs."',
        'permalink: /knowledge-all/',
        "---",
        "",
        "# Complete Business Central Agent Knowledge",
        "",
        "This single page consolidates the complete routing catalog for knowledge systems that retrieve only the configured public URL or do not follow nested links.",
        "",
    ]
    for path in candidates:
        rel = path.relative_to(ROOT).as_posix()
        content = strip_front_matter(path.read_text(encoding="utf-8")).strip()
        lines.extend([
            "---",
            "",
            f"## Source document: `{rel}`",
            "",
            content,
            "",
        ])
    (ROOT / "knowledge-all.md").write_text("\n".join(lines), encoding="utf-8")

def write_root_index() -> None:
    agents = ROOT / "AGENTS.md"
    lines = [
        "---",
        "layout: default",
        'title: "Business Central Agent Knowledge Hub"',
        'description: "Source routing and evidence framework for Microsoft Dynamics 365 Business Central agents."',
        "---",
        "",
        "# Business Central Agent Knowledge Hub",
        "",
        "Vendor-neutral routing catalog for agents that investigate Microsoft Dynamics 365 Business Central.",
        "",
        "This repository does not mirror product documentation. It tells agents which source to use, how to qualify evidence, and when live-environment validation is required.",
        "",
        "## Start here",
        "",
    ]
    if agents.exists():
        lines.append("1. [Open the agent routing entry point](AGENTS.md).")
    lines.extend([
        "2. Load the matching role under [Routing](routing/).",
        "3. Open the relevant [Domain catalog](domains/).",
        "4. Apply the required [Evidence policies](policies/).",
        "5. Select the necessary [Source catalog](sources/).",
        "",
        "## Complete consolidated knowledge",
        "",
        "- [Open the complete routing, domain, policy and source catalog on one page](knowledge-all.md).",
        "",
        "## Complete crawlable catalog",
        "",
    ])
    for name in INDEXED_DIRS:
        if (ROOT / name).is_dir():
            lines.append(f"- [{name.replace('-', ' ').title()}]({name}/)")
    lines.extend([
        "",
        "## Retrieval scope",
        "",
        "- Use this Hub to choose and qualify sources.",
        "- Use the selected operational tool or final source to supply evidence.",
        "- Keep internal, public, and combined research scopes explicitly separated.",
        "- Do not treat a zero-result query as proof that content does not exist.",
        "",
    ])
    (ROOT / "index.md").write_text("\n".join(lines), encoding="utf-8")

def write_config() -> None:
    config = ROOT / "_config.yml"
    existing = config.read_text(encoding="utf-8") if config.exists() else ""
    required = {
        "title": "Business Central Agent Knowledge Hub",
        "description": "Source routing and evidence framework for Microsoft Dynamics 365 Business Central agents.",
        "theme": "jekyll-theme-primer",
        "url": "https://mypartnerts.github.io",
        "baseurl": SITE_BASE,
        "markdown": "kramdown",
    }
    additions = []
    for key, value in required.items():
        if not re.search(rf"(?m)^\s*{re.escape(key)}\s*:", existing):
            rendered = f'"{value}"' if isinstance(value, str) else value
            additions.append(f"{key}: {rendered}")
    if additions:
        sep = "" if not existing or existing.endswith("\n") else "\n"
        config.write_text(existing + sep + "\n".join(additions) + "\n", encoding="utf-8")

def write_robots_and_sitemap() -> None:
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /bc-agent-knowledge-hub/\n"
        "Sitemap: https://mypartnerts.github.io/bc-agent-knowledge-hub/sitemap.xml\n",
        encoding="utf-8",
    )
    pages = [p for p in markdown_files(ROOT) if p.name.lower() != "readme.md"]
    urls = sorted({"https://mypartnerts.github.io" + page_url(p) for p in pages})
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    xml.extend(f"  <url><loc>{u}</loc></url>" for u in urls)
    xml.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")

def main():
    if not (ROOT / "AGENTS.md").exists():
        raise SystemExit("Run this script from the repository root; AGENTS.md was not found.")

    for name in INDEXED_DIRS:
        folder = ROOT / name
        if folder.is_dir():
            write_folder_index(folder)

    write_consolidated_knowledge()
    write_root_index()

    changed = 0
    for path in markdown_files(ROOT):
        if add_front_matter(path):
            changed += 1

    write_config()
    write_robots_and_sitemap()

    print(f"Patch applied. Added front matter to {changed} Markdown files.")
    print("Generated: index.md, knowledge-all.md, section indexes, robots.txt and sitemap.xml")
    print("Next: review 'git diff', commit, push, wait for Pages deployment, then re-add or refresh the Copilot Studio knowledge source.")

if __name__ == "__main__":
    main()
