# Manufacturer MakerNote Dictionaries

> Part of [iOS Image Metadata Skill](../../SKILL.md) · [References Index](../README.md)

Vendor-specific capture data embedded in the EXIF MakerNote tag (0x927C).
Each camera manufacturer defines their own proprietary binary format inside
this single EXIF tag. Apple's ImageIO framework parses MakerNote data for
seven vendors and exposes it as flat dictionaries.

---

## Overview

The MakerNote is an opaque binary blob within EXIF whose internal structure
is entirely vendor-defined. It stores data that has no standard EXIF
equivalent: proprietary shooting modes, internal autofocus data, lens
identification, shutter count, image processing parameters, and
computational photography flags.

**Key characteristics:**
- **Not standardized** -- the EXIF spec only reserves the tag; contents are proprietary
- **Offset-fragile** -- many MakerNote formats use absolute byte offsets that break when EXIF is rewritten
- **No XMP representation** -- MakerNote data exists only in the property dictionary system, not in `CGImageMetadata`
- **Partially encrypted** -- Nikon encrypts lens data and color balance using serial number + shutter count
- **Reverse-engineered** -- most specifications come from ExifTool, not from manufacturers
- **Vendor-exclusive** -- only one MakerNote dictionary is populated per image (determined by camera Make)

---

## ImageIO Dictionary Constants

| Dictionary Constant | Vendor | iOS | Format | Offset Strategy | Documentation |
|---------------------|--------|-----|--------|-----------------|---------------|
| `kCGImagePropertyMakerCanonDictionary` | Canon | 4.0+ | Headerless IFD | Absolute (fragile) | Extensive (~5K lines in ExifTool) |
| `kCGImagePropertyMakerNikonDictionary` | Nikon | 4.0+ | Self-contained TIFF (Type 3) | Own header (resilient) | Extensive (~8K lines) |
| `kCGImagePropertyMakerMinoltaDictionary` | Minolta / Sony | 4.0+ | IFD (model-dependent) | Model-dependent (fragile) | Moderate (Sony ~10K lines) |
| `kCGImagePropertyMakerFujiDictionary` | Fujifilm | 4.0+ | Header + IFD, always LE | Relative (most resilient) | Good |
| `kCGImagePropertyMakerOlympusDictionary` | Olympus / OM System | 4.0+ | Header + nested sub-IFDs | Absolute or relative (varies) | Good |
| `kCGImagePropertyMakerPentaxDictionary` | Pentax / Ricoh | 4.0+ | AOC header + IFD | Model-dependent | Good |
| `kCGImagePropertyMakerAppleDictionary` | Apple (iPhone/iPad) | 7.0+ | Header + IFD + bplist values | N/A (always fresh) | Partial (undocumented by Apple) |

---

## File Index

| File | Contents |
|------|----------|
| [makernote-concept.md](makernote-concept.md) | What MakerNote is (EXIF tag 37500), five format variants (headerless IFD, self-contained TIFF, header+IFD, flat binary, Apple hybrid), offset fragility problem with detailed examples, Microsoft OffsetSchema workaround, ImageIO access patterns, metadata preservation strategies, decoder library comparison, vendor signature table, known idiosyncrasies |
| [apple.md](apple.md) | Apple MakerNote: complete tag reference (30+ tags), format details (bplist encoding), RunTime/CMTime structure, AccelerationVector coordinate system, BurstUUID burst grouping, ContentIdentifier Live Photo linking, HDRImageType, ImageCaptureType, HDRHeadroom, CameraType, SemanticStyle/Photographic Styles, computational photography pipeline context, Swift code examples, privacy considerations |
| [canon.md](canon.md) | Canon MakerNote: 50+ top-level tags, CameraSettings array (40+ indexed values with full enum decode tables), ShotInfo array, lens identification (LensModel + LensType + LensInfo), camera identification (CanonModelID with 20+ model values), AFInfo2 modern AF structure with AFAreaMode values, shutter count extraction methods, known firmware bugs, Swift code examples |
| [nikon.md](nikon.md) | Nikon MakerNote: three format types (Type 1/2/3) with byte-level layouts, 60+ tags, LensData encryption (XOR cipher using serial + shutter count), ColorBalance encryption, VRInfo vibration reduction, AFInfo2 structure with AFAreaMode values, PictureControl presets, Active D-Lighting, shutter count (direct tag), NEFCompression values, lens type bitfield, Swift code examples |
| [other-vendors.md](other-vendors.md) | Fujifilm (Film Simulation complete decode table with 16 modes including REALA ACE, dynamic range tags, grain effect, Color Chrome, tone controls, recipe reconstruction guide), Olympus (5 nested sub-IFDs for Equipment/CameraSettings/RawDevelopment/ImageProcessing/FocusInfo, art filter values, IS modes), Minolta/Sony (shared heritage, model-dependent formats, CameraSettings array, Sony-specific sub-structures), Pentax (Shake Reduction, ImageTone presets, lens two-byte ID system, shutter count, sensor temperature, world time) |

---

## Quick Reference: What Each Vendor Stores

| Data | Canon | Nikon | Apple | Fuji | Olympus | Pentax | Minolta/Sony |
|------|-------|-------|-------|------|---------|--------|--------------|
| **Shutter count** | Indirect (CameraInfo) | Tag 0x00a7 | -- | -- | -- | Tag 0x0215 | -- |
| **Lens model** | Tag 0x0095 (string) | Tags 0x0083-0x0084 | -- | Tags 0x1404-0x1407 | Sub-IFD 0x2010 | Tag 0x003f | Varies |
| **Serial number** | Tag 0x000c | Tag 0x001d | -- | Tag 0x0010 | Sub-IFD 0x2010 | -- | -- |
| **Focus mode** | Settings[7] | Tag 0x0007 (string) | Tag 0x0007 (AFStable) | Tag 0x1021 | Sub-IFD 0x2020 | Tag 0x000d | Settings[24] |
| **White balance** | ShotInfo[7] | Tag 0x0005 (string) | -- | Tag 0x1002 | Sub-IFD 0x2020 | Tag 0x0019 | Settings[3] |
| **Image stabilization** | Settings[34] | Tag 0x001f (VRInfo) | Tag 0x000f (OIS) | -- | Sub-IFD 0x2020 | Tag 0x007f (SR) | Tag 0x0018 |
| **Film simulation** | -- | -- | -- | Tag 0x1401 | -- | -- | -- |
| **Art filters** | -- | -- | -- | -- | Sub-IFD 0x2040 | -- | -- |
| **HDR info** | Tag 0x4025 | Tag 0x002c | Tag 0x000a | -- | -- | Tag 0x0069 | -- |
| **Burst/Live Photo** | -- | -- | Tags 0x000b, 0x0011 | -- | -- | -- | -- |
| **Firmware version** | Tag 0x0007 | -- | -- | -- | Tag 0x0104 | -- | -- |
| **Scene classification** | -- | -- | Tag 0x0016 (bplist) | -- | -- | -- | -- |
| **Photographic Styles** | -- | -- | Tag 0x0040 (bplist) | -- | -- | -- | -- |
| **Image tone preset** | Picture Style | Picture Control | -- | Film Simulation | Art Filter | ImageTone | Color Mode |
| **Sensor temperature** | -- | -- | -- | -- | -- | Tag 0x0047 | -- |
| **Encryption** | -- | ColorBalance, LensData | -- | -- | -- | -- | -- |

---

## Common Access Pattern (Swift)

```swift
import ImageIO

let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as! [String: Any]

// Each vendor dictionary has string keys (tag IDs as decimal strings)
let apple  = props[kCGImagePropertyMakerAppleDictionary as String]   as? [String: Any]
let canon  = props[kCGImagePropertyMakerCanonDictionary as String]   as? [String: Any]
let nikon  = props[kCGImagePropertyMakerNikonDictionary as String]   as? [String: Any]
let fuji   = props[kCGImagePropertyMakerFujiDictionary as String]    as? [String: Any]
let olymp  = props[kCGImagePropertyMakerOlympusDictionary as String] as? [String: Any]
let pentax = props[kCGImagePropertyMakerPentaxDictionary as String]  as? [String: Any]
let minolt = props[kCGImagePropertyMakerMinoltaDictionary as String] as? [String: Any]

// Only ONE of these will be non-nil for any given image.
// Keys are decimal string representations of vendor-specific tag IDs:
//   Canon:  "1" (CameraSettings), "6" (ImageType), "149" (LensModel)
//   Nikon:  "7" (FocusMode), "167" (ShutterCount)
//   Apple:  "11" (BurstUUID), "17" (ContentIdentifier)
//   Fuji:   "5121" (FilmMode), "4129" (FocusMode)
//   Pentax: "533" (ShutterCount), "92" (ImageTone)
```

---

## Vendor Format Comparison

| Feature | Canon | Nikon (Type 3) | Apple | Fujifilm | Olympus | Pentax |
|---------|-------|----------------|-------|----------|---------|--------|
| **Header** | None | `"Nikon\0"` + TIFF | `"Apple iOS\0"` + MM | `"FUJIFILM"` | `"OLYMP\0"` / `"OLYMPUS\0"` | `"AOC\0"` + BO |
| **Own byte order** | No | Yes | Yes (always MM) | Yes (always LE) | No | Yes |
| **Offset base** | Main TIFF | Internal TIFF | MakerNote | MakerNote | Main TIFF / MakerNote | Varies |
| **Resilient to rewrite** | No | Yes (if moved intact) | N/A | Yes | Partial | Partial |
| **Nested sub-IFDs** | No | No | No | No | Yes (5 levels) | No |
| **Encrypted fields** | No | Yes (2 fields) | No | No | No | No |
| **Binary plist values** | No | No | Yes (4+ tags) | No | No | No |
| **ExifTool source size** | ~5,000 lines | ~8,000 lines | ~500 lines | ~1,500 lines | ~3,000 lines | ~3,000 lines |

---

## Cross-References

- [EXIF MakerNote overview](../exif/makernote.md) -- MakerNote in the EXIF standard context, offset fragility, GPS stripping caveat
- [ImageIO Property Keys](../imageio/property-keys.md) -- All `kCGImageProperty*` constants including MakerNote dictionaries
- [ImageIO Auxiliary Data](../imageio/auxiliary-data.md) -- Depth maps, segmentation mattes, gain maps (related to Apple computational photography but accessed via separate API)
- [EXIF Pitfalls](../exif/pitfalls.md) -- MakerNote offset corruption, 64 KB APP1 limit

### External References

- [ExifTool Tag Names](https://exiftool.org/TagNames/) -- Comprehensive MakerNote tag documentation for all vendors
- [ExifTool MakerNote Types](https://exiftool.org/makernote_types.html) -- Format signatures for 6,940+ camera models from 106 manufacturers
- [ExifTool Idiosyncrasies](https://exiftool.org/idiosyncracies.html) -- Vendor-specific bugs and edge cases
- [Exiv2 MakerNote Documentation](https://exiv2.org/makernote.html) -- Format specifications and automatic detection
