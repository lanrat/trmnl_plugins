---
name: trmnl-og-2bit-reference
description: >-
  Practical and technical constraints for the TRMNL OG 2-bit (4-shade grayscale)
  display mode at 800x480. Use when designing, generating, or reviewing plugin
  markup or image assets targeting TRMNL OG 2-bit grayscale, e-ink 4-shade
  palettes, 2-bit PNG workflows, or OG V2 display output.
---

# TRMNL OG 2-Bit Reference

This file explains the practical and technical constraints of the TRMNL OG 2-bit display mode so an agent can design and generate correct plugin output.

## What this target is

TRMNL OG 2-bit is the 7.5" 800x480 OG display running in 4-shade grayscale mode instead of standard 1-bit monochrome.
It is intended for OG model devices with grayscale + fast refresh support enabled.
TRMNL documents 2-bit PNG support as experimental and available on OG devices running firmware 1.6.0+.

## Core specs

- Device family: TRMNL OG / OG V2 references in framework docs.
- Resolution: 800x480.
- Display mode: 2-bit grayscale.
- Effective grayscale palette size: 4 shades.
- Intended image format for 2-bit mode: PNG.
- 2-bit image workflow is documented for Alias/Redirect style image delivery and DIY-compatible rendering workflows.
- 1-bit BMP3 and 1-bit PNG are also supported, but they are different targets.

## Color / grayscale model

Treat 2-bit mode as exactly 4 grayscale values:
- `#000000`
- `#555555`
- `#AAAAAA`
- `#FFFFFF`

Do not assume smooth gradients.
Do not assume anti-aliased web-style rendering will survive conversion well.
Do not design as though full grayscale or color exists.
All visual decisions must still work when reduced to four tones only.

## Firmware and support notes

- TRMNL documents 2-bit PNG as experimental.
- It is meant for OG devices on firmware 1.6.0 or newer.
- The docs describe it as tied to grayscale + fast refresh support.
- If compatibility is uncertain, prefer a safe 1-bit-friendly design.

## Agent design rules

When designing for TRMNL OG 2-bit:
- Always target 800x480 first.
- Design for 4 shades only.
- Use contrast in large blocks, not subtle tonal nuance.
- Prefer clean edges and simple shapes.
- Prefer hierarchy from size, spacing, and grouping more than tonal complexity.
- Keep layouts glanceable from a distance.
- Assume e-ink refresh artifacts and avoid "busy" compositions.

## Tone usage rules

Use the 4 shades intentionally:
- Black (`#000000`) for primary text and strongest separators.
- Dark gray (`#555555`) for secondary text or chart strokes.
- Light gray (`#AAAAAA`) for soft fills, muted dividers, and background grouping.
- White (`#FFFFFF`) as the page/background or negative space.

Avoid:
- relying on tiny differences between `#555555` and `#AAAAAA`
- thin low-contrast lines
- subtle shaded textures
- photographic detail that depends on midtone richness
- UI styles that require smooth gradients

## Typography rules

In 2-bit mode:
- Use fewer text sizes, but make hierarchy obvious.
- Keep text short.
- Prefer stronger font-size contrast over many weight variations.
- Use dark text on light backgrounds most of the time.
- Keep secondary labels visibly subordinate.
- Avoid long paragraphs, condensed data tables, and tiny metadata.

## Layout rules

Default to layouts that survive harsh grayscale reduction:
- one primary focal block
- one supporting section
- optional small footer/meta section

Prefer:
- larger modules
- obvious spacing
- stable alignment
- simple columns or stacked blocks

Avoid:
- dense dashboards
- micro-cards
- packed KPI walls
- decorative boxes everywhere
- thin separators between many adjacent regions

## Charts and graphics

2-bit can improve gradients and charts compared with 1-bit, but it is still only 4 shades.

For charts:
- prefer line, bar, sparkline, or very simple area shapes
- use direct labels where possible
- reduce axes, ticks, and legends
- make strokes thick enough to survive e-ink rendering
- keep chart backgrounds plain
- never rely on color hue; only rely on value contrast

For images/illustrations:
- use high-contrast source material
- simplify before conversion
- prefer bold silhouettes and strong composition
- avoid detailed photos unless specifically prepared for 4-shade dithering

## TRMNL Framework behavior

TRMNL Framework UI supports bit-depth-aware utilities.
The docs explicitly show `1bit:`, `2bit:`, and `4bit:` prefixes for bit-depth responsive behavior.
Framework docs also show that display/visibility utilities can target 2-bit devices specifically, including OG V2-oriented 2-bit behavior.

Use this when available:
- make certain elements visible only for 2-bit targets
- adjust alignment for 2-bit targets
- simplify or enhance a layout depending on available bit depth

Do not assume every class works identically without checking the framework docs in the project.

## Plugin rendering context

For marketplace plugins:
- TRMNL generates screens by POSTing to your `plugin_markup_url`.
- The request includes `user_uuid`.
- The request includes a `trmnl` object with metadata such as device dimensions and timezone.
- The request uses a Bearer token in the `Authorization` header.
- Your server returns HTML within root nodes such as `markup` and other layout-specific nodes.

Use the incoming TRMNL metadata when deciding layout behavior.
Do not hardcode assumptions that ignore device/layout metadata if the plugin supports multiple layouts.

## Image-generation specifics

TRMNL documents a 2-bit PNG workflow using ImageMagick with a 4-color grayscale palette.

Documented palette generation:
```bash
magick -size 4x1 xc:#000000 xc:#555555 xc:#aaaaaa xc:#ffffff +append -type Palette colormap-2bit.png
```

Documented 2-bit conversion example:
```bash
magick input.jpeg -resize 800x480\! -dither FloydSteinberg -remap colormap-2bit.png -define png:bit-depth=2 -define png:color-type=0 output.png
```

When creating direct image assets for TRMNL OG 2-bit:
- output PNG
- force 800x480
- remap to the exact 4-shade palette
- test that the result still looks clean after dithering

## What the agent must never assume

Never assume:
- full grayscale beyond 4 shades
- color hue support
- that a normal web screenshot will look good on-device
- that subtle shadows or gradients will render cleanly
- that 2-bit is always enabled for every user/plugin
- that every plugin should use image rendering instead of TRMNL markup
- that "prettier" means more visual complexity

## Safe design defaults

If uncertain, do this:
- white background
- black primary text
- dark gray secondary text
- light gray section fills only when they improve grouping
- one hero metric or one hero list
- short labels
- bold spacing
- minimal dividers
- no decorative gradients
- no fragile tiny details

## Quality checklist

Before finalizing any TRMNL OG 2-bit design, verify:
1. It still works at exactly 800x480.
2. It uses only 4 grayscale values conceptually.
3. The main message is readable in 3 seconds.
4. Long strings cannot destroy the layout.
5. Empty states still look intentional.
6. Lines, icons, and chart strokes are thick enough.
7. No important meaning depends on color hue.
8. The design would still be acceptable if downgraded to 1-bit.
9. Any image asset is exported as a proper TRMNL-compatible 2-bit PNG when relevant.
10. The screen is cleaner than a normal web dashboard, not busier.

## Practical interpretation

Think of TRMNL OG 2-bit as:
- an e-ink editorial card
- not a web app
- not a tablet UI
- not a full grayscale art canvas

The best 2-bit TRMNL designs use the extra shades to improve clarity and softness, not to cram in more detail.