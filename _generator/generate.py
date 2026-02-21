#!/usr/bin/env python3
"""Generate TRMNL comic plugin files from comics.yml config.

Usage:
    python3 _generator/generate.py              # Generate all comics
    python3 _generator/generate.py "Pickles"    # Generate comics matching name
    python3 _generator/generate.py --check      # Verify files match (no overwrite)
"""

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import quote

import yaml
from jinja2 import Environment, FileSystemLoader


# Use custom delimiters so Liquid's {{ }} and {% %} pass through as literals
JINJA_ENV_KWARGS = dict(
    variable_start_string="<<",
    variable_end_string=">>",
    block_start_string="<%",
    block_end_string="%>",
    comment_start_string="<#",
    comment_end_string="#>",
    keep_trailing_newline=True,
)

LAYOUT_FILES = [
    "full.liquid",
    "half_horizontal.liquid",
    "half_vertical.liquid",
    "quadrant.liquid",
]

PATTERN_TEMPLATES = {
    "title": "shared_title.liquid.j2",
    "caption": "shared_caption.liquid.j2",
    "panels": "shared_panels.liquid.j2",
}


def load_config(generator_dir: Path) -> list[dict]:
    config_path = generator_dir / "comics.yml"
    with open(config_path) as f:
        data = yaml.safe_load(f)
    return data["comics"]


def create_jinja_env(generator_dir: Path) -> Environment:
    template_dir = generator_dir / "templates"
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        **JINJA_ENV_KWARGS,
    )


def url_encode_path(value: str) -> str:
    """URL-encode a path component, replacing spaces with %20."""
    return quote(value, safe="")


def generate_comic(comic: dict, env: Environment, repo_root: Path) -> dict[str, str]:
    """Generate all files for a comic. Returns dict of relative_path -> content."""
    files = {}
    plugin_dir = comic["dir"]
    src_dir = f"{plugin_dir}/src"

    # settings.yml
    settings_template = env.get_template("settings.yml.j2")
    files[f"{src_dir}/settings.yml"] = settings_template.render(comic=comic, urlencode=url_encode_path)

    # Layout files (all identical)
    layout_template = env.get_template("layout.liquid.j2")
    layout_content = layout_template.render(comic=comic)
    for layout_file in LAYOUT_FILES:
        files[f"{src_dir}/{layout_file}"] = layout_content

    # shared.liquid (pattern-specific)
    pattern = comic["pattern"]
    if pattern not in PATTERN_TEMPLATES:
        print(f"Error: Unknown pattern '{pattern}' for comic '{comic['name']}'", file=sys.stderr)
        sys.exit(1)
    shared_template = env.get_template(PATTERN_TEMPLATES[pattern])
    files[f"{src_dir}/shared.liquid"] = shared_template.render(comic=comic)

    # .trmnlp.yml (in plugin root, not src/)
    trmnlp_template = env.get_template("trmnlp.yml.j2")
    files[f"{plugin_dir}/.trmnlp.yml"] = trmnlp_template.render(comic=comic)

    return files


def write_files(files: dict[str, str], repo_root: Path) -> int:
    """Write generated files to disk. Returns count of files written."""
    count = 0
    for rel_path, content in files.items():
        file_path = repo_root / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        count += 1
    return count


def check_files(files: dict[str, str], repo_root: Path) -> list[str]:
    """Check if generated files match existing files. Returns list of mismatched paths."""
    mismatches = []
    for rel_path, expected_content in files.items():
        file_path = repo_root / rel_path
        if not file_path.exists():
            mismatches.append(f"{rel_path} (missing)")
            continue
        actual_content = file_path.read_text()
        if actual_content != expected_content:
            mismatches.append(rel_path)
    return mismatches


def main():
    parser = argparse.ArgumentParser(description="Generate TRMNL comic plugin files")
    parser.add_argument("filter", nargs="?", help="Only generate comics matching this name (substring match)")
    parser.add_argument("--check", action="store_true", help="Verify files match without overwriting")
    args = parser.parse_args()

    # Determine paths relative to this script
    generator_dir = Path(__file__).resolve().parent
    repo_root = generator_dir.parent

    # Load config and create Jinja environment
    comics = load_config(generator_dir)
    env = create_jinja_env(generator_dir)

    # Add custom filter for URL encoding
    env.filters["urlencode"] = url_encode_path

    # Filter comics if requested
    if args.filter:
        comics = [c for c in comics if args.filter.lower() in c["name"].lower()]
        if not comics:
            print(f"No comics matching '{args.filter}'", file=sys.stderr)
            sys.exit(1)

    # Generate all files
    all_files = {}
    for comic in comics:
        all_files.update(generate_comic(comic, env, repo_root))

    if args.check:
        mismatches = check_files(all_files, repo_root)
        if mismatches:
            print("Files out of sync with generator:")
            for path in mismatches:
                print(f"  {path}")
            sys.exit(1)
        else:
            print(f"All {len(all_files)} files are in sync.")
    else:
        count = write_files(all_files, repo_root)
        print(f"Generated {count} files for {len(comics)} comic(s).")


if __name__ == "__main__":
    main()
