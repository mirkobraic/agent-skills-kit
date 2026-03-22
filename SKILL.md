---
name: ios-image-metadata-skill
description: Expert guidance on reading, writing, and preserving image metadata on iOS/macOS using Apple's ImageIO framework. Covers all metadata standards (EXIF, XMP, IPTC, GPS, TIFF, ICC), format-specific properties, auxiliary data (depth maps, HDR gain maps, portrait mattes, spatial photos), and manufacturer MakerNotes. Use when tasks involve image metadata, photo properties, EXIF data, XMP tags, IPTC fields, GPS coordinates in images, ICC color profiles, CGImageSource, CGImageDestination, CGImageMetadata, or any ImageIO framework usage.
---

# iOS Image Metadata Skill

## Workflow

1. Identify the metadata domain: which standard (EXIF, XMP, IPTC, GPS, TIFF, ICC), which format, or which ImageIO API.
2. Consult the appropriate reference in `references/`:
   - **ImageIO framework** → `references/imageio/` (APIs, supported formats, all property keys, auxiliary data, pitfalls)
   - **EXIF** → `references/exif/` (camera settings, exposure, timestamps, lens)
   - **XMP** → `references/xmp/` (namespaces, value types, embedding locations)
   - **IPTC** → `references/iptc/` (editorial metadata, Core vs Extension, IIM vs XMP)
   - **GPS** → `references/gps/` (coordinates, direction, speed, altitude)
   - **TIFF** → `references/tiff/` (make/model, orientation, artist, copyright)
   - **ICC** → `references/icc/` (color profiles, color models)
   - **Format-specific** → `references/formats/` (JPEG, PNG, GIF, HEIF, DNG, WebP, etc.)
   - **MakerNotes** → `references/makers/` (Apple, Canon, Nikon, etc.)
   - **Cross-standard sync** → `references/interoperability/` (MWG rules, field mapping)
3. For property key lookups, `references/imageio/property-keys.md` has the complete list of every `kCGImageProperty*` constant.
4. For format support questions, `references/imageio/supported-formats.md` has the full matrix.

## Key Concepts

**Two metadata APIs in ImageIO:**
- **Property dictionaries** (`CGImageSourceCopyPropertiesAtIndex`) — flat key–value for standard fields (EXIF, GPS, TIFF, IPTC). See `references/imageio/cgimagesource.md`.
- **XMP metadata tree** (`CGImageSourceCopyMetadataAtIndex`) — structured access to any XMP namespace. See `references/imageio/cgimage-metadata.md`.

**Format determines which standards are available:**
- JPEG and TIFF support everything (EXIF + XMP + IPTC IIM + ICC + GPS).
- HEIF/HEIC supports EXIF + XMP + ICC (no IPTC IIM).
- PNG, WebP, AVIF support XMP + ICC only.
- IPTC IIM is JPEG/TIFF only — use XMP namespaces (`Iptc4xmpCore`, `Iptc4xmpExt`) for modern formats.

## Tools

- `scripts/iptc_metadata.py` — read, write, or validate IPTC/XMP metadata via ExifTool CLI. See `references/iptc/tooling.md` for usage.

## Response Guidance

- Use exact Apple API names (`kCGImagePropertyExifDateTimeOriginal`, not "EXIF date").
- When referencing property keys, include the dictionary they belong to.
- For GPS coordinates, always note the absolute-value + reference-letter convention (not signed decimals).
- For EXIF timestamps, mention `OffsetTimeOriginal` for timezone awareness.
- For IPTC, provide both IIM and XMP mappings when both exist; note Extension fields are XMP-only.
- Warn about metadata loss through `UIImage` — always recommend `CGImageSource`/`CGImageDestination`.
- For metadata writing, note whether lossless update is possible (JPEG/PNG/TIFF/PSD yes, HEIC no).

## References

- `references/imageio/` — ImageIO framework (complete API surface, all property keys, formats, pitfalls)
- `references/iptc/standard-overview.md` — IPTC schema overview, Core vs Extension, XMP namespaces
- `references/iptc/user-guide.md` — Practical IPTC usage, minimal fields, AI metadata, accessibility
- `references/iptc/tooling.md` — ExifTool CLI wrapper and tag naming
- See `PLAN.md` for the full roadmap and folder contents.
