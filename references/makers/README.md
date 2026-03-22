# Manufacturer MakerNote Dictionaries

Vendor-specific capture data embedded in the EXIF MakerNote tag. Each camera
manufacturer defines their own proprietary format.

## ImageIO dictionaries

| Dictionary | Vendor | iOS |
|---|---|---|
| `kCGImagePropertyMakerCanonDictionary` | Canon | 4.0 |
| `kCGImagePropertyMakerNikonDictionary` | Nikon | 4.0 |
| `kCGImagePropertyMakerMinoltaDictionary` | Minolta / Sony | 4.0 |
| `kCGImagePropertyMakerFujiDictionary` | Fuji | 4.0 |
| `kCGImagePropertyMakerOlympusDictionary` | Olympus | 4.0 |
| `kCGImagePropertyMakerPentaxDictionary` | Pentax | 4.0 |
| `kCGImagePropertyMakerAppleDictionary` | Apple | 7.0 |

## Planned content

- MakerNote concept: opaque binary blob inside EXIF, vendor-specific structure
- Per-vendor key reference (Canon and Nikon have full Apple docs; others are dictionary-only)
- Apple MakerNote: semantic segmentation, HDR gain map, computational photography data
- Common use cases: shutter count, lens adapter info, shooting mode, internal serial numbers
- Limitations: MakerNote data can break when EXIF is rewritten without preserving byte offsets
