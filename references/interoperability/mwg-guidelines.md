# Metadata Working Group (MWG) Guidelines

> Part of [Interoperability Reference](README.md)

The Metadata Working Group guidelines define how applications should handle
redundant or inconsistent metadata when the same field exists in EXIF, IPTC
IIM, and XMP simultaneously. Though called "guidelines," the document is
written as a specification with precise algorithms, pseudocode, and an
accompanying verification test suite.

---

## Overview

| Aspect | Detail |
|--------|--------|
| **Document** | Guidelines for Handling Image Metadata, Version 2.0 |
| **Date** | November 2010 |
| **Founded** | 2006 |
| **Members** | Adobe, Apple, Canon, Microsoft, Nokia, Sony (founding members) |
| **Status** | No updates since 2010; the MWG is effectively dormant |
| **Scope** | Interoperability among EXIF, IPTC IIM, and XMP in consumer digital images |
| **Spec PDF** | [MWG Guidelines 2.0](https://s3.amazonaws.com/software.tagthatphoto.com/docs/mwg_guidance.pdf) |

### Why It Matters

Before MWG, every application handled metadata conflicts differently. Some
preferred EXIF, some preferred XMP, and there was no standard way to determine
whether IPTC IIM and XMP were in sync. The MWG specification provides:

1. **A reading reconciliation algorithm** for each overlapping field
2. **Writing rules** to keep all locations synchronized
3. **IPTCDigest** as a sync-detection mechanism
4. **Multi-value conventions** for fields like Creator (semicolons in EXIF)
5. **UTF-8 recommendation** for EXIF "ASCII" strings
6. **Preferred metadata sources** for each field group

### Current Relevance

Despite being from 2010, MWG guidelines remain the de facto standard for
metadata reconciliation. ExifTool, Adobe products, and many DAM tools
implement MWG-conformant behavior. Apple's ImageIO framework implements a
subset of MWG-like behavior (see [imageio-behavior.md](imageio-behavior.md))
but does not claim full MWG conformance.

The 2010 date means MWG predates HEIF/HEIC, computational photography, AI
content generation, and C2PA provenance. For these newer topics, no equivalent
cross-standard reconciliation specification exists.

---

## Core Concepts

### The Three Storage Layers

The MWG addresses metadata stored in three layers within a single image file:

| Layer | Standard | Binary Format | Scope |
|-------|----------|--------------|-------|
| **EXIF/TIFF** | CIPA EXIF (within TIFF IFD structure) | Binary IFD entries | Camera settings, timestamps, orientation, make/model |
| **IPTC IIM** | IPTC Information Interchange Model | Binary dataset records | Editorial: caption, keywords, copyright, location |
| **XMP** | ISO 16684-1 (Adobe XMP) | UTF-8 XML/RDF | All of the above + unlimited extensibility |

XMP can represent everything that EXIF and IPTC IIM contain, plus arbitrary
additional data. The MWG's fundamental premise is that XMP is the preferred
storage but backward compatibility requires maintaining all three.

### The Fundamental Problem

When an application modifies Caption in XMP but not in IPTC IIM, or updates
Artist in EXIF but not in XMP, the metadata becomes inconsistent. A reader
then faces three potentially conflicting values with no way to know which is
current. The MWG solves this with IPTCDigest-based sync detection and
explicit reconciliation rules.

---

## IPTCDigest — The Sync Detection Mechanism

The IPTCDigest is the linchpin of MWG reconciliation. It is an MD5 hash of
the entire IPTC IIM data block, stored in XMP as
`photoshop:LegacyIPTCDigest`.

### How It Works

```
1. An MWG-conformant app writes/modifies IPTC IIM and XMP simultaneously
2. After writing IPTC IIM, it computes MD5(entire IPTC IIM block)
3. It stores this hash in XMP as photoshop:LegacyIPTCDigest
4. On next read, it recomputes MD5 of current IPTC IIM and compares to stored digest
5. If they match: IPTC IIM and XMP are in sync (prefer XMP)
6. If they don't match: a non-MWG app modified IPTC IIM since last sync
```

### IPTCDigest States and Their Meaning

| State | Condition | Interpretation | Action |
|-------|-----------|---------------|--------|
| **Match** | `photoshop:LegacyIPTCDigest` == MD5(current IPTC IIM) | XMP and IPTC IIM are synchronized. A MWG-conformant app made the last edit. | Prefer XMP values (they are more expressive) |
| **Mismatch** | `photoshop:LegacyIPTCDigest` != MD5(current IPTC IIM) | A non-MWG-conformant app modified IPTC IIM without updating XMP. IPTC IIM may be newer. | Apply field-by-field reconciliation (see below) |
| **Absent** | No `photoshop:LegacyIPTCDigest` in XMP | File predates MWG or was created by a non-MWG app | Prefer XMP values (assume XMP is authoritative) |
| **Present, no IIM** | `photoshop:LegacyIPTCDigest` exists but no IPTC IIM block | IPTC IIM was removed by some process | Ignore digest; use XMP values |

### Digest Calculation Details

- **Input:** The raw bytes of the entire IPTC IIM data block (all Record 2
  datasets, in the order they appear in the file)
- **Algorithm:** MD5 (128-bit hash)
- **Output:** 32-character hexadecimal string stored in
  `photoshop:LegacyIPTCDigest`
- **Scope:** Only covers IPTC IIM (Record 2). Does not cover EXIF or XMP.

### Why MD5?

MD5 is used for change detection, not security. The MWG spec chose it for
speed and universal availability. It does not need to be collision-resistant
for this use case — it only needs to detect when the IPTC IIM block has been
modified.

---

## Reading Reconciliation Algorithm

The MWG defines a priority-based reconciliation algorithm for reading
metadata. The algorithm varies by field type but follows a general pattern.

### General Reading Algorithm (Pseudocode)

```
function readField(fieldGroup):
    xmpValue = readXMP(fieldGroup.xmpPath)
    exifValue = readEXIF(fieldGroup.exifTag)    // if applicable
    iimValue = readIIM(fieldGroup.iimDataset)   // if applicable

    if only one source exists:
        return that source's value

    if xmpValue exists AND iimValue exists:
        digestStatus = checkIPTCDigest()

        if digestStatus == MATCH or digestStatus == ABSENT:
            return xmpValue    // XMP is preferred

        if digestStatus == MISMATCH:
            // A non-MWG app may have updated IIM
            predictedIIM = convertToIIM(xmpValue)
            if predictedIIM == iimValue:
                return xmpValue    // Values actually agree despite digest mismatch
            else:
                return iimValue    // IIM was truly modified; it's newer

    if xmpValue exists AND exifValue exists:
        return xmpValue    // XMP preferred over EXIF

    if exifValue exists AND iimValue exists:
        return iimValue    // IIM preferred over EXIF (more expressive for text fields)

    return whichever exists
```

### The "Predicted IIM" Comparison

When the digest mismatches, the MWG does not immediately prefer IPTC IIM.
Instead, it creates a "predicted" IPTC IIM value from the XMP value by
applying the same transformations that a MWG-conformant writer would apply:

1. Extract `x-default` from `langAlt` fields
2. Truncate to IPTC IIM field length limits
3. Convert character encoding (UTF-8 to applicable encoding)
4. Compare the predicted value with the actual IPTC IIM value

If they match despite the digest mismatch (which can happen if a tool
modified the IPTC binary layout without changing field values), XMP is still
preferred. Only when the predicted value differs from the actual IPTC IIM
value does the algorithm use the IPTC IIM value.

This prevents false positives from tools that re-serialize IPTC IIM blocks
(changing the binary layout, thus the digest) without modifying field values.

---

## Field-Specific Reconciliation Rules

### Description / Caption Group

| Source | Tag |
|--------|-----|
| EXIF/TIFF | IFD0 ImageDescription (0x010E) |
| IPTC IIM | Caption-Abstract (2:120) |
| XMP | `dc:description` |

**Reading priority:**

1. XMP `dc:description` (preferred if IPTCDigest matches or is absent)
2. IPTC IIM Caption-Abstract (preferred if IPTCDigest mismatches AND
   predicted value differs)
3. EXIF ImageDescription (fallback if neither XMP nor IIM exist)

**Writing rule:** Update all three locations.

**Type coercion on write:**
- XMP `dc:description` is `langAlt` → write `x-default` language variant
- IPTC IIM Caption-Abstract is plain text → extract `x-default`, truncate
  to 2000 chars
- EXIF ImageDescription is ASCII → write UTF-8 (per MWG recommendation)

**Special case:** `tiff:ImageDescription` in XMP is the mirror of the EXIF
binary tag. The MWG treats `dc:description` as the authoritative XMP
location, not `tiff:ImageDescription`.

### Creator / Author / Artist Group

| Source | Tag |
|--------|-----|
| EXIF/TIFF | IFD0 Artist (0x013B) |
| IPTC IIM | By-line (2:80) — repeatable |
| XMP | `dc:creator` — `rdf:Seq` |

**Reading priority:** Same algorithm as Description.

**Multi-value handling (critical):**

EXIF Artist is a single string. MWG mandates the semicolon-space convention:

```
XMP:        ["Jane Doe", "John Smith", "Alice"]
EXIF:       "Jane Doe; John Smith; Alice"
IPTC IIM:   [2:80 "Jane Doe"] [2:80 "John Smith"] [2:80 "Alice"]
```

**Quoting rules for semicolons in names:**
```
XMP:        ["Doe; Jane Inc.", "John Smith"]
EXIF:       "\"Doe; Jane Inc.\"; John Smith"
```

A literal double quote within a name is escaped by doubling:
```
XMP:        ["She said \"hello\"", "Other"]
EXIF:       "\"She said \"\"hello\"\"\"; Other"
```

**Parsing algorithm for EXIF Artist:**
1. Split on `; ` (semicolon-space)
2. If a segment starts with `"`, it is a quoted segment — find the matching
   closing `"` (unescaped), treating `""` as an escaped literal quote
3. Strip outer quotes from quoted segments
4. Replace `""` with `"` within unquoted result

### Copyright Group

| Source | Tag |
|--------|-----|
| EXIF/TIFF | IFD0 Copyright (0x8298) |
| IPTC IIM | CopyrightNotice (2:116) |
| XMP | `dc:rights` |

**Reading priority:** Same algorithm as Description.

**Special EXIF copyright format:** The EXIF spec allows the Copyright field
to contain two strings separated by a NULL byte: photographer copyright
followed by editor copyright. The MWG treats the entire field as a single
string for reconciliation. If a NULL separator exists, concatenate with a
space or use only the photographer portion.

### Date/Time (Original) Group

| Source | Tags |
|--------|------|
| EXIF | DateTimeOriginal (0x9003) + SubSecTimeOriginal (0x9291) + OffsetTimeOriginal (0x9011) |
| IPTC IIM | DateCreated (2:55) + TimeCreated (2:60) |
| XMP | `photoshop:DateCreated` |

**Reading priority:** Same general algorithm, but with additional complexity
due to format differences.

**Constructing a complete timestamp from EXIF:**
```
DateTimeOriginal:      "2024:06:15 14:30:00"     (date + time, no TZ)
SubSecTimeOriginal:    "123"                      (fractional seconds)
OffsetTimeOriginal:    "+05:30"                   (timezone offset)
--> Combined:          2024-06-15T14:30:00.123+05:30
```

**Constructing from IPTC IIM:**
```
DateCreated:           "20240615"                 (date only)
TimeCreated:           "143000+0530"              (time + TZ)
--> Combined:          2024-06-15T14:30:00+05:30  (no fractional seconds possible)
```

**Constructing from XMP:**
```
photoshop:DateCreated: "2024-06-15T14:30:00.123+05:30"  (already complete)
```

**Timezone preservation (MWG rule):** Timezone information must not be
implicitly added. If the source has no timezone (e.g., EXIF DateTimeOriginal
without OffsetTimeOriginal), the XMP value should also lack a timezone
designator. Existing timezone values must be preserved during round-trips.

**Precision preservation:**
- SubSecTimeOriginal `"123"` maps to fractional seconds `.123` in ISO 8601
- IPTC IIM does not support fractional seconds — precision is lost
- EXIF binary datetime has 1-second resolution
- XMP can represent arbitrary precision

**MWG preferred source:** `photoshop:DateCreated` (not `exif:DateTimeOriginal`,
which is the mechanical EXIF mirror).

### Date/Time (Digitized) Group

| Source | Tags |
|--------|------|
| EXIF | DateTimeDigitized (0x9004) + SubSecTimeDigitized + OffsetTimeDigitized |
| IPTC IIM | DigitalCreationDate (2:62) + DigitalCreationTime (2:63) |
| XMP | `xmp:CreateDate` |

Same algorithm as Date/Time (Original). For digital cameras, this usually
equals the original date/time. For scanned images, it records the scan date.

### Date/Time (Modified) Group

| Source | Tags |
|--------|------|
| EXIF/TIFF | DateTime (IFD0 0x0132) + SubSecTime + OffsetTime |
| XMP | `xmp:ModifyDate` |

No IPTC IIM equivalent. Reading priority: XMP preferred.

### Keywords Group

| Source | Tag |
|--------|-----|
| IPTC IIM | Keywords (2:25) — repeatable |
| XMP | `dc:subject` — `rdf:Bag` |

**Reading priority:** Same algorithm as Description (no EXIF equivalent).

**Set semantics:** Keywords are unordered sets. When comparing predicted IIM
to actual IIM during mismatch reconciliation, order does not matter — only
the set of values.

**Case sensitivity:** MWG does not specify. In practice, keywords are
case-sensitive (a keyword "Beach" is different from "beach").

### Rating

`xmp:Rating` is XMP-only. Not part of MWG reconciliation. Value range: -1
(rejected) to 5 (five stars), with 0 meaning unrated.

IPTC Urgency (2:10 / `photoshop:Urgency`) is semantically different from
Rating and the MWG explicitly states they should NOT be mapped to each other.

### Location Group

| Source | Tags |
|--------|------|
| IPTC IIM | City (2:90), Province/State (2:95), Country (2:101), CountryCode (2:100), Sub-location (2:92) |
| XMP | `photoshop:City`, `photoshop:State`, `photoshop:Country`, `Iptc4xmpCore:CountryCode`, `Iptc4xmpCore:Location` |

**Reading priority:** Same algorithm as Description (no EXIF equivalent for
editorial location; GPS is a separate domain not covered by MWG
reconciliation).

**Each sub-field is independent.** City, State, Country, CountryCode, and
Sub-location are reconciled independently. A file could have City from XMP
and Country from IPTC IIM if the digest mismatches.

---

## Writing Rules

### Fundamental Principle

> When a field value is changed, the MWG-conformant application **must update
> all locations** where that field exists — EXIF/TIFF, IPTC IIM, and XMP.

This ensures backward compatibility: an older application that only reads
EXIF will still see the updated value, as will one that only reads IPTC IIM,
and one that only reads XMP.

### Writing Algorithm

For each overlapping field, when writing:

1. **Write the XMP value.** XMP is the primary store and the preferred read
   source. Use the appropriate XMP type (`langAlt`, `rdf:Seq`, `rdf:Bag`,
   simple text, etc.).
2. **Write the corresponding EXIF/TIFF value** if the field has an EXIF
   equivalent and the format supports EXIF. Apply type coercion (ISO 8601 to
   EXIF datetime format, `langAlt` to ASCII string, etc.).
3. **Write the corresponding IPTC IIM value** if the field has an IPTC IIM
   equivalent and the format supports IPTC IIM. Apply type coercion and
   length truncation.
4. **Recompute and update the IPTCDigest** to reflect the new IPTC IIM state.

### Write-Only to XMP When IIM Not Present

If the original file does **not** contain an IPTC IIM block, an
MWG-conformant application **should not create** a new IPTC IIM block. Write
to XMP (and EXIF if applicable) only. This avoids introducing a legacy data
block unnecessarily.

If the file already contains IPTC IIM, the application must keep it
synchronized. The intent is to prevent IPTC IIM from propagating into files
that never had it.

### Write-Only to XMP When Format Does Not Support IIM

| Format | EXIF Write | IPTC IIM Write | XMP Write |
|--------|-----------|---------------|-----------|
| JPEG | Yes | Yes (if already present) | Yes |
| TIFF | Yes | Yes (if already present) | Yes |
| HEIF/HEIC | Yes | N/A (not supported) | Yes |
| PNG | N/A | N/A | Yes |
| WebP | N/A | N/A | Yes |
| DNG | Yes | N/A | Yes |
| AVIF | N/A | N/A | Yes |

For HEIF and other modern formats, IPTC IIM is irrelevant. Only XMP (and
EXIF where supported) needs to be written.

---

## Strict Conformance Mode

In "strict MWG conformance mode" (as implemented by ExifTool's MWG module):

1. **Non-standard metadata locations are ignored.** For example, IPTC IIM in
   a HEIF file (which should not exist) would be ignored.
2. **Warnings are generated** when non-standard metadata is encountered.
3. **EXIF Artist is treated as a list.** The semicolon-space separator
   convention is enforced for multi-value Creator fields.
4. **IPTCDigest is actively maintained.** Updated on every IPTC IIM write.
5. **Type coercion is enforced.** `langAlt` values are properly extracted
   for IIM/EXIF, arrays are properly serialized, etc.

Non-strict mode (default in many applications) reads metadata from all
locations regardless of whether the location is standard for the format. This
is more permissive but can lead to reading stale or incorrect data from
non-standard locations.

---

## Multi-Value Field Conventions

### Creator (dc:creator / EXIF Artist / IPTC By-line)

| Format | Storage |
|--------|---------|
| XMP | `rdf:Seq` — ordered array of strings |
| EXIF Artist | Single string with `; ` (semicolon-space) separator |
| IPTC IIM By-line | Multiple repeating 2:80 datasets (max 32 chars each) |

**Conversion rules (MWG):**

```
XMP:        ["Jane Doe", "John Smith"]
EXIF:       "Jane Doe; John Smith"
IPTC IIM:   [2:80 "Jane Doe"] [2:80 "John Smith"]
```

If a name contains a semicolon:
```
XMP:        ["Doe; Jane", "John Smith"]
EXIF:       "\"Doe; Jane\"; John Smith"
IPTC IIM:   [2:80 "Doe; Jane"] [2:80 "John Smith"]
```

> **IPTC IIM does not have this quoting problem** because each value is a
> separate dataset. The quoting convention only applies to EXIF Artist.

### Keywords (dc:subject / IPTC Keywords)

| Format | Storage |
|--------|---------|
| XMP | `rdf:Bag` — unordered set of strings |
| IPTC IIM | Multiple repeating 2:25 datasets (max 64 chars each) |

Keywords are always treated as individual values, never concatenated into a
single string. The conversion is straightforward: each `rdf:Bag` element
becomes a separate 2:25 dataset, and vice versa.

---

## UTF-8 Recommendation for EXIF

The MWG recommends that EXIF "ASCII" string values (EXIF data type 2) be
stored as UTF-8. This is technically contrary to the EXIF specification,
which defines ASCII type as 7-bit ASCII only.

**Rationale:** Many real-world images already contain UTF-8 in EXIF ASCII
fields. Cameras and phones with non-ASCII locale settings (e.g., Japanese,
Korean, Chinese, European languages) write UTF-8 strings into EXIF fields
tagged as ASCII. The MWG pragmatically acknowledges this reality and
recommends:

1. **Writers** should write UTF-8 to EXIF ASCII fields when the content
   requires characters outside 7-bit ASCII.
2. **Readers** should accept UTF-8 in ASCII fields and decode accordingly.
3. **Validators** should not reject files with UTF-8 in ASCII fields.

**EXIF 3.0 update (2023):** The EXIF 3.0 specification formally added UTF-8
support as a new data type (type 129 (0x81), "utf8"), making the MWG recommendation
less necessary for new images but still relevant for the billions of existing
legacy files.

---

## Date/Time Handling Across Standards

The MWG specification addresses the complexity of datetime reconciliation
in considerable detail. This is the most error-prone area of metadata
interoperability.

### Constructing a Complete Timestamp

A complete timestamp requires four components: date, time, fractional seconds,
and timezone. No single EXIF field contains all components.

**From EXIF (up to 3 separate tags):**
```
DateTimeOriginal:      "2024:06:15 14:30:00"     (date + time, no TZ)
SubSecTimeOriginal:    "123"                      (fractional seconds)
OffsetTimeOriginal:    "+05:30"                   (timezone offset)
--> Combined:          2024-06-15T14:30:00.123+05:30
```

**From IPTC IIM (2 separate datasets):**
```
DateCreated:           "20240615"                 (date only)
TimeCreated:           "143000+0530"              (time + TZ)
--> Combined:          2024-06-15T14:30:00+05:30
                       (no fractional seconds — IPTC IIM cannot express them)
```

**From XMP (single field, complete):**
```
photoshop:DateCreated: "2024-06-15T14:30:00.123+05:30"  (all components)
```

### Timezone Preservation Rules

The MWG is explicit about timezone handling:

1. **Do not add timezone if source lacks it.** If EXIF DateTimeOriginal has
   no OffsetTimeOriginal, the XMP value should be timezone-naive:
   `"2024-06-15T14:30:00"` (no `+HH:MM` or `Z` suffix).
2. **Do not remove timezone if source has it.** If converting from XMP to
   EXIF and the XMP value has a timezone, write the corresponding
   OffsetTimeOriginal tag.
3. **Preserve the exact offset.** Do not convert `+05:30` to UTC. The offset
   carries geographic information.

### Precision Preservation Rules

When converting between formats, preserve as much precision as possible:

| Source | Destination | Precision Impact |
|--------|------------|-----------------|
| XMP (fractional seconds) | EXIF | SubSecTime* preserves fractional seconds |
| XMP (fractional seconds) | IPTC IIM | **Precision lost** (no fractional seconds in IIM) |
| EXIF + SubSecTime | XMP | Fractional seconds preserved |
| EXIF + SubSecTime | IPTC IIM | **Precision lost** |
| IPTC IIM (no fractional sec) | XMP | No precision added (write without fractional seconds) |
| IPTC IIM (no fractional sec) | EXIF | No SubSecTime written |

### Partial Date Handling

XMP ISO 8601 allows partial dates: `"2024"` (year only), `"2024-06"` (year
and month), etc. EXIF and IPTC IIM require specific fixed-length formats. The
MWG recommends:

- When writing partial dates to EXIF: pad with zeros or spaces
  (`"2024:00:00 00:00:00"` or `"2024:  :   :  :  "`)
- When writing partial dates to IPTC IIM: write only the date dataset without
  the time dataset
- When reading partial EXIF dates with zeros: convert to the corresponding
  partial ISO 8601 form

---

## Practical Implementation Notes

### For iOS Developers Using ImageIO

Apple's ImageIO framework implements a subset of MWG-like behavior. Here is
how it compares to full MWG conformance:

| MWG Feature | ImageIO Behavior | Gap |
|-------------|-----------------|-----|
| Read-side auto-synthesis | Yes — both APIs see metadata from all sources | Comparable to MWG reading reconciliation |
| IPTCDigest validation | **No** — ImageIO does not check `photoshop:LegacyIPTCDigest` | Cannot detect IPTC-only edits by non-MWG tools |
| IPTCDigest update on write | **No** — digest is not maintained | Files written by ImageIO will have stale or absent digest |
| Multi-location write sync | Partial — `CopyImageSource` regenerates IPTC IIM from XMP | EXIF/TIFF binary is preserved in merge mode, not regenerated |
| Date format sync | **Gap** — `photoshop:DateCreated` (ISO 8601) is not converted to IPTC IIM format | Must write IIM date fields separately if IIM compatibility required |
| EXIF Artist semicolon convention | Not enforced | Application must implement quoting/splitting |
| Write-only-to-XMP when no IIM | **No** — `CopyImageSource` creates IPTC IIM from XMP regardless | May introduce IIM block into files that never had one |

See [imageio-behavior.md](imageio-behavior.md) for detailed ImageIO behavior.

### ExifTool MWG Module

ExifTool provides the most complete MWG implementation available. Enable it
with the `-use MWG` flag:

```bash
# Read with MWG reconciliation
exiftool -use MWG -MWG:Description photo.jpg

# Write with MWG synchronization (updates all locations)
exiftool -use MWG -MWG:Description="My caption" photo.jpg

# Read all MWG composite tags
exiftool -use MWG -MWG:all photo.jpg
```

When the MWG module is loaded:
- MWG Composite tags are available (MWG:Description, MWG:Creator, etc.)
- Strict conformance mode is activated
- IPTCDigest is automatically maintained
- Multi-value EXIF Artist uses semicolon convention
- Non-standard metadata locations generate warnings
- Write operations update all locations simultaneously

### MWG Composite Tags in ExifTool

| MWG Tag | Reconciles | Sources (read priority) |
|---------|-----------|------------------------|
| `MWG:Description` | Caption/Description | XMP `dc:description` > IPTC Caption-Abstract > EXIF ImageDescription |
| `MWG:Creator` | Author/Artist | XMP `dc:creator` > IPTC By-line > EXIF Artist |
| `MWG:Copyright` | Copyright notice | XMP `dc:rights` > IPTC CopyrightNotice > EXIF Copyright |
| `MWG:CreateDate` | Original date/time | XMP `photoshop:DateCreated` > EXIF DateTimeOriginal(+subs+offset) > IPTC DateCreated+TimeCreated |
| `MWG:DateTimeOriginal` | Same as CreateDate | Same as MWG:CreateDate |
| `MWG:ModifyDate` | Modification date | XMP `xmp:ModifyDate` > EXIF DateTime (IFD0) |
| `MWG:Keywords` | Keywords | XMP `dc:subject` > IPTC Keywords |
| `MWG:Rating` | Rating | XMP `xmp:Rating` (XMP only — no reconciliation) |
| `MWG:Country` | Country name | XMP `photoshop:Country` > IPTC Country |
| `MWG:State` | State/province | XMP `photoshop:State` > IPTC Province/State |
| `MWG:City` | City | XMP `photoshop:City` > IPTC City |
| `MWG:Location` | Sub-location | XMP `Iptc4xmpCore:Location` > IPTC Sub-location |

The `>` symbol indicates fallback order, not just preference. IPTCDigest
status affects whether IPTC IIM is preferred over XMP.

---

## MWG 2.0 vs MWG 1.0 Changes

Version 2.0 (November 2010) updated version 1.0 (September 2008):

| Area | MWG 1.0 | MWG 2.0 |
|------|---------|---------|
| **Reading algorithm** | Simple priority (XMP > IIM > EXIF) | Digest-based reconciliation with predicted-value comparison |
| **IPTCDigest** | Mentioned but not fully specified | Full algorithm with edge cases |
| **Date/Time** | Basic rules | Detailed timezone and precision preservation rules |
| **Creator multi-value** | Not specified | Semicolon-space convention with quoting rules |
| **UTF-8 recommendation** | Not specified | Explicit recommendation for EXIF ASCII fields |
| **Partial dates** | Not addressed | Explicit handling rules |
| **Error handling** | Not addressed | Specified behavior for corrupted or invalid values |

---

## Edge Cases and Special Situations

### When All Three Sources Disagree

If EXIF, IPTC IIM, and XMP all have different values for the same field:

1. Check IPTCDigest for XMP/IIM sync status
2. If digest matches: XMP wins (it is in sync with IIM; EXIF is stale)
3. If digest mismatches: IIM wins over XMP (IIM was modified more recently);
   but IIM also wins over EXIF (EXIF is the least authoritative for text
   fields)
4. EXIF is only used when both XMP and IIM are absent

### When a Field Exists in IIM but Not XMP

This means either the file has no XMP packet at all, or the XMP packet
exists but lacks that specific field. The MWG treats these differently:

- **No XMP packet:** All IIM values are authoritative (no XMP to conflict)
- **XMP packet exists, field absent:** The field was intentionally not
  included in XMP. If IPTCDigest matches, the IIM value should be promoted
  to XMP. If IPTCDigest mismatches, the IIM value takes precedence.

### When IIM Field Exceeds XMP Value Length

IPTC IIM has field length limits (e.g., Caption-Abstract: 2000 chars). If
the XMP value exceeds this limit, the IIM value will be a truncated version.
The predicted-value comparison accounts for truncation: if the predicted IIM
value (truncated XMP) matches the actual IIM value, they are considered in
sync.

---

## Cross-References

- [overlapping-fields.md](overlapping-fields.md) — Complete field mapping
  tables for all overlapping fields
- [imageio-behavior.md](imageio-behavior.md) — How Apple ImageIO implements
  MWG-like behavior
- [pitfalls.md](pitfalls.md) — Common problems with metadata reconciliation
- [../exif/xmp-mapping.md](../exif/xmp-mapping.md) — EXIF-to-XMP standard
  mapping
