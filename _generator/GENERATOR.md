# Comic Plugin Generator

The `_generator/` directory contains a Python-based code generator for comiccaster.xyz RSS comic plugins. These comic plugins share identical CSS, layout, and similar JavaScript, so they are generated from shared Jinja2 templates and a single YAML config file. This eliminates duplication and ensures consistency across all generated plugins.

## Generated Plugins

- **Pickles Comic** (`pattern: title`)
- **FoxTrot Classics Comic** (`pattern: title`)
- **Daily New Yorker Cartoon** (`pattern: caption`)

## Setup

Create a Python virtual environment and install dependencies:

```bash
python3 -m venv _generator/.venv
_generator/.venv/bin/pip install -r _generator/requirements.txt
```

## Usage

```bash
# Generate all comics
_generator/.venv/bin/python3 _generator/generate.py

# Generate a single comic (substring match on name)
_generator/.venv/bin/python3 _generator/generate.py "Pickles"

# Verify generated files match existing files (no overwrite)
_generator/.venv/bin/python3 _generator/generate.py --check
```

## Adding a New Comic

1. Add an entry to `_generator/comics.yml`:

   ```yaml
   - name: "My New Comic"
     dir: "My New Comic"
     id: 0
     polling_url: "https://comiccaster.xyz/rss/my-new-comic"
     refresh_interval: 360
     no_screen_padding: false
     description: "Displays the daily My New Comic by Author Name"
     pattern: title
   ```

2. Run the generator: `_generator/.venv/bin/python3 _generator/generate.py "My New Comic"`
3. Use `trmnlp.sh` to initialize and push: `./trmnlp.sh "My New Comic" push`
4. After pushing, the TRMNL API assigns an `id`. Run `./trmnlp.sh "My New Comic" pull` to retrieve it, then update the `id` field in `comics.yml` and re-run the generator.

## Patterns

The `pattern` field in `comics.yml` selects which `shared.liquid` template is used:

- **`title`** — Displays the comic image with a title bar at the bottom showing `rss.channel.item[0].title`. Used by Pickles and FoxTrot.
- **`caption`** — Displays the comic image with a caption extracted from the `<em>` tag in the RSS description. Used by Daily New Yorker Cartoon.
- **`panels`** — For multi-panel comics where the RSS description contains multiple `<img>` tags. Displays a single panel selected by `panel_index`. Supports negative indices (`-1` = last panel, `-2` = second to last, etc). Used by ADHDinos.

## Config Reference (`comics.yml`)

Each comic entry supports the following fields:

| Field | Required | Description |
| --- | --- | --- |
| `name` | Yes | Plugin name (used in `settings.yml` and as the display name) |
| `dir` | Yes | Plugin directory name (the folder under the repo root) |
| `id` | Yes | TRMNL API plugin ID (set to `0` for new plugins, update after first push) |
| `polling_url` | Yes | RSS feed URL |
| `refresh_interval` | Yes | Polling interval in minutes |
| `no_screen_padding` | Yes | `true` for full-bleed, `false` for default padding |
| `description` | Yes | Short description shown in plugin metadata |
| `pattern` | Yes | Template pattern: `title`, `caption`, or `panels` |
| `panel_index` | No | For `panels` pattern: which panel to display (supports negative indices, e.g. `-1` for last) |
| `custom_fields_name` | No | Override the name shown in `custom_fields` (defaults to `name`) |

## Generated Files

For each comic, the generator produces 7 files:

| File | Location | Description |
| --- | --- | --- |
| `settings.yml` | `<dir>/src/` | Plugin configuration (strategy, polling URL, metadata) |
| `shared.liquid` | `<dir>/src/` | Main template with CSS, JS, and HTML (pattern-specific) |
| `full.liquid` | `<dir>/src/` | Full-screen layout entry point |
| `half_horizontal.liquid` | `<dir>/src/` | Half-horizontal layout entry point |
| `half_vertical.liquid` | `<dir>/src/` | Half-vertical layout entry point |
| `quadrant.liquid` | `<dir>/src/` | Quadrant layout entry point |
| `.trmnlp.yml` | `<dir>/` | Local dev server configuration |

All generated files are checked into git. They contain a "DO NOT EDIT DIRECTLY" comment header.

## How It Works

The generator uses Python with [Jinja2](https://jinja.palletsprojects.com/) for templating and [PyYAML](https://pyyaml.org/) for config parsing.

### Jinja2 Delimiter Customization

Since the generated `.liquid` files use Liquid's `{{ }}` and `{% %}` syntax, the Jinja2 templates use custom delimiters to avoid conflicts:

| Jinja2 Feature | Standard | Custom (used here) |
| --- | --- | --- |
| Variables | `{{ }}` | `<< >>` |
| Blocks | `{% %}` | `<% %>` |
| Comments | `{# #}` | `<# #>` |

This means Liquid syntax passes through the Jinja2 templates untouched, while `<< comic.name >>` is substituted by Jinja2.

### Template Files

Located in `_generator/templates/`:

- `settings.yml.j2` — Settings with per-comic variable substitution
- `layout.liquid.j2` — Static one-liner shared by all layout entry points
- `shared_title.liquid.j2` — Full `shared.liquid` for the `title` pattern
- `shared_caption.liquid.j2` — Full `shared.liquid` for the `caption` pattern
- `trmnlp.yml.j2` — Static `.trmnlp.yml` dev server config

## Workflow

- **Updating shared CSS or layout**: Edit the relevant `.j2` template in `_generator/templates/`, re-run the generator, review the git diff, then push with `./trmnlp.sh . push`.
- **After `trmnlp pull`**: The pull may overwrite generated files with server-side versions. Re-run the generator to restore canonical versions and check the diff.
- **Verifying consistency**: Run `generate.py --check` to confirm all generated files match what the generator would produce. Useful after pulls or manual edits.
