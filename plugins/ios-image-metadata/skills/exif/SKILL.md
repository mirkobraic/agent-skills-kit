---
name: exif
description: Use when tasks involve EXIF metadata — tag definitions, IFD structure, MakerNote fields, EXIF-to-ImageIO key mapping, or vendor-specific camera metadata on iOS/macOS.
---

# EXIF — Exchangeable Image File Format

## Use For

- Looking up EXIF tag names, IDs, types, or allowed values.
- Understanding EXIF binary structure (IFD0, IFD1, EXIF IFD, Interop IFD).
- Mapping EXIF tags to `kCGImagePropertyExif*` ImageIO keys.
- Mapping EXIF tags to XMP equivalents (`exif:`, `tiff:`, `aux:` namespaces).
- Reading or interpreting MakerNote data (Apple, Canon, Nikon, others).
- EXIF-specific pitfalls (timezone tags, rational overflow, thumbnail drift).

## Do Not Use For

- GPS tags — use the `gps` skill.
- TIFF IFD0 tags (Make, Model, DateTime) — use the `tiff` skill.
- XMP data model or namespace questions — use the `xmp` skill.
- Cross-standard sync issues (EXIF vs XMP conflicts) — use `metadata-sync`.

## Workflow

1. Identify the EXIF tag by name or hex ID.
2. Look up the tag in `references/exif/tag-reference.md`.
3. Find the ImageIO key mapping in `references/exif/imageio-mapping.md`.
4. Check pitfalls in `references/exif/pitfalls.md` for known edge cases.

## Guardrails

- For EXIF times, include matching `OffsetTime*` tags when timezone matters.
- Rational values (e.g., ExposureTime, FNumber) must be stored as RATIONAL, not ASCII.
- MakerNote data is opaque and vendor-specific — do not modify unless using vendor documentation.

## References

- `references/exif/` — EXIF standard reference
  - `tag-reference.md` — complete tag list with types and values
  - `technical-structure.md` — IFD layout, byte order, offsets
  - `imageio-mapping.md` — EXIF tags to ImageIO property keys
  - `xmp-mapping.md` — EXIF tags to XMP properties
  - `makernote.md` — MakerNote format and parsing
  - `pitfalls.md` — common EXIF pitfalls
- `references/makers/` — vendor-specific MakerNote documentation
  - `apple.md`, `canon.md`, `nikon.md`, `other-vendors.md`
  - `makernote-concept.md` — how MakerNotes work
