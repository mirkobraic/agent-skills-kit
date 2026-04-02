---
name: tiff
description: Use when tasks involve TIFF IFD metadata — Make, Model, DateTime, orientation, resolution, software tags, or kCGImagePropertyTIFF* keys on iOS/macOS.
---

# TIFF IFD Reference

## Use For

- Looking up TIFF IFD0 tags (Make, Model, DateTime, Software, Artist, Copyright, etc.).
- Understanding TIFF as a structural container for EXIF, GPS, and other IFDs.
- Mapping TIFF tags to `kCGImagePropertyTIFF*` ImageIO keys.
- Resolution tags (XResolution, YResolution, ResolutionUnit).

## Do Not Use For

- EXIF IFD tags (shutter speed, ISO, etc.) — use the `exif` skill.
- GPS IFD tags — use the `gps` skill.
- Orientation mapping across systems — use `metadata-sync`.

## Workflow

1. Look up the tag in `references/tag-reference.md`.
2. Find the ImageIO key in `references/imageio-mapping.md`.
3. For container questions, check `references/tiff-as-container.md`.

## Guardrails

- TIFF `DateTime` is local time with no timezone; pair with EXIF `OffsetTime` when timezone matters.
- TIFF orientation tag (tag 274) is shared with EXIF; see `metadata-sync` for cross-system mapping.
- TIFF is the structural foundation for JPEG EXIF, DNG, HEIF, and most RAW formats.

## References

- `references/`
  - `README.md` — TIFF IFD overview
  - `tag-reference.md` — all TIFF IFD0 tags
  - `imageio-mapping.md` — TIFF tags to ImageIO keys
  - `tiff-as-container.md` — TIFF as multi-IFD container
  - `pitfalls.md` — common TIFF pitfalls
