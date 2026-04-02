# Overlapping Fields — Cross-Standard Metadata Mapping

> Part of [Interoperability Reference](README.md)

This document maps every image metadata field that exists in multiple standards
simultaneously. When the same conceptual field lives in EXIF/TIFF, IPTC IIM,
and XMP, applications must decide which to read, which to write, and how to
keep them synchronized. The [MWG Guidelines](mwg-guidelines.md) define the
reconciliation rules; this file documents *where* each field lives.

---

## How to Read This Document

Each "family" section describes one conceptual metadata field and its locations
across all three standards. The tables include:

- **Standard:** EXIF/TIFF, IPTC IIM, or XMP
- **Location:** Tag name and ID (EXIF/TIFF), dataset number (IPTC IIM), or
  XMP path
- **ImageIO Key / XMP Path:** The constant or path used in Apple's ImageIO
  framework
- **Type:** Data type in that standard

Fields are grouped by semantic meaning, not by standard. The
[Complete Cross-Reference Table](#complete-cross-reference-table) at the end
provides a flat view for quick lookup.

---

## DateTime Family (Most Complex Overlap)

DateTime is the most problematic overlapping field because it exists in 6+
locations with three different format conventions, different precision levels,
and different timezone handling.

### Format Conventions

| Standard | Format | Example | Timezone | Fractional Seconds |
|----------|--------|---------|----------|--------------------|
| EXIF | `YYYY:MM:DD HH:MM:SS` | `2024:06:15 14:30:00` | None (naive) | None |
| EXIF 2.31+ | OffsetTime* tags | `+05:30` | Separate tag | SubSecTime* tag |
| IPTC IIM Date | `YYYYMMDD` | `20240615` | None | None |
| IPTC IIM Time | `HHMMSS±HHMM` | `143000+0530` | In field | None |
| XMP | ISO 8601 `YYYY-MM-DDTHH:MM:SS.sss±HH:MM` | `2024-06-15T14:30:00.123+05:30` | Inline | Inline |

> **Key insight:** Only XMP can represent a complete timestamp (date + time +
> fractional seconds + timezone) in a single field. EXIF requires up to three
> separate tags. IPTC IIM requires two separate datasets and cannot express
> fractional seconds at all.

### Original Date/Time (When the Photo Was Taken)

This is the most important datetime field. It records when the shutter was
pressed (or the equivalent moment for computational photography).

| Standard | Location | ImageIO Key / XMP Path | Notes |
|----------|----------|----------------------|-------|
| EXIF | ExifIFD tag 0x9003 DateTimeOriginal | `kCGImagePropertyExifDateTimeOriginal` | Naive datetime (no TZ) |
| EXIF | ExifIFD tag 0x9291 SubSecTimeOriginal | `kCGImagePropertyExifSubsecTimeOriginal` | Fractional seconds (e.g., `"123"`) |
| EXIF 2.31+ | ExifIFD tag 0x9011 OffsetTimeOriginal | `kCGImagePropertyExifOffsetTimeOriginal` | UTC offset (e.g., `"+05:30"`) |
| IPTC IIM | Dataset 2:55 DateCreated | `kCGImagePropertyIPTCDateCreated` | Date only: `YYYYMMDD` |
| IPTC IIM | Dataset 2:60 TimeCreated | `kCGImagePropertyIPTCTimeCreated` | Time + TZ: `HHMMSS±HHMM` |
| XMP | `photoshop:DateCreated` | `photoshop:DateCreated` | MWG-preferred source. ISO 8601 complete |
| XMP | `exif:DateTimeOriginal` | `exif:DateTimeOriginal` | XMP mirror of EXIF binary tag |

> **MWG reconciliation group:** These fields should all represent the same
> instant. When writing, update all locations. XMP `photoshop:DateCreated` is
> the MWG-preferred read source for "date created." `exif:DateTimeOriginal` is
> the XMP mirror of the EXIF binary tag. See [mwg-guidelines.md](mwg-guidelines.md).

> **iPhone behavior:** All iPhones write `OffsetTimeOriginal` (EXIF 2.31+),
> providing timezone information. Many third-party cameras only write
> `DateTimeOriginal` without the offset, making the timestamp ambiguous.

### Digitized Date/Time (When the Image Was Digitized)

For film scans, this differs from "Date taken" (the original exposure).
For digital cameras, it usually equals DateTimeOriginal.

| Standard | Location | ImageIO Key / XMP Path | Notes |
|----------|----------|----------------------|-------|
| EXIF | ExifIFD tag 0x9004 DateTimeDigitized | `kCGImagePropertyExifDateTimeDigitized` | Naive datetime |
| EXIF | ExifIFD tag 0x9292 SubSecTimeDigitized | `kCGImagePropertyExifSubsecTimeDigitized` | Fractional seconds |
| EXIF 2.31+ | ExifIFD tag 0x9012 OffsetTimeDigitized | `kCGImagePropertyExifOffsetTimeDigitized` | UTC offset |
| IPTC IIM | Dataset 2:62 DigitalCreationDate | `kCGImagePropertyIPTCDigitalCreationDate` | Date only |
| IPTC IIM | Dataset 2:63 DigitalCreationTime | `kCGImagePropertyIPTCDigitalCreationTime` | Time + TZ |
| XMP | `xmp:CreateDate` | `xmp:CreateDate` | ISO 8601 complete |
| XMP | `exif:DateTimeDigitized` | `exif:DateTimeDigitized` | XMP mirror of EXIF binary |

### Modification Date/Time (Last Modified)

When the file was last saved or processed. Updated by editing software.

| Standard | Location | ImageIO Key / XMP Path | Notes |
|----------|----------|----------------------|-------|
| TIFF | IFD0 tag 0x0132 DateTime | `kCGImagePropertyTIFFDateTime` | Naive datetime |
| EXIF | ExifIFD tag 0x9290 SubSecTime | `kCGImagePropertyExifSubsecTime` | Fractional seconds for IFD0 DateTime |
| EXIF 2.31+ | ExifIFD tag 0x9010 OffsetTime | `kCGImagePropertyExifOffsetTime` | UTC offset for IFD0 DateTime |
| XMP | `xmp:ModifyDate` | `xmp:ModifyDate` | ISO 8601 complete |
| XMP | `tiff:DateTime` | `tiff:DateTime` | XMP mirror of TIFF binary tag |

> **Note:** IPTC IIM has no modification date field. Only TIFF/EXIF and XMP
> carry this timestamp.

### Metadata Date (When Metadata Was Last Modified)

| Standard | Location | XMP Path | Notes |
|----------|----------|----------|-------|
| XMP | XMP-only | `xmp:MetadataDate` | Updated when any metadata changes, even without pixel changes |

This is an XMP-only field with no EXIF or IPTC IIM equivalent.

---

## Creator / Artist Family

| Standard | Location | ImageIO Key / XMP Path | Type |
|----------|----------|----------------------|------|
| TIFF | IFD0 tag 0x013B Artist | `kCGImagePropertyTIFFArtist` | ASCII string (semicolon-separated for multiple) |
| IPTC IIM | Dataset 2:80 By-line | `kCGImagePropertyIPTCByline` | String (max 32 chars per value), repeatable |
| IPTC IIM | Dataset 2:85 By-lineTitle | `kCGImagePropertyIPTCBylineTitle` | String (max 32 chars), repeatable. Title/role of creator |
| XMP | `dc:creator` | `dc:creator` | `rdf:Seq` (ordered list) |

**Multi-value handling — the single most common conversion bug:**

- **EXIF Artist** is a single ASCII string. The MWG recommends semicolon-space
  (`; `) separation for multiple creators: `"Jane Doe; John Smith"`.
- **IPTC IIM By-line** is a repeatable dataset (multiple 2:80 records). Each
  value is limited to 32 bytes (not characters).
- **XMP `dc:creator`** is an ordered sequence (`rdf:Seq`). The first entry is
  the primary creator.

**Quoting rules (MWG spec):** If a creator name contains a semicolon, the
entire name should be enclosed in double quotes in the EXIF Artist string.
A literal double quote within a name is escaped by doubling it:

```
Single:    "Jane Doe"
Multiple:  "Jane Doe; John Smith"
With semi: "\"Doe; Jane\"; John Smith"
With quote: "\"She said \"\"hello\"\"\"; John Smith"
```

**MWG reconciliation:** XMP `dc:creator` is the preferred read source.
ExifTool converts between the semicolon-separated string and the XMP sequence
automatically when the MWG module is loaded.

**By-lineTitle:** `By-lineTitle` (2:85) maps to `photoshop:AuthorsPosition`
in XMP. It is the creator's job title/role, not a separate name. It has no
EXIF equivalent.

---

## Copyright Family

| Standard | Location | ImageIO Key / XMP Path | Type |
|----------|----------|----------------------|------|
| TIFF | IFD0 tag 0x8298 Copyright | `kCGImagePropertyTIFFCopyright` | ASCII string |
| IPTC IIM | Dataset 2:116 CopyrightNotice | `kCGImagePropertyIPTCCopyrightNotice` | String (max 128 chars) |
| XMP | `dc:rights` | `dc:rights` | `rdf:Alt` (language alternatives — `langAlt`) |
| XMP | `xmpRights:UsageTerms` | `xmpRights:UsageTerms` | `rdf:Alt` (language alternatives) |
| XMP | `xmpRights:WebStatement` | `xmpRights:WebStatement` | Text (URL to license) |
| XMP | `xmpRights:Marked` | `xmpRights:Marked` | Boolean (true = copyrighted, false = public domain) |
| XMP | `xmpRights:Owner` | `xmpRights:Owner` | `rdf:Bag` of strings |
| XMP | `plus:CopyrightOwner` | `plus:CopyrightOwner` | Structured (PLUS licensing framework) |

**Notes:**

- `dc:rights` is `langAlt` type — it can hold copyright notices in multiple
  languages. Most apps read only the `x-default` variant.
- `xmpRights:UsageTerms`, `xmpRights:WebStatement`, `xmpRights:Marked`, and
  `xmpRights:Owner` are XMP-only fields with no EXIF or IPTC IIM equivalent.
- TIFF Copyright can contain both photographer and editor copyright separated
  by a NULL byte (`\0`). The portion before the NULL is the photographer's
  copyright; the portion after is the editor's. Rarely used in practice.
- The PLUS licensing framework (`plus:CopyrightOwner`, `plus:Licensor`, etc.)
  provides structured rights information but requires manual namespace
  registration in ImageIO.

**MWG reconciliation:** XMP `dc:rights` is the preferred read source.

---

## Description / Caption Family

| Standard | Location | ImageIO Key / XMP Path | Type |
|----------|----------|----------------------|------|
| TIFF | IFD0 tag 0x010E ImageDescription | `kCGImagePropertyTIFFImageDescription` | ASCII string |
| IPTC IIM | Dataset 2:120 Caption-Abstract | `kCGImagePropertyIPTCCaptionAbstract` | String (max 2000 chars) |
| XMP | `dc:description` | `dc:description` | `rdf:Alt` (language alternatives — `langAlt`) |
| XMP | `tiff:ImageDescription` | `tiff:ImageDescription` | `rdf:Alt` (XMP mirror of TIFF binary) |
| EXIF | ExifIFD tag 0x9286 UserComment | `kCGImagePropertyExifUserComment` | Encoded text (8-byte charset prefix + bytes) |

**Important distinctions:**

- `ImageDescription` (TIFF/EXIF IFD0), `Caption-Abstract` (IPTC IIM), and
  `dc:description` (XMP) are considered equivalent by MWG. They should contain
  the same text.
- `tiff:ImageDescription` is the XMP namespace mirror of the TIFF binary tag.
  It should be kept in sync with `dc:description`.
- `UserComment` (EXIF tag 0x9286) is semantically different — it is a user
  note or annotation, not a formal description. It uses a special 8-byte
  charset identifier prefix (ASCII, JIS, Unicode, or undefined). **UserComment
  is NOT part of MWG reconciliation.**
- `dc:description` is `langAlt` type. Most tools read only the `x-default`
  language variant.
- IPTC Caption-Abstract has a 2000-character limit. Longer descriptions will
  be truncated when writing to IPTC IIM.

**MWG reconciliation:** XMP `dc:description` is the preferred read source.

---

## Keywords / Subject Family

| Standard | Location | ImageIO Key / XMP Path | Type |
|----------|----------|----------------------|------|
| IPTC IIM | Dataset 2:25 Keywords | `kCGImagePropertyIPTCKeywords` | String (max 64 chars per keyword), repeatable |
| XMP | `dc:subject` | `dc:subject` | `rdf:Bag` (unordered set) |

**Notes:**

- **No EXIF equivalent exists.** Keywords are an IPTC/XMP concept.
- IPTC IIM stores keywords as multiple repeating 2:25 datasets. Each dataset
  contains exactly one keyword.
- XMP stores keywords as an `rdf:Bag` (unordered set) of strings.
- MWG recommends treating them as equivalent sets.
- **Common legacy bug:** Some older tools write multiple keywords as a single
  semicolon-separated string within one IPTC 2:25 dataset (e.g.,
  `"sunset; ocean; beach"`). This is incorrect per the IIM specification. Each
  keyword should be a separate dataset. When encountering this, the entire
  string becomes one keyword (including semicolons).
- Hierarchical keywords (e.g., `"Nature|Landscape|Mountain"`) are stored in
  `lr:hierarchicalSubject` (Lightroom) or `Iptc4xmpCore:SubjectCode`. The
  pipe-separated convention is tool-specific, not standardized.

**MWG reconciliation:** XMP `dc:subject` is the preferred read source.

---

## Title / Object Name Family

| Standard | Location | ImageIO Key / XMP Path | Type |
|----------|----------|----------------------|------|
| IPTC IIM | Dataset 2:5 ObjectName | `kCGImagePropertyIPTCObjectName` | String (max 64 chars) |
| XMP | `dc:title` | `dc:title` | `rdf:Alt` (language alternatives — `langAlt`) |

**Notes:**

- **No EXIF/TIFF equivalent tag exists.** EXIF has `ImageDescription` but
  that maps to description/caption, not title.
- `dc:title` is `langAlt` type. Most tools read `x-default`.
- Some applications use IPTC Headline (2:105) as a title substitute, but
  Headline is semantically distinct — it is a brief publishable synopsis, not
  a title. Conflating these causes interoperability problems.
- IPTC ObjectName is limited to 64 characters. Longer titles will be
  truncated when writing to IIM.

---

## Headline Family

| Standard | Location | ImageIO Key / XMP Path | Type |
|----------|----------|----------------------|------|
| IPTC IIM | Dataset 2:105 Headline | `kCGImagePropertyIPTCHeadline` | String (max 256 chars) |
| XMP | `photoshop:Headline` | `photoshop:Headline` | Text |

**Notes:**

- No EXIF/TIFF equivalent.
- Headline is a brief publishable synopsis — like a newspaper headline. It is
  distinct from Title (ObjectName) and Description (Caption-Abstract).
- Maximum 256 characters in IPTC IIM.

---

## Location Fields

Location metadata exists in three different systems with different
granularity and semantics.

### GPS Location (Where the Camera Was)

Physical coordinates recorded by the camera's GPS receiver.

| Standard | Location | ImageIO Key / XMP Path | Notes |
|----------|----------|----------------------|-------|
| EXIF GPS | GPSLatitude (3 RATIONALs: deg/min/sec) | `kCGImagePropertyGPSLatitude` | Absolute value (always positive) |
| EXIF GPS | GPSLatitudeRef | `kCGImagePropertyGPSLatitudeRef` | `"N"` or `"S"` |
| EXIF GPS | GPSLongitude (3 RATIONALs: deg/min/sec) | `kCGImagePropertyGPSLongitude` | Absolute value (always positive) |
| EXIF GPS | GPSLongitudeRef | `kCGImagePropertyGPSLongitudeRef` | `"E"` or `"W"` |
| EXIF GPS | GPSAltitude (RATIONAL) | `kCGImagePropertyGPSAltitude` | Meters |
| EXIF GPS | GPSAltitudeRef (BYTE) | `kCGImagePropertyGPSAltitudeRef` | 0 = above sea level, 1 = below |
| EXIF GPS | GPSTimeStamp (3 RATIONALs) | `kCGImagePropertyGPSTimeStamp` | UTC time of GPS fix |
| EXIF GPS | GPSDateStamp | `kCGImagePropertyGPSDateStamp` | `"YYYY:MM:DD"` UTC date of GPS fix |
| XMP | `exif:GPSLatitude` | `exif:GPSLatitude` | DMS encoded: `"DDD,MM,SS.SSK"` or `"DDD,MM.MMK"` |
| XMP | `exif:GPSLongitude` | `exif:GPSLongitude` | DMS encoded: `"DDD,MM,SS.SSK"` or `"DDD,MM.MMK"` |
| XMP | `exif:GPSAltitude` | `exif:GPSAltitude` | Rational string (e.g., `"100/1"`) |
| XMP | `exif:GPSAltitudeRef` | `exif:GPSAltitudeRef` | `"0"` or `"1"` |

### Editorial Location (What Place is Depicted)

Human-assigned location describing the depicted scene. May differ from GPS
coordinates (e.g., a photo of the Eiffel Tower taken from across the river).

| Standard | Location | ImageIO Key / XMP Path | Max Length (IIM) |
|----------|----------|----------------------|------------------|
| IPTC IIM | Dataset 2:90 City | `kCGImagePropertyIPTCCity` | 32 chars |
| IPTC IIM | Dataset 2:92 Sub-location | `kCGImagePropertyIPTCSubLocation` | 32 chars |
| IPTC IIM | Dataset 2:95 Province/State | `kCGImagePropertyIPTCProvinceState` | 32 chars |
| IPTC IIM | Dataset 2:101 Country | `kCGImagePropertyIPTCCountryPrimaryLocationName` | 64 chars |
| IPTC IIM | Dataset 2:100 CountryCode | `kCGImagePropertyIPTCCountryPrimaryLocationCode` | 3 chars (ISO 3166) |
| XMP | `photoshop:City` | `photoshop:City` | — |
| XMP | `Iptc4xmpCore:Location` | `Iptc4xmpCore:Location` | — |
| XMP | `photoshop:State` | `photoshop:State` | — |
| XMP | `photoshop:Country` | `photoshop:Country` | — |
| XMP | `Iptc4xmpCore:CountryCode` | `Iptc4xmpCore:CountryCode` | — |

### IPTC Extension Location (Structured, XMP-Only)

| XMP Path | Purpose |
|----------|---------|
| `Iptc4xmpExt:LocationShown` | Array of structured locations shown in the image |
| `Iptc4xmpExt:LocationCreated` | Array of structured locations where the image was created |

Each location structure contains: `City`, `ProvinceState`, `CountryName`,
`CountryCode`, `Sublocation`, `WorldRegion`, and optionally
`GPSLatitude`/`GPSLongitude`/`GPSAltitude` fields. No IIM equivalent exists.

> **GPS vs editorial location:** GPS coordinates record where the camera
> physically was. Editorial location fields describe the place depicted in
> the image, which may differ. IPTC Extension LocationCreated bridges this
> gap by providing a structured location specifically for where the camera
> was located.

---

## Credit / Provider Family

| Standard | Location | ImageIO Key / XMP Path |
|----------|----------|----------------------|
| IPTC IIM | Dataset 2:110 Credit | `kCGImagePropertyIPTCCredit` |
| XMP | `photoshop:Credit` | `photoshop:Credit` |

No EXIF/TIFF equivalent. The field was originally named "Credit" in IIM,
renamed to "Provider" in IPTC Core 1.0, then to "Credit Line" in IPTC
Core 1.1. Despite the name changes, the underlying IIM dataset number and
XMP path remain the same.

---

## Source Family

| Standard | Location | ImageIO Key / XMP Path |
|----------|----------|----------------------|
| IPTC IIM | Dataset 2:115 Source | `kCGImagePropertyIPTCSource` |
| XMP | `photoshop:Source` | `photoshop:Source` |

No EXIF/TIFF equivalent. Identifies the original owner or copyright holder
of the intellectual content (not necessarily the photographer).

---

## Rating / Urgency

| Standard | Location | ImageIO Key / XMP Path | Range |
|----------|----------|----------------------|-------|
| XMP | `xmp:Rating` | `xmp:Rating` | -1 to 5 (-1 = rejected, 0 = unrated, 1-5 = stars) |
| IPTC IIM | Dataset 2:10 Urgency | `kCGImagePropertyIPTCUrgency` | 1-8 (1 = most urgent, 5 = normal, 8 = least) |
| XMP | `photoshop:Urgency` | `photoshop:Urgency` | 1-8 (same as IIM) |

**Important:** `xmp:Rating` and IPTC Urgency are **not** semantically
equivalent. Rating is an editorial quality/importance assessment. Urgency is
a distribution priority indicator from the wire service era. They should never
be mapped to each other.

Urgency was deprecated from the IPTC Core schema (version 1.1+) but remains
synchronized with `photoshop:Urgency` via XMP for legacy compatibility.

---

## Instructions / Special Instructions

| Standard | Location | ImageIO Key / XMP Path | Max Length (IIM) |
|----------|----------|----------------------|------------------|
| IPTC IIM | Dataset 2:40 SpecialInstructions | `kCGImagePropertyIPTCSpecialInstructions` | 256 chars |
| XMP | `photoshop:Instructions` | `photoshop:Instructions` | — |

Used for editorial/handling instructions to the receiver. Often contains
embargo dates or usage restrictions.

---

## Writer / Caption Writer

| Standard | Location | ImageIO Key / XMP Path | Max Length (IIM) |
|----------|----------|----------------------|------------------|
| IPTC IIM | Dataset 2:122 Writer-Editor | `kCGImagePropertyIPTCWriterEditor` | 32 chars |
| XMP | `photoshop:CaptionWriter` | `photoshop:CaptionWriter` | — |

The person who wrote the caption/description. Distinct from the Creator
(photographer).

---

## Category / Supplemental Category (Deprecated)

| Standard | Location | ImageIO Key / XMP Path | Max Length (IIM) |
|----------|----------|----------------------|------------------|
| IPTC IIM | Dataset 2:15 Category | `kCGImagePropertyIPTCCategory` | 3 chars |
| IPTC IIM | Dataset 2:20 Supplemental Category | `kCGImagePropertyIPTCSupplementalCategory` | 32 chars, repeatable |
| XMP | `photoshop:Category` | `photoshop:Category` | — |
| XMP | `photoshop:SupplementalCategories` | `photoshop:SupplementalCategories` | — |

**Deprecated.** These fields were deprecated by the IPTC in favor of
`Iptc4xmpCore:SubjectCode` (IPTC Subject Reference taxonomy). Category is
limited to 3 characters and was designed for the wire service categorization
system (e.g., `"SPO"` for sports). Still present in many legacy files.

---

## Contact Info (XMP-Only Structured)

| XMP Path | Purpose |
|----------|---------|
| `Iptc4xmpCore:CreatorContactInfo` | Structured contact info for the creator |

Contains fields: `CiEmailWork`, `CiTelWork`, `CiAdrExtadr` (address),
`CiAdrCity`, `CiAdrRegion`, `CiAdrPcode` (postal code), `CiAdrCtry`
(country), `CiUrlWork`. No EXIF or IPTC IIM equivalent exists — this is an
XMP-only structure from the IPTC Core schema.

---

## Orientation (Special Case)

Orientation is not a typical overlapping field but exists in multiple
locations within the same standard ecosystem:

| Location | Values | ImageIO Key |
|----------|--------|-------------|
| TIFF IFD0 tag 0x0112 Orientation | 1-8 | `kCGImagePropertyTIFFOrientation` |
| Top-level property | 1-8 | `kCGImagePropertyOrientation` |
| XMP | 1-8 | `tiff:Orientation` |

These should always agree. The top-level `kCGImagePropertyOrientation` is a
convenience alias that ImageIO derives from the TIFF IFD0 value. See
[orientation-mapping.md](orientation-mapping.md) for the complete mapping
across EXIF, CGImagePropertyOrientation, and UIImage.Orientation numbering
systems.

---

## Software / Processing Information

| Standard | Location | ImageIO Key / XMP Path |
|----------|----------|----------------------|
| TIFF | IFD0 tag 0x0131 Software | `kCGImagePropertyTIFFSoftware` |
| XMP | `tiff:Software` | `tiff:Software` |
| XMP | `xmp:CreatorTool` | `xmp:CreatorTool` |

`tiff:Software` is the XMP mirror of the TIFF binary tag. `xmp:CreatorTool`
is an XMP-native field. They are often the same but can differ: `Software`
is the last processing software, while `CreatorTool` is the original
creating application.

---

## Rights Management (XMP-Only)

These fields have no EXIF or IPTC IIM equivalents:

| XMP Path | Purpose | Type |
|----------|---------|------|
| `xmpRights:Marked` | Copyright status (true/false/absent) | Boolean |
| `xmpRights:UsageTerms` | Human-readable license terms | `langAlt` |
| `xmpRights:WebStatement` | URL to license/rights information | Text (URI) |
| `xmpRights:Owner` | Copyright owner(s) | `rdf:Bag` |
| `plus:Licensor` | PLUS licensing framework — licensor info | Structured |
| `plus:CopyrightOwner` | PLUS — copyright owner info | Structured |
| `plus:ImageSupplier` | PLUS — image supplier info | Structured |

---

## AI / Provenance (Emerging)

These are increasingly relevant fields that exist only in XMP:

| XMP Path | Purpose | Spec |
|----------|---------|------|
| `Iptc4xmpExt:DigitalSourceType` | How the image was created (original, composite, AI-generated, etc.) | IPTC Extension 1.6+ |
| `c2pa:*` | Coalition for Content Provenance and Authenticity | C2PA spec |
| `xmp:CreateDate` + `xmpMM:OriginalDocumentID` | Provenance chain | XMP Media Management |

`Iptc4xmpExt:DigitalSourceType` uses a controlled vocabulary from
`http://cv.iptc.org/newscodes/digitalsourcetype/`. Values include
`trainedAlgorithmicMedia` (AI-generated), `compositeSynthetic`, etc.

---

## Complete Cross-Reference Table

A condensed view of all overlapping fields and where they live:

| Concept | EXIF/TIFF Tag | IPTC IIM Dataset | XMP Path(s) | MWG Preferred |
|---------|---------------|------------------|-------------|---------------|
| **Date taken** | ExifIFD 0x9003 DateTimeOriginal | 2:55 DateCreated + 2:60 TimeCreated | `photoshop:DateCreated`, `exif:DateTimeOriginal` | `photoshop:DateCreated` |
| **Date digitized** | ExifIFD 0x9004 DateTimeDigitized | 2:62 DigitalCreationDate + 2:63 DigitalCreationTime | `xmp:CreateDate`, `exif:DateTimeDigitized` | `xmp:CreateDate` |
| **Date modified** | IFD0 0x0132 DateTime | -- | `xmp:ModifyDate`, `tiff:DateTime` | `xmp:ModifyDate` |
| **Creator** | IFD0 0x013B Artist | 2:80 By-line | `dc:creator` | `dc:creator` |
| **Creator title** | -- | 2:85 By-lineTitle | `photoshop:AuthorsPosition` | XMP |
| **Copyright** | IFD0 0x8298 Copyright | 2:116 CopyrightNotice | `dc:rights` | `dc:rights` |
| **Description** | IFD0 0x010E ImageDescription | 2:120 Caption-Abstract | `dc:description` | `dc:description` |
| **Keywords** | -- | 2:25 Keywords | `dc:subject` | `dc:subject` |
| **Title** | -- | 2:5 ObjectName | `dc:title` | `dc:title` |
| **Headline** | -- | 2:105 Headline | `photoshop:Headline` | XMP |
| **City** | -- | 2:90 City | `photoshop:City` | XMP |
| **State/Province** | -- | 2:95 Province/State | `photoshop:State` | XMP |
| **Country** | -- | 2:101 Country | `photoshop:Country` | XMP |
| **Country code** | -- | 2:100 CountryCode | `Iptc4xmpCore:CountryCode` | XMP |
| **Sub-location** | -- | 2:92 Sub-location | `Iptc4xmpCore:Location` | XMP |
| **Credit line** | -- | 2:110 Credit | `photoshop:Credit` | XMP |
| **Source** | -- | 2:115 Source | `photoshop:Source` | XMP |
| **Instructions** | -- | 2:40 SpecialInstructions | `photoshop:Instructions` | XMP |
| **Caption writer** | -- | 2:122 Writer-Editor | `photoshop:CaptionWriter` | XMP |
| **Urgency** | -- | 2:10 Urgency | `photoshop:Urgency` | XMP |
| **Rating** | -- | -- | `xmp:Rating` | XMP (only) |
| **Orientation** | IFD0 0x0112 | -- | `tiff:Orientation` | -- |
| **GPS coords** | GPS IFD tags | -- | `exif:GPSLatitude`, `exif:GPSLongitude` | -- |
| **Software** | IFD0 0x0131 Software | -- | `tiff:Software`, `xmp:CreatorTool` | -- |
| **Usage terms** | -- | -- | `xmpRights:UsageTerms` | XMP (only) |
| **Contact info** | -- | -- | `Iptc4xmpCore:CreatorContactInfo` | XMP (only) |

---

## IPTC IIM Field Length Limits

When writing to IPTC IIM, these maximum lengths apply. XMP has no such limits.

| IIM Dataset | Field | Max Length |
|-------------|-------|-----------|
| 2:5 | ObjectName (Title) | 64 chars |
| 2:10 | Urgency | 1 char |
| 2:15 | Category | 3 chars |
| 2:20 | SupplementalCategory | 32 chars per value |
| 2:25 | Keywords | 64 chars per keyword |
| 2:40 | SpecialInstructions | 256 chars |
| 2:55 | DateCreated | 8 chars (`YYYYMMDD`) |
| 2:60 | TimeCreated | 11 chars (`HHMMSS±HHMM`) |
| 2:80 | By-line | 32 chars per value |
| 2:85 | By-lineTitle | 32 chars |
| 2:90 | City | 32 chars |
| 2:92 | Sub-location | 32 chars |
| 2:95 | Province/State | 32 chars |
| 2:100 | CountryCode | 3 chars |
| 2:101 | Country | 64 chars |
| 2:105 | Headline | 256 chars |
| 2:110 | Credit | 32 chars |
| 2:115 | Source | 32 chars |
| 2:116 | CopyrightNotice | 128 chars |
| 2:120 | Caption-Abstract | 2000 chars |
| 2:122 | Writer-Editor | 32 chars |

> These are byte limits in the IIM specification, but in practice they are
> treated as character limits for UTF-8 text. Non-ASCII characters consume
> multiple bytes, so the effective character limit may be lower.

---

## Cross-References

- [mwg-guidelines.md](mwg-guidelines.md) — Reconciliation rules for reading
  and writing overlapping fields
- [imageio-behavior.md](imageio-behavior.md) — How Apple ImageIO handles
  cross-standard sync
- [orientation-mapping.md](orientation-mapping.md) — Three orientation
  numbering systems
- [pitfalls.md](pitfalls.md) — Common problems with overlapping fields
- [../exif/xmp-mapping.md](../exif/xmp-mapping.md) — Complete EXIF-to-XMP
  mapping tables
