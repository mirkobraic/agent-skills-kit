---
name: ios-image-metadata
description: Use when tasks involve ImageIO metadata work on iOS/macOS, including EXIF, XMP, IPTC, GPS, TIFF, ICC, orientation behavior, metadata preservation, and interop mismatches across standards.
---

# iOS Image Metadata

## Use For

- The task touches EXIF/XMP/IPTC/GPS/TIFF/ICC metadata or ImageIO APIs.
- The user needs read/write/preserve guidance for metadata pipelines on Apple platforms.
- The issue is interop-related: orientation, timezone tags, GPS sign/ref, or XMP vs property-dictionary mismatch.
- The request asks format capability, lossless update behavior, or metadata-loss risk.

## Do Not Use For

- Pure UI/view-layer image tasks with no metadata requirements.
- Non-Apple metadata stacks where ImageIO and CoreGraphics APIs are not part of the solution.
- General Swift questions unrelated to image files, metadata schemas, or metadata persistence.

## Fast Workflow

1. Classify intent: `read`, `write`, `preserve`, `interop`, `format-capability`, or `MakerNote`.
2. Route to the smallest relevant reference first (table below).
3. Validate format constraints before proposing write logic.
4. Answer with exact API/key names plus lossless/data-loss caveats.

## Quick Routing

| Question Type | Start Here | Key Files |
|---|---|---|
| Which API should I use? | ImageIO overview | `references/imageio/README.md`, `references/imageio/cgimagesource.md`, `references/imageio/cgimagedestination.md`, `references/imageio/cgimage-metadata.md` |
| What exact property key/constant is needed? | Property key index | `references/imageio/property-keys.md` |
| What formats support this metadata? | Format matrix | `references/imageio/supported-formats.md`, `references/formats/README.md` |
| How do I write/update metadata safely? | Write behavior + pitfalls | `references/imageio/cgimagedestination.md`, `references/imageio/pitfalls.md` |
| Why are XMP and EXIF/IPTC values inconsistent? | Interop reconciliation | `references/interoperability/overlapping-fields.md`, `references/interoperability/mwg-guidelines.md`, `references/interoperability/imageio-behavior.md` |
| Orientation is rotated/mirrored incorrectly | Orientation mapping | `references/interoperability/orientation-mapping.md`, `references/exif/imageio-mapping.md` |
| GPS coordinates are wrong | GPS conventions | `references/gps/README.md`, `references/gps/coordinate-conventions.md` |
| IPTC in HEIC/PNG/WebP/AVIF | IPTC + XMP path | `references/iptc/README.md`, `references/xmp/README.md`, `references/xmp/imageio-integration.md` |
| Color profile or Display P3 issues | ICC reference | `references/icc/README.md`, `references/icc/common-profiles.md` |
| Vendor-specific camera fields | MakerNote docs | `references/makers/README.md` |

## Guardrails

- Prefer `CGImageSource`/`CGImageDestination` for metadata-critical flows; avoid `UIImage` paths unless preservation is explicit.
- Use exact constants (`kCGImageProperty...`) and name the parent dictionary.
- For GPS EXIF keys, use absolute values + `Ref` letters (`N/S`, `E/W`), not signed decimals.
- For EXIF times, include matching `OffsetTime*` tags when timezone matters.
- For IPTC, include IIM + XMP mappings when both exist; IPTC Extension is XMP-only.
- For writes, always state whether the path is lossless for the target format.
- Call out reconciliation limits between XMP and property dictionaries (including `IPTCDigest` behavior).

## Tooling

- `scripts/iptc_metadata.py` — read, write, or validate IPTC/XMP metadata via ExifTool CLI (`references/iptc/tooling.md`).

## References

- `references/README.md` — central index for all metadata reference areas
- `references/imageio/` — API behavior, property keys, format support, pitfalls
- `references/exif/`, `references/xmp/`, `references/iptc/`, `references/gps/`, `references/tiff/`, `references/icc/` — standards deep dives
- `references/interoperability/` — overlap/sync behavior, MWG guidance, orientation mapping
- `references/formats/` and `references/makers/` — container behavior and vendor MakerNotes
