# IPTC Photo Metadata Standard

IPTC Photo Metadata Standard (Core 1.5, Extension 1.9). Editorial, descriptive,
and rights metadata for images.

## ImageIO Access

- `kCGImagePropertyIPTCDictionary` (iOS 4.0) — ~40 keys (IIM legacy, JPEG/TIFF only)
- `kCGImageMetadataNamespaceIPTCCore` / `kCGImageMetadataPrefixIPTCCore` — Core via XMP
- `kCGImageMetadataNamespaceIPTCExtension` / `kCGImageMetadataPrefixIPTCExtension` — Extension via XMP

> **Note:** IPTC IIM is only supported in JPEG and TIFF. For modern formats
> (HEIF, WebP, AVIF, PNG), IPTC metadata must be written via XMP using the
> `Iptc4xmpCore` and `Iptc4xmpExt` namespaces.

## Files

| File | Contents |
|------|----------|
| [standard-overview.md](standard-overview.md) | Schema overview, Core vs Extension, data types, TechReference, XMP namespaces |
| [user-guide.md](user-guide.md) | Minimal fields, AI metadata, accessibility, Digital Source Type, preservation |
| [tooling.md](tooling.md) | ExifTool CLI wrapper documentation |
| [iptc-pmd-techreference_2025.1.json](iptc-pmd-techreference_2025.1.json) | Machine-readable spec (JSON) |
| [iptc-pmd-techreference_2025.1.yml](iptc-pmd-techreference_2025.1.yml) | Machine-readable spec (YAML) |

## Planned Additional Content

- Complete key reference for `kCGImagePropertyIPTCDictionary`
- IPTC Extension properties accessible via CGImageMetadata
- Mapping between IIM datasets and XMP properties
