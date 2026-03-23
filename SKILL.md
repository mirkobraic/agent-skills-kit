---
name: ios-image-metadata-skill
description: Use when tasks involve reading, writing, debugging, or preserving image metadata on iOS/macOS with ImageIO, including EXIF, XMP, IPTC, GPS, TIFF, ICC, format-specific metadata behavior, orientation mapping, and cross-standard sync between property dictionaries and CGImageMetadata.
---

# iOS Image Metadata Skill

## When to Use

- The task touches EXIF/XMP/IPTC/GPS/TIFF/ICC metadata or ImageIO APIs.
- The user needs read/write/preserve guidance for metadata pipelines.
- The issue is interop-related: orientation, timezone, GPS sign/ref, or XMP vs property-dict mismatch.
- The request asks format capability or lossless metadata-update constraints.

## When Not to Use

- Pure UI/view-layer image tasks with no metadata requirements.
- Non-Apple metadata stacks where ImageIO and CoreGraphics APIs are not part of the solution.
- General Swift questions unrelated to image files, metadata schemas, or metadata persistence.

## Workflow

1. Classify intent: read, write, preserve, interoperability, format capability, or MakerNote.
2. Route to the smallest relevant reference first (table below).
3. Validate format constraints before proposing write logic.
4. Answer with exact API/key names and data-loss caveats.

## Quick Routing

| Question Type | Start Here | Key Files |
|---|---|---|
| Which API should I use? | ImageIO overview | `references/imageio/README.md`, `references/imageio/cgimagesource.md`, `references/imageio/cgimagedestination.md`, `references/imageio/cgimage-metadata.md` |
| What exact property key/constant is needed? | Property key index | `references/imageio/property-keys.md` |
| What formats support this metadata? | Format matrix | `references/imageio/supported-formats.md`, `references/formats/README.md` |
| How do I write/update metadata safely? | Write behavior + pitfalls | `references/imageio/cgimagedestination.md`, `references/imageio/pitfalls.md` |
| Why are XMP and EXIF/IPTC values inconsistent? | Interop reconciliation | `references/interoperability/overlapping-fields.md`, `references/interoperability/mwg-guidelines.md`, `references/interoperability/imageio-behavior.md` |
| Orientation is rotated/mirrored incorrectly | Orientation mapping | `references/interoperability/orientation-mapping.md`, `references/exif/orientation.md` |
| GPS coordinates are wrong | GPS conventions | `references/gps/README.md`, `references/gps/coordinate-conventions.md` |
| IPTC in HEIC/PNG/WebP/AVIF | IPTC + XMP path | `references/iptc/README.md`, `references/xmp/README.md`, `references/xmp/imageio-integration.md` |
| Color profile or Display P3 issues | ICC reference | `references/icc/README.md`, `references/icc/common-profiles.md` |
| Vendor-specific camera fields | MakerNote docs | `references/makers/README.md` |

## Key Concepts

- **Two metadata APIs in ImageIO**
  - Property dictionaries via `CGImageSourceCopyPropertiesAtIndex`.
  - XMP tree via `CGImageSourceCopyMetadataAtIndex`.
- **Bridge behavior exists but is not full MWG conformance**
  - ImageIO often auto-synthesizes between property dictionaries and XMP.
  - ImageIO does not reconcile `IPTCDigest`.
- **Format dictates capability**
  - IPTC IIM is legacy and mainly JPEG/TIFF.
  - Modern IPTC flows use XMP (`Iptc4xmpCore`, `Iptc4xmpExt`).
- **Lossless metadata update is limited**
  - `CGImageDestinationCopyImageSource` is lossless only for specific formats.
- **Metadata-loss risk is real**
  - `UIImage` and some image-processing paths can strip or alter metadata unless explicitly preserved.

## Tooling

- `scripts/iptc_metadata.py` — read, write, or validate IPTC/XMP metadata via ExifTool CLI (`references/iptc/tooling.md`).

## Response Guidance

- Use exact Apple API names (`kCGImagePropertyExifDateTimeOriginal`, not "EXIF date").
- When referencing property keys, include the dictionary they belong to.
- For EXIF/ImageIO GPS dictionary keys, note the absolute-value + reference-letter convention (not signed decimals).
- For EXIF timestamps, mention the matching `OffsetTime*` tag (`OffsetTime`, `OffsetTimeOriginal`, or `OffsetTimeDigitized`) for timezone awareness.
- For IPTC, provide both IIM and XMP mappings when both exist; note Extension fields are XMP-only.
- Warn about metadata loss through `UIImage` — always recommend `CGImageSource`/`CGImageDestination`.
- For metadata writing, always state whether lossless update is possible for the target format.

## References

- `references/README.md` — central index for all metadata reference areas
- `references/imageio/` — APIs, property keys, formats, auxiliary data, pitfalls
- `references/exif/`, `references/xmp/`, `references/iptc/`, `references/gps/`, `references/tiff/`, `references/icc/` — standard-specific deep dives
- `references/interoperability/` — MWG sync rules, overlap mapping, ImageIO behavior, orientation mapping
- `references/formats/` and `references/makers/` — container behavior and vendor MakerNotes
- `references/iptc/tooling.md` and `PLAN.md` — IPTC CLI workflow and repo roadmap
