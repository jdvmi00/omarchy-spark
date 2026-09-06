# Artwork

Hero, announcement card, wallpaper and icon for the port, in Omarchy's pixel
wordmark style with the Tokyo Night palette that the Spark installation uses by
default. The SVG files are the sources; the PNGs are rendered from them with
JetBrains Mono installed.

| File | Use |
| --- | --- |
| `hero.png` (2560×1280), `hero.svg` | README banner and the GitHub social preview (repository Settings → Social preview accepts the PNG) |
| `announcement.png` (2400×1350), `announcement.svg` | Release or forum announcement card, 16:9 |
| `wallpaper-3840x2160.png`, `wallpaper.svg` | Desktop wallpaper for the Spark's 4K display; drop it into an Omarchy theme's `backgrounds/` |
| `icon.png` (1024), `icon-256.png`, `icon.svg` | Repository or organization avatar, app icon |

The wordmark is Omarchy's MIT-licensed logo with new `s`, `p` and `k` letters
drawn on its 15-pixel stair-step grid; `a` and `r` reuse the original glyphs.
The spark glyph and the bracket icon are original. Colors come from Omarchy's
`themes/tokyo-night/colors.toml`; the amber is that theme's yellow. See
THIRD_PARTY.md for provenance. NVIDIA and DGX Spark are named in plain text
only; no NVIDIA logo or trademark artwork is used.

To re-render after editing an SVG:

```sh
rsvg-convert -w 2560 hero.svg -o hero.png
rsvg-convert -w 3840 wallpaper.svg -o wallpaper-3840x2160.png
```
