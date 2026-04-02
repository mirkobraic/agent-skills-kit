---
name: iptc
description: Use when tasks involve IPTC photo metadata — IIM legacy fields, IPTC Core/Extension via XMP, editorial/rights metadata, or the iptc_metadata.py tooling script on iOS/macOS.
---

# IPTC Photo Metadata Standard

## Use For

- Writing or reading editorial metadata (headline, caption, keywords, creator, copyright).
- Understanding IPTC IIM (legacy binary) vs IPTC Core/Extension (XMP).
- Using `kCGImagePropertyIPTCDictionary` for IIM fields in JPEG/TIFF.
- Using `kCGImageMetadataNamespaceIPTCCore` / `IPTCExtension` for XMP-based IPTC.
- Validating IPTC metadata with the `iptc_metadata.py` script.

## Do Not Use For

- EXIF capture metadata (shutter speed, ISO) — use the `exif` skill.
- XMP data model or custom namespaces — use the `xmp` skill.
- Cross-standard sync (IPTC vs EXIF conflicts) — use `metadata-sync`.

## Workflow

1. Determine if the target format supports IIM (`kCGImagePropertyIPTCDictionary`) or requires XMP.
2. For JPEG/TIFF: can use both IIM and XMP paths; keep them in sync.
3. For HEIF/WebP/AVIF/PNG: must use XMP path (`Iptc4xmpCore:`, `Iptc4xmpExt:`).
4. For batch validation, use `scripts/iptc_metadata.py`.

## Guardrails

- IPTC IIM is only supported in JPEG and TIFF. For modern formats, use XMP.
- When both IIM and XMP exist, include both mappings to prevent sync drift.
- IPTC Extension is XMP-only — no IIM equivalent exists.
- `IPTCDigest` tag tracks IIM/XMP sync state; updating one side without the other causes readers to flag conflicts.

## Tooling

- `scripts/iptc_metadata.py` — read, write, or validate IPTC/XMP metadata via ExifTool CLI.
- See `references/tooling.md` for usage details.

## References

- `references/`
  - `README.md` — IPTC overview and ImageIO access
  - `standard-overview.md` — IIM vs Core vs Extension
  - `property-reference.md` — complete IPTC property list
  - `tooling.md` — ExifTool and script usage
- `assets/reference-images/` — IPTC reference test image
