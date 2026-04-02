# IPTC Photo Metadata Standard

> Part of [iOS Image Metadata Skill](../../SKILL.md) · [References Index](../README.md)

IPTC Photo Metadata Standard (Core 1.5, Extension 1.9). Editorial, descriptive,
and rights metadata for images.

## ImageIO Access

- `kCGImagePropertyIPTCDictionary` (iOS 4.0) — ~40 keys (IIM legacy, JPEG/TIFF only)
- `kCGImageMetadataNamespaceIPTCCore` / `kCGImageMetadataPrefixIPTCCore` — Core via XMP
- `kCGImageMetadataNamespaceIPTCExtension` / `kCGImageMetadataPrefixIPTCExtension` — Extension via XMP

> **Note:** IPTC IIM is only supported in JPEG and TIFF. For modern formats
> (HEIF, WebP, AVIF, PNG), IPTC metadata must be written via XMP using the
> `Iptc4xmpCore` and `Iptc4xmpExt` namespaces.

## File Index

| File | Contents |
|------|----------|
| [standard-overview.md](standard-overview.md) | Schema overview, Core vs Extension, XMP namespaces, minimal fields, AI metadata, accessibility, preservation |
| [tooling.md](tooling.md) | ExifTool CLI wrapper documentation |
| [property-reference.md](property-reference.md) | All 66 properties + 19 structures: XMP IDs, IIM mappings, types, cardinality |

## Planned Additional Content

- Complete key reference for `kCGImagePropertyIPTCDictionary`
- IPTC Extension properties accessible via CGImageMetadata
- Mapping between IIM datasets and XMP properties
