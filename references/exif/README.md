# EXIF — Exchangeable Image File Format

> Part of [iOS Image Metadata Skill](../../SKILL.md) · [References Index](../README.md)

Complete reference for the EXIF metadata standard (CIPA DC-008). The files in
this folder document the EXIF standard itself — binary format, tag definitions,
XMP mappings, and known pitfalls. All Apple ImageIO integration details are
consolidated in a single file ([`imageio-mapping.md`](imageio-mapping.md)).

---

## Overview

**EXIF (Exchangeable Image File Format)** is the dominant standard for storing
technical capture metadata in digital photographs. It records camera settings,
exposure parameters, timestamps, lens information, and image characteristics
directly inside image files.

- **Governing bodies:** CIPA (Camera & Imaging Products Association) and JEITA
  (Japan Electronics and Information Technology Industries Association)
- **Specification:** CIPA DC-008
- **Current version:** 3.1 (January 2026)
- **Detailed baseline in this folder:** 3.0 (May 2023, corrected December 2024),
  with forward-compatibility notes for 3.1 where relevant
- **Based on:** TIFF Rev. 6.0 tag structure
- **Related standards:** DCF (Design rule for Camera File system), TIFF/EP

### What EXIF Records

- Camera make/model and firmware
- Exposure settings (shutter speed, aperture, ISO, metering mode)
- Date and time of capture (with optional timezone since v2.31)
- Lens information (focal length, make, model, serial number)
- Flash status and energy
- Color space and white balance
- Image dimensions and orientation
- Scene and subject information
- Composite image metadata (since v2.32)
- Subsecond timing precision
- Environmental conditions (temperature, humidity, pressure — v2.31+)

### What EXIF Does Not Record

- GPS is not in the Exif SubIFD itself (it is stored in the separate GPS IFD in
  the EXIF container — see `../gps/`)
- Editorial metadata like titles, keywords, credits (IPTC/XMP — see `../iptc/`, `../xmp/`)
- Color profile data (ICC — see `../icc/`)

---

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| 1.0 | October 1995 | Initial release by JEIDA. Basic tag definitions |
| 1.1 | May 1997 | Added tags and operating specifications |
| 2.0 | November 1997 | Added sRGB color space, GPS IFD, compressed thumbnails |
| 2.1 | December 1998 | Added DCF interoperability tags |
| 2.2 | April 2002 | Applied ExifPrint for optimal printing |
| 2.21 | September 2003 | Added Adobe RGB color space support; corrections |
| 2.3 | April 2010 | Added revised ISO tags, `LensSpecification`/`LensMake`/`LensModel`/`LensSerialNumber` |
| **2.31** | **July 2016** | **Added `OffsetTime*` timezone tags**, environmental tags (Temperature, Humidity, Pressure, WaterDepth, Acceleration, CameraElevationAngle) |
| **2.32** | **May 2019** | **Added `CompositeImage` tags** for computational photography / Night Mode |
| **3.0** | **May 2023** | **Added UTF-8 data type** (type ID 129). New identity tags (ImageTitle, Photographer, etc.). Annex H metadata handling guidelines. Corrected December 2024 |
| **3.1** | **January 2026** | Latest CIPA revision (DC-008-2026); this repo tracks compatibility across versions |

---

## File Index

### EXIF Standard

| File | Content |
|------|---------|
| [`technical-structure.md`](technical-structure.md) | Binary format: APP1 layout, TIFF header, IFD entry format, data types, byte order, complete tag tables for every IFD (IFD0, Exif SubIFD, GPS, Interoperability, IFD1), format embedding, MPF |
| [`tag-reference.md`](tag-reference.md) | Tag semantics by category: all enum values decoded, Flash bitfield, DateTime triplet relationships, Composite Image, Environmental tags, EXIF 3.0, UserComment charset |
| [`xmp-mapping.md`](xmp-mapping.md) | Standard EXIF↔XMP mapping: `exif:`, `exifEX:`, `aux:`, `tiff:` namespaces, complete tag→XMP path tables, binary vs XMP format differences |
| [`orientation.md`](orientation.md) | Orientation values 1–8, row/column semantics, display transforms, visual reference, common camera values |
| [`makernote.md`](makernote.md) | MakerNote characteristics, offset fragility, vendor formats (Canon, Nikon, Apple, Sony, etc.), GPS stripping caveat, decoder libraries |
| [`pitfalls.md`](pitfalls.md) | Standard-level pitfalls: timezone ambiguity, MakerNote fragility, 64 KB limit, orientation inconsistency, ColorSpace ambiguity, privacy risks |

### ImageIO Integration

| File | Content |
|------|---------|
| [`imageio-mapping.md`](imageio-mapping.md) | All Apple ImageIO details in one place: property dictionary keys (`kCGImagePropertyExif*`), EXIF Auxiliary dictionary, ExifAux↔EXIF 2.3 overlap, orientation constants, UIImage warning, XMP namespace constants, bridge functions, auto-synthesis, Swift code examples, ImageIO-specific pitfalls |

---

## Cross-References

- **GPS IFD** (location metadata): `../gps/`
- **TIFF IFD** (Make, Model, Orientation, DateTime, Artist, Copyright): `../tiff/`
- **XMP standard** (namespaces, value types, embedding): `../xmp/`
- **ImageIO framework** (APIs, formats, all property keys): `../imageio/`
- **MakerNote vendors** (Apple, Canon, Nikon key details): `../makers/`
- **Interoperability** (EXIF/IPTC/XMP sync rules): `../interoperability/`
- **ICC color profiles** (ColorSpace tag relationship): `../icc/`
