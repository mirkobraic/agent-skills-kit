---
name: xmp
description: Use when tasks involve XMP metadata — data model, namespaces, serialization, embedding in image formats, or CGImageMetadata XMP APIs on iOS/macOS.
---

# XMP — Extensible Metadata Platform

## Use For

- Understanding XMP data model (properties, qualifiers, alt/bag/seq arrays).
- Looking up standard XMP namespaces (`dc:`, `xmp:`, `photoshop:`, `exif:`, `tiff:`, `Iptc4xmpCore:`, etc.).
- Embedding or extracting XMP packets in specific image formats.
- Using `CGImageMetadata` APIs for XMP-level metadata access.
- Custom namespace registration and property creation.

## Do Not Use For

- EXIF tag lookup or IFD structure — use the `exif` skill.
- IPTC IIM fields or editorial metadata — use the `iptc` skill.
- Cross-standard reconciliation — use `metadata-sync`.

## Workflow

1. Identify the XMP namespace and property name.
2. Check if ImageIO exposes it via `CGImageMetadata` in `references/imageio-integration.md`.
3. For custom properties, register the namespace prefix first.
4. Verify embedding support for the target format.

## Guardrails

- XMP is the only metadata channel for IPTC Extension, PLUS licensing, and custom properties.
- `CGImageMetadata` operates on XMP; property dictionaries (`kCGImageProperty*`) are a separate path.
- Not all XMP written by third-party tools round-trips through ImageIO — check `pitfalls.md`.

## References

- `references/`
  - `README.md` — XMP overview
  - `data-model.md` — properties, qualifiers, structured types
  - `namespaces.md` — standard namespace URIs and prefixes
  - `embedding.md` — how XMP packets sit inside JPEG, HEIF, PNG, etc.
  - `imageio-integration.md` — CGImageMetadata API usage
  - `pitfalls.md` — common XMP pitfalls
