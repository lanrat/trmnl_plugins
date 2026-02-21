# Claud

This repository contains the source for all of my Trmnl Plugins.
TRMNL is an e-ink display device designed to help users stay focused and calm by showing glanceable, distraction-free information dashboards. It supports a plugin ecosystem that allows developers to build and share custom screen layouts delivering data from any source to the device.

Each plugin is in its own folder, and is synced both to github and to the Trmnl API.

## trmnlp Sync Tool

`trmnlp.sh` is a wrapper around the `trmnl/trmnlp` Docker container that syncs plugin files with the TRMNL API. Requires `trmnl.env` with `TRMNL_API_KEY` (auto-created on first run).

```bash
./trmnlp.sh <plugin-dir> <command>
```

Commands:
- `init` — Scaffold a new plugin
- `serve` — Local dev server at http://localhost:4567
- `pull` — Download plugin from TRMNL server
- `push` — Upload plugin to TRMNL server

Use `.` as plugin-dir to run on all plugins (any dir containing `src/settings.yml`).
`./trmnlp.sh pull` (no plugin-dir) updates the Docker image itself.

## Plugin Architecture

### Template Structure

Each plugin has `src/` with these files:
- `shared.liquid` — Main template (shared markup and styles)
- `full.liquid`, `half_horizontal.liquid`, `half_vertical.liquid`, `quadrant.liquid` — Layout-specific entry points that typically render the shared template
- `settings.yml` — Plugin config (strategy, polling, custom fields, `no_screen_padding`, `dark_mode`, etc.)

### Framework Layout Hierarchy

The TRMNL framework wraps plugin content in: **Screen → View → Layout**

The `screen` class sets CSS variables for the target device:

- `--screen-w`, `--screen-h` — Device dimensions (e.g., 800x480 for OG, 1200x825 for Inkplate 10)
- `--full-w`, `--full-h` — Dimensions minus padding
- `--ui-scale`, `--gap-scale`, `--color-depth`

### Server-Side Rendering

Plugins are rendered to PNG by a headless browser on TRMNL's server. The screenshot captures the `screen` container element, **not the browser viewport**. This means:

- **Do NOT use `position: fixed` or viewport units (`100vw`/`100vh`)** — these reference the browser viewport which may not match the device's screen container
- **Use percentage-based sizing (`width: 100%; height: 100%`) and flexbox** — these size relative to the framework's screen container and work across all devices

### Proven Layout Pattern

All image/content plugins should use this pattern (works across all device sizes):

```css
.view { height: 100%; width: 100%; display: flex; flex-direction: column; overflow: hidden; position: relative; }
.content-container { flex: 1; display: flex; overflow: hidden; min-height: 0; width: 100%; }
.title_bar { flex-shrink: 0; }
```

### Responsive Breakpoints

Size-based (mobile-first): `sm:` (600px+), `md:` (800px+), `lg:` (1024px+)
Bit-depth (non-progressive): `1bit:`, `2bit:`, `4bit:`

### Settings Notes

- `no_screen_padding: 'yes'` — Removes framework padding for full-bleed content (adds `screen--no-bleed`)
- `no_screen_padding: 'no'` — Keeps default gap-based padding around content
- The `trmnlp` sync tool writes files with CRLF line endings; the repo normalizes to LF via `.gitattributes`

## Developer Docs

- Settings Overview: <https://help.trmnl.com/en/articles/10542599-importing-and-exporting-private-plugins>
- API and Overview: <https://docs.trmnl.com/go/>
- Plugin Marketplace: <https://docs.trmnl.com/go/plugin-marketplace/introduction>
- Webhooks: <https://docs.trmnl.com/go/private-plugins/webhooks>
- Screen Templating: <https://docs.trmnl.com/go/private-plugins/templates>
- Graphics: <https://docs.trmnl.com/go/private-plugins/templates-advanced>
- Reusing Markup: <https://docs.trmnl.com/go/reusing-markup>
- UI Design Framework: <https://trmnl.com/framework/docs>
- UI Examples: <https://trmnl.com/framework/examples>
