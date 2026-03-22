# Format-Specific Metadata

Metadata dictionaries tied to specific image file formats. Each has a small set
of format-specific property keys.

## ImageIO dictionaries

| Dictionary | Format | iOS |
|---|---|---|
| `kCGImagePropertyJFIFDictionary` | JPEG (JFIF) | 4.0 |
| `kCGImagePropertyPNGDictionary` | PNG | 4.0 |
| `kCGImagePropertyGIFDictionary` | GIF | 4.0 |
| `kCGImagePropertyDNGDictionary` | DNG (Digital Negative) | 4.0 |
| `kCGImagePropertyRawDictionary` | Generic RAW | 4.0 |
| `kCGImageProperty8BIMDictionary` | Adobe Photoshop (8BIM) | 4.0 |
| `kCGImagePropertyCIFFDictionary` | Canon legacy (CIFF) | 4.0 |
| `kCGImagePropertyOpenEXRDictionary` | OpenEXR (HDR) | 11.3 |
| `kCGImagePropertyHEICSDictionary` | HEIF sequences | 13.0 |
| `kCGImagePropertyTGADictionary` | TGA | 14.0 |
| `kCGImagePropertyWebPDictionary` | WebP | 14.0 |
| `kCGImagePropertyHEIFDictionary` | HEIF | 16.0 |
| `kCGImagePropertyAVISDictionary` | AV1 Image Sequence | 16.0 |

## Planned content

Per-format sections covering:

- All dictionary keys and their types
- What metadata each format can embed (e.g., PNG supports text chunks but not EXIF natively)
- Format-specific behaviors and gotchas
- Which cross-format standards (EXIF, IPTC, XMP) each format supports
