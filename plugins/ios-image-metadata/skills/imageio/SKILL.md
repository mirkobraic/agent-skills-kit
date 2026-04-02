---
name: imageio
description: Use when tasks involve Apple's ImageIO framework — CGImageSource, CGImageDestination, CGImageMetadata APIs, property keys, format support matrices, and read/write/preserve workflows on iOS/macOS.
---

# ImageIO Framework

## Use For

- Reading or writing image metadata via `CGImageSource` / `CGImageDestination`.
- Looking up `kCGImageProperty*` constants or property dictionary keys.
- Determining which image formats support specific metadata standards.
- Understanding lossless vs lossy metadata update paths.
- Working with `CGImageMetadata` (XMP-level) vs property dictionaries.
- Auxiliary data (depth maps, HDR gain maps, portrait mattes).

## Do Not Use For

- Questions about a specific metadata standard (EXIF, XMP, IPTC, GPS, TIFF, ICC) — use the dedicated skill.
- Cross-standard reconciliation or orientation mapping — use `metadata-sync`.
- Pure UI/view-layer image tasks with no metadata requirements.

## Workflow

1. Identify the operation: `read`, `write`, `thumbnail`, `incremental-store`, or `auxiliary-data`.
2. Check format support in `references/formats/` if the format is non-JPEG.
3. Use exact `kCGImageProperty*` constants and name the parent dictionary.
4. State whether the write path is lossless for the target format.

## Guardrails

- Prefer `CGImageSource`/`CGImageDestination` for metadata-critical flows; avoid `UIImage` paths unless preservation is explicit.
- `CGImageDestination` with `kCGImageDestinationMergeMetadata` merges into existing; without it, supplied metadata replaces all.
- Not all formats support all metadata dictionaries — check format references before proposing write logic.

## References

- `references/imageio/` — API behavior, property keys, pitfalls
  - `cgimagesource.md` — reading images, metadata, thumbnails
  - `cgimagedestination.md` — writing images, metadata, auxiliary data
  - `cgimage-metadata.md` — XMP-level metadata API
  - `property-keys.md` — complete property key index
  - `supported-formats.md` — format support matrix
  - `auxiliary-data.md` — depth, disparity, HDR gain maps
  - `pitfalls.md` — common ImageIO pitfalls
- `references/formats/` — per-format metadata capabilities
  - `jpeg.md`, `heif.md`, `png.md`, `webp.md`, `gif.md`, `dng-raw.md`, `other-formats.md`
