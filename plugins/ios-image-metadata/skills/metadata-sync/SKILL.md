---
name: metadata-sync
description: Use when tasks involve cross-standard metadata conflicts — EXIF vs XMP vs IPTC sync, orientation mapping across systems, MWG reconciliation, or metadata loss during format conversion on iOS/macOS.
---

# Metadata Sync — Cross-Standard Reconciliation

## Use For

- Values differ between EXIF, IPTC IIM, and XMP for the same field.
- Orientation is wrong or rotated after save/export/conversion.
- Understanding MWG (Metadata Working Group) reconciliation guidelines.
- ImageIO auto-sync behavior between property dictionaries and XMP.
- Metadata loss during format conversion (e.g., JPEG to HEIF, PNG to WebP).
- `UIImage` or `CIImage` stripping metadata silently.

## Do Not Use For

- Questions about a single metadata standard in isolation — use the dedicated skill.
- ImageIO API usage without a cross-standard conflict — use the `imageio` skill.

## Workflow

1. Identify which standards are in conflict (EXIF vs XMP, IPTC vs XMP, etc.).
2. Check overlapping field mappings in `references/overlapping-fields.md`.
3. Review ImageIO sync behavior in `references/imageio-behavior.md`.
4. For orientation issues, use `references/orientation-mapping.md`.
5. For reconciliation strategy, follow MWG guidelines in `references/mwg-guidelines.md`.

## Guardrails

- ImageIO syncs some fields automatically between property dictionaries and XMP — but not all.
- `IPTCDigest` tracks whether IIM and XMP are in sync; mismatches cause reader warnings.
- Orientation has three numbering systems (EXIF 1-8, UIImage.Orientation raw values, CGImagePropertyOrientation) — they do not match.
- Format conversion through `UIImage` or `CIImage` can strip all metadata unless explicitly preserved.
- Social media and messaging apps routinely strip metadata on upload.

## References

- `references/`
  - `README.md` — interoperability overview
  - `overlapping-fields.md` — field-by-field EXIF/IPTC/XMP mapping
  - `mwg-guidelines.md` — MWG reconciliation algorithm
  - `imageio-behavior.md` — ImageIO auto-sync details
  - `orientation-mapping.md` — orientation value mapping across systems
  - `pitfalls.md` — 15 named cross-standard pitfalls
