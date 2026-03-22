# EXIF

EXIF standard (CIPA DC-008, version 3.0). Camera and capture technical metadata.

## ImageIO dictionaries

- `kCGImagePropertyExifDictionary` (iOS 4.0) — ~60 keys
- `kCGImagePropertyExifAuxDictionary` (iOS 4.0) — ~9 keys

## Planned content

- IFD structure (IFD0, ExifIFD, Interop IFD, thumbnail IFD1)
- Data types (BYTE, ASCII, SHORT, LONG, RATIONAL, UNDEFINED, etc.)
- Complete tag reference grouped by category (camera, exposure, timestamp, lens, image quality)
- MakerNote concept (opaque vendor blob — details in `../makers/`)
- Byte order markers (big-endian / little-endian)
- EXIF 3.0 changes: UTF-8 support, Annex H metadata handling guidelines
- Format support: JPEG APP1, TIFF, HEIF, WebP
