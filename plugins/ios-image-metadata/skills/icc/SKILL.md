---
name: icc
description: Use when tasks involve ICC color profiles — sRGB, Display P3, Adobe RGB, profile embedding, color space conversion, or kCGImagePropertyProfileName on iOS/macOS.
---

# ICC Color Profiles

## Use For

- Understanding ICC profile basics (v2 vs v4, PCS, rendering intents).
- Common profiles: sRGB, Display P3, Adobe RGB, ProPhoto RGB.
- Embedding or extracting ICC profiles in image formats.
- ImageIO integration for color profile handling.
- Display P3 wide color issues on Apple platforms.

## Do Not Use For

- Color management at the UI/rendering layer (this covers metadata-level profiles).
- EXIF ColorSpace tag — use the `exif` skill (but check `metadata-sync` for EXIF/ICC conflicts).

## Workflow

1. Identify the current and target color space.
2. Check embedding support for the format in `references/embedding.md`.
3. Use `references/imageio-integration.md` for API details.
4. Review `references/pitfalls.md` for common issues.

## Guardrails

- EXIF ColorSpace tag (1 = sRGB, 65535 = uncalibrated) does not always match the embedded ICC profile.
- Display P3 images saved as JPEG may lose wide gamut if the profile is stripped.
- ImageIO preserves ICC profiles during metadata-only updates; `UIImage` paths may not.

## References

- `references/`
  - `README.md` — ICC overview
  - `profile-basics.md` — ICC spec fundamentals
  - `common-profiles.md` — sRGB, Display P3, Adobe RGB, ProPhoto
  - `embedding.md` — per-format ICC embedding
  - `imageio-integration.md` — ImageIO color profile APIs
  - `pitfalls.md` — common ICC pitfalls
