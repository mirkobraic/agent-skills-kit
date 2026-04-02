# TIFF IFD Reference

> Part of [iOS Image Metadata Skill](../../SKILL.md) · [References Index](../README.md)

TIFF (Tagged Image File Format) metadata as exposed by Apple's ImageIO
framework through `kCGImagePropertyTIFFDictionary`. TIFF is both a standalone
image format and the **structural foundation** for EXIF metadata in JPEG, DNG,
HEIF, and most RAW formats.

---

## What TIFF Tags Cover

The 20 keys in `kCGImagePropertyTIFFDictionary` describe:

- **Device info** -- Make, Model, Software, HostComputer
- **Image description** -- ImageDescription, DocumentName
- **Orientation and resolution** -- Orientation, XResolution, YResolution, ResolutionUnit
- **Authorship** -- Artist, Copyright
- **Timestamps** -- DateTime
- **Color characterization** -- WhitePoint, PrimaryChromaticities, TransferFunction
- **Encoding** -- Compression, PhotometricInterpretation
- **Tiling** -- TileWidth, TileLength

These are **not** camera capture settings -- exposure, ISO, focal length, lens
info, and similar tags live in the Exif SubIFD (see
[`../exif/`](../exif/README.md)). TIFF IFD0 tags describe the image file
itself and the device that created it.

---

## Why TIFF Matters Beyond TIFF Files

Every JPEG with EXIF data contains a TIFF structure inside its APP1 segment.
DNG files are TIFF files. HEIF embeds EXIF using the same IFD binary format.
Understanding TIFF is understanding how image metadata is physically stored
across all major formats.

The TIFF 6.0 specification (Adobe, June 1992) defines 36 baseline tags,
60 extension tags, and supports private tags for vendor-specific data. Of
these, ImageIO exposes the 20 most commonly used descriptive tags through the
TIFF dictionary, plus a handful of structural tags through top-level keys
(`kCGImagePropertyPixelWidth`, `kCGImagePropertyDepth`, etc.).

---

## File Index

| File | Description |
|------|-------------|
| [`tag-reference.md`](tag-reference.md) | Complete reference for all 20 TIFF tags exposed by ImageIO: tag ID, data type, ImageIO key, enum values, typical values, and usage notes. Plus tags NOT in the dictionary but exposed elsewhere |
| [`tiff-as-container.md`](tiff-as-container.md) | TIFF file structure: header, IFDs, byte order, sub-IFD pointers (ExifIFD, GPS, Interop), IFD1 thumbnail, multi-page TIFF, how ImageIO separates TIFF/EXIF/GPS, BigTIFF, offset model |
| [`imageio-mapping.md`](imageio-mapping.md) | All `kCGImagePropertyTIFF*` constants, Swift read/write examples, lossless update, orientation duplication, DateTime relationships, CGImagePropertyOrientation vs UIImage.Orientation, XMP `tiff:` namespace mapping with bridge functions |
| [`pitfalls.md`](pitfalls.md) | 8 known pitfalls: orientation duplication, DateTime timezone, Make/Model ASCII encoding, Artist/Copyright/Description triplication across TIFF/IPTC/XMP with MWG reconciliation, resolution units, BigTIFF, HostComputer duplication, UTF-8 in ASCII fields |

---

## ImageIO Dictionary

- **Dictionary key:** `kCGImagePropertyTIFFDictionary`
- **Available since:** iOS 4.0, macOS 10.4
- **Key count:** 20 constants
- **Format support:** JPEG (via EXIF), TIFF, DNG, HEIF/HEIC, all RAW formats
- **XMP namespace:** `tiff:` (`http://ns.adobe.com/tiff/1.0/`)

---

## Key Relationships

### TIFF <> EXIF

TIFF IFD0 is the parent container. It holds descriptive tags (Make, Model,
DateTime) and pointers to the Exif SubIFD (tag 34665) and GPS IFD (tag
34853). ImageIO splits these into separate dictionaries:

- `kCGImagePropertyTIFFDictionary` -- IFD0 tags
- `kCGImagePropertyExifDictionary` -- Exif SubIFD tags
- `kCGImagePropertyGPSDictionary` -- GPS IFD tags

The split means that in the raw binary format these all live in one IFD-based
structure, but ImageIO presents them as if they were independent dictionaries.
See [`tiff-as-container.md`](tiff-as-container.md#how-imageio-separates-tiff-tags)
for the full diagram.

### TIFF <> IPTC <> XMP (Triple-Stored Fields)

Three tags are stored in all three standards (the "triple-stored" fields):

| Concept | TIFF Tag | IPTC Field | XMP Property |
|---------|----------|------------|-------------|
| Creator | Artist | By-line | `dc:creator` |
| Rights | Copyright | CopyrightNotice | `dc:rights` |
| Description | ImageDescription | Caption-Abstract | `dc:description` |

The MWG (Metadata Working Group) recommends reading precedence:
**XMP first, then IPTC, then TIFF/EXIF.** When writing, update all three
to keep them in sync. See [`pitfalls.md`](pitfalls.md) for details.

### TIFF <> XMP tiff: Namespace

All TIFF IFD0 tags map to the `tiff:` XMP namespace
(`http://ns.adobe.com/tiff/1.0/`). ImageIO's bridge functions
(`CGImageMetadataCopyTagMatchingImageProperty` /
`CGImageMetadataSetValueMatchingImageProperty`) handle the conversion
automatically. The namespace includes structural tags (ImageWidth,
ImageLength, BitsPerSample, SamplesPerPixel) that are not in
`kCGImagePropertyTIFFDictionary` but do exist in XMP.

See [`imageio-mapping.md`](imageio-mapping.md#xmp-mapping-for-tiff-tags).

---

## Specification History

| Date | Event |
|------|-------|
| 1986 | TIFF 1.0 -- Aldus Corporation (with Microsoft) |
| 1988 | TIFF 5.0 -- added palette color, LZW |
| 1992 | TIFF 6.0 -- final Aldus revision; added tiling, CMYK, YCbCr, JPEG-in-TIFF |
| 1994 | Adobe acquires Aldus and TIFF specification |
| 2001 | TIFF/EP (ISO 12234-2) -- electronic photography extension |
| 1998 | TIFF/IT (ISO 12639) -- image technology for prepress (revised 2004) |
| 2007 | BigTIFF proposal -- 64-bit offsets for >4 GB files |

No new revision of the core TIFF specification has been released since 6.0.
Extensions are handled through private tags and supplementary specifications
(EXIF, DNG, GeoTIFF, OME-TIFF, etc.).

---

## Cross-References

- [`../exif/technical-structure.md`](../exif/technical-structure.md) -- Full
  IFD binary format, data types, all IFD0/Exif SubIFD/GPS/IFD1 tag tables
- [`../interoperability/orientation-mapping.md`](../interoperability/orientation-mapping.md) -- Orientation values 1-8,
  visual diagrams, EXIF↔ImageIO↔UIImage mapping
- [`../exif/pitfalls.md`](../exif/pitfalls.md) -- EXIF-specific pitfalls
  including DateTime timezone and MakerNote fragility
- [`../imageio/property-keys.md`](../imageio/property-keys.md) -- Complete
  `kCGImageProperty*` constant catalog for all dictionaries
- [`../imageio/pitfalls.md`](../imageio/pitfalls.md) -- UIImage metadata loss,
  orientation confusion across Apple APIs
- [`../iptc/README.md`](../iptc/README.md) -- IPTC Photo Metadata (IIM + Core + Extension)
