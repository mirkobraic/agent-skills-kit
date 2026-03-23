# XMP — Extensible Metadata Platform

> Part of [iOS Image Metadata Skill](../../SKILL.md) · [References Index](../README.md)

Complete reference for the XMP metadata standard (ISO 16684-1). The files in
this folder document the XMP standard itself — data model, namespaces,
embedding in file formats, and known pitfalls. All Apple ImageIO integration
details are consolidated in a single file
([`imageio-integration.md`](imageio-integration.md)).

---

## Overview

**XMP (Extensible Metadata Platform)** is an ISO-standardized, XML-based
metadata framework originally created by Adobe Systems. It uses a subset of
W3C RDF (Resource Description Framework) serialized as XML to represent
metadata as named properties organized into namespaces. Unlike binary metadata
standards (EXIF, IPTC IIM), XMP is text-based, extensible, and format-agnostic
— the same XMP data model can be embedded in JPEG, TIFF, PNG, HEIF, PDF, DNG,
WebP, AVIF, and many other formats.

- **Creator:** Adobe Systems (April 2001)
- **ISO standard:** ISO 16684-1 (Part 1: Data model, serialization, and core
  properties)
- **Current edition:** ISO 16684-1:2019 (confirmed 2024)
- **Based on:** W3C RDF/XML (subset)
- **Internal codename:** Originally called XAP (Extensible Authoring and
  Publishing) before the public XMP name
- **Reference implementation:** Adobe XMP Toolkit SDK (C++ / Java, BSD license,
  open source since 2007)

### What XMP Provides

- **Namespace-based extensibility** — any organization can define custom
  namespaces with custom properties; no central registry required
- **Structured values** — supports simple scalars, ordered/unordered arrays,
  language alternatives, and nested structures
- **Cross-format portability** — a single metadata schema works identically
  across JPEG, TIFF, PNG, HEIF, PDF, WebP, AVIF, and more
- **Modern IPTC path** — IPTC Core and Extension schemas are defined as XMP
  namespaces (`Iptc4xmpCore`, `Iptc4xmpExt`), making XMP the required path
  for IPTC metadata in modern formats (HEIF, WebP, AVIF, PNG)
- **Universal support** — XMP is the only metadata standard embedded in every
  image format that ImageIO supports (except GIF)

### What XMP Does Not Provide

- Binary efficiency — XMP is XML text, significantly larger than equivalent
  EXIF binary data
- DRM or access control — `xmpRights:` properties express rights information
  but do not enforce them
- Pixel-level data — XMP describes metadata about resources, not the resources
  themselves

---

## Version History

| Date | Event |
|------|-------|
| April 2001 | Adobe introduces XMP with Acrobat 5.0 (originally codenamed XAP) |
| September 2001 | XMP Specification 1.0 published |
| June 2004 | Adobe and IPTC announce collaboration on IPTC Core for XMP |
| March 2005 | IPTC Core Schema for XMP 1.0 released |
| 2005 | XMP Specification updated; three-part structure introduced (Part 1: Data Model, Part 2: Schemas, Part 3: Storage in Files) |
| May 2007 | Adobe releases XMP Toolkit SDK under BSD open-source license |
| February 2012 | ISO 16684-1:2012 published — XMP becomes an ISO standard |
| 2014 | ISO 16684-2:2014 — Description of XMP schemas using RELAX NG |
| 2019 | ISO 16684-1:2019 — Revised Part 1 (current edition, confirmed 2024) |
| January 2020 | Adobe XMP Specification Parts 1-3 updated (current Adobe docs) |
| 2021 | ISO 16684-3:2021 — Part 3: Storage of XMP in JSON-LD |
| January 2024 | ISO 16684-4:2024 — Part 4: Use of XMP for semantic units |

### ISO 16684 Series

| Part | Title | Edition |
|------|-------|---------|
| Part 1 | Data model, serialization, and core properties | ISO 16684-1:2019 |
| Part 2 | Description of XMP schemas using RELAX NG | ISO 16684-2:2014 |
| Part 3 | Storage of XMP in JSON-LD | ISO 16684-3:2021 |
| Part 4 | Use of XMP for semantic units | ISO 16684-4:2024 |

### Adobe XMP Specification Parts

| Part | Content | Last Updated |
|------|---------|--------------|
| Part 1 | Data Model, Serialization, and Core Properties | January 2020 |
| Part 2 | Standard Schemas (namespace definitions and property catalogs) | February 2022 |
| Part 3 | Storage in Files (embedding rules for JPEG, TIFF, PNG, PDF, etc.) | January 2020 |

---

## File Index

### XMP Standard

| File | Content |
|------|---------|
| [`data-model.md`](data-model.md) | RDF/XML serialization, XMP packet structure (header, body, padding, trailer), property forms (simple, struct, array), qualifiers, value types, `CGImageMetadataType` mapping, complete serialization examples |
| [`namespaces.md`](namespaces.md) | Complete namespace catalog: URI, prefix, purpose, key properties for all standard namespaces (dc, xmp, xmpRights, xmpMM, xmpBJ, photoshop, tiff, exif, exifEX, crs, Iptc4xmpCore, Iptc4xmpExt, plus), structure types (stRef, stEvt, stDim, stArea), ImageIO pre-registered constants, custom namespace registration |
| [`embedding.md`](embedding.md) | Per-format embedding: JPEG (APP1 marker, extended XMP), TIFF (tag 700), PNG (iTXt chunk), HEIF/HEIC (ISOBMFF metadata item), DNG, PDF (metadata stream), WebP (XMP RIFF chunk), AVIF. Packet wrapper format, padding, sidecar .xmp files, packet scanning |
| [`pitfalls.md`](pitfalls.md) | Known issues: JPEG 64 KB limit, namespace prefix conflicts, langAlt handling, metadata loss, EXIF/IPTC/XMP sync, sidecar priority, UTF-8 encoding, whitespace/formatting differences, date format inconsistencies |

### ImageIO Integration

| File | Content |
|------|---------|
| [`imageio-integration.md`](imageio-integration.md) | All Apple ImageIO XMP details: `CGImageMetadata` / `CGMutableImageMetadata`, `CGImageMetadataTag`, `CGImageMetadataType` enum, all 10 namespace constants, reading/writing XMP, bridge functions, auto-synthesis, custom namespace registration, langAlt workarounds, format-specific behavior, Swift code examples |

---

## Cross-References

- **ImageIO framework** (XMP tree API, CGImageMetadata): `../imageio/cgimage-metadata.md`
- **EXIF standard** (EXIF tags mapped to XMP `exif:` / `exifEX:` / `tiff:`): `../exif/xmp-mapping.md`
- **IPTC standard** (IIM legacy + XMP Core/Extension schemas): `../iptc/`
- **TIFF IFD** (IFD0 tags mapped to XMP `tiff:` namespace): `../tiff/`
- **GPS IFD** (GPS tags mapped to XMP `exif:` namespace): `../gps/`
- **Interoperability** (MWG sync rules, cross-standard mapping): `../interoperability/`
- **ICC color profiles** (color management context): `../icc/`
- **Format-specific details** (embedding per container format): `../formats/`
