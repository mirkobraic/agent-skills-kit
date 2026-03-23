# TIFF Metadata Pitfalls

> Part of [TIFF Reference](README.md)

> **Guidance, not absolute truth.** The pitfalls below are based on observed
> behavior and community knowledge at the time of writing. Edge cases may vary
> by format, device, or software. Treat these as starting points for
> investigation -- always verify and test with real images before relying on any
> assumption documented here.

Known issues, gotchas, and edge cases when working with TIFF metadata in the
Apple ecosystem. Each pitfall includes a description, why it matters, and how
to handle it correctly.

---

## Orientation Duplication

**The problem:** Orientation exists in two places in ImageIO's property
dictionary:

1. `kCGImagePropertyTIFFOrientation` -- inside the TIFF dictionary
2. `kCGImagePropertyOrientation` -- at the top level

Both hold the same 1-8 EXIF orientation value and should always agree. When
reading, ImageIO populates both from the same IFD0 tag. But when writing,
setting one does not guarantee the other is updated.

**Impact:** If the values disagree, different code paths may interpret the
orientation differently, causing images to display rotated or flipped.
Specifically:
- `CGImageSourceCreateThumbnailWithTransform` reads the **top-level** value
- Manual rotation code may read the **TIFF dictionary** value
- Third-party libraries may read either one

**Solution:**

```swift
// Always set both when writing orientation
let orientation = 6 // 90 CW (portrait)

let properties: [String: Any] = [
    kCGImagePropertyOrientation as String: orientation,
    kCGImagePropertyTIFFDictionary as String: [
        kCGImagePropertyTIFFOrientation as String: orientation
    ]
]
```

**Additional risk -- UIImage.Orientation confusion:**

`CGImagePropertyOrientation` (EXIF numbering, 1-8) and
`UIImage.Orientation` (UIKit numbering, different raw values) are **not**
interchangeable. See [`imageio-mapping.md`](imageio-mapping.md#cgimagepropertyorientation-vs-uiimageorientation)
for the full mapping table. Converting a `UIImage` to `CGImage` and writing
metadata without correcting orientation is a common source of bugs.

---

## DateTime Has No Timezone

**The problem:** TIFF DateTime (`"YYYY:MM:DD HH:MM:SS"`) has **no timezone
information**. The exact same format is used by EXIF's DateTimeOriginal and
DateTimeDigitized. A timestamp of `"2025:03:15 14:30:22"` is ambiguous -- it
could be in any timezone.

**Impact:** Sorting photos by date, synchronizing across time zones, or
displaying "taken at" times can be wrong by hours. A photo taken at 2:30 PM
in New York and a photo taken at 2:30 PM in Tokyo will appear to be at the
same time if you only read DateTime.

**Solution:** Always check for EXIF 2.31+ OffsetTime tags:

```swift
let tiff = properties[kCGImagePropertyTIFFDictionary as String] as? [String: Any]
let exif = properties[kCGImagePropertyExifDictionary as String] as? [String: Any]

let dateTime = tiff?[kCGImagePropertyTIFFDateTime as String] as? String
// "2025:03:15 14:30:22"

let offset = exif?[kCGImagePropertyExifOffsetTime as String] as? String
// "-05:00" (if present -- iPhone always writes this; many cameras do not)
```

**Which devices write OffsetTime?**

| Device/Software | Writes OffsetTime? | Notes |
|-----------------|-------------------|-------|
| iPhone (all models) | Yes | Always writes all three offset tags |
| iPad (with camera) | Yes | Same behavior as iPhone |
| Canon (recent models) | Some | EOS R-series may write it; older models do not |
| Nikon (recent models) | Some | Z-series may write it; older models do not |
| Sony (recent models) | Some | Newer firmware may include it |
| Adobe Lightroom | Yes | Writes offset tags when exporting |
| Most older cameras | No | EXIF 2.31 (2016) adoption is still incomplete |

If OffsetTime is absent, the timestamp is in the photographer's local time
at capture -- but you have no way to determine what timezone that was
without external information (such as GPS coordinates).

**Workaround for missing OffsetTime:**

```swift
// If GPS data is available, you can approximate the timezone
// from the GPS coordinates using TimeZone(identifier:) or a
// timezone lookup library. This is imprecise but better than nothing.
func approximateTimezone(latitude: Double, longitude: Double) -> TimeZone? {
    // Use CLGeocoder or a timezone database lookup
    // This is a network call and should be done asynchronously
    return nil // placeholder
}
```

---

## Make/Model Encoding (ASCII Only)

**The problem:** TIFF defines Make and Model as ASCII type (7-bit characters
only). Camera manufacturer names and model names with non-ASCII characters
(e.g., accented letters, CJK characters) cannot be properly stored.

**Impact:** Names containing non-ASCII characters may be truncated, garbled,
or rejected by strict TIFF parsers.

**Workaround:** EXIF 3.0 introduced the UTF-8 data type (type 129) for
certain tags (ImageTitle, Photographer, ImageEditor, CameraFirmware, etc.),
but Make and Model remain ASCII-only even in EXIF 3.0. For non-ASCII creator
names, use the EXIF 3.0 `Photographer` tag (0xA437) or XMP `dc:creator`.

**In practice:** This is rarely a problem because camera manufacturers use
ASCII-compatible names. However, tools that inject metadata should validate
that ASCII-only fields actually contain only ASCII characters.

**Affected tags (all ASCII-only in TIFF 6.0 and EXIF 3.0):**

| Tag | ASCII-Only? | Alternative for Unicode |
|-----|------------|------------------------|
| Make (0x010F) | Yes | XMP `tiff:Make` (natively Unicode) |
| Model (0x0110) | Yes | XMP `tiff:Model` |
| Software (0x0131) | Yes | XMP `tiff:Software` |
| Artist (0x013B) | Yes | EXIF 3.0 `Photographer` (0xA437), XMP `dc:creator` |
| Copyright (0x8298) | Yes | XMP `dc:rights` |
| ImageDescription (0x010E) | Yes | EXIF 3.0 `ImageTitle` (0xA436), XMP `dc:description` |
| DocumentName (0x010D) | Yes | XMP (custom namespace) |
| HostComputer (0x013C) | Yes | No standard alternative |
| DateTime (0x0132) | Yes | N/A (format is inherently ASCII) |

---

## Artist vs IPTC Byline vs XMP dc:creator

**The problem:** Three different metadata standards store the image creator:

| Standard | Field | Key / Path |
|----------|-------|-----------|
| TIFF/EXIF | Artist | `kCGImagePropertyTIFFArtist` |
| IPTC IIM | By-line | `kCGImagePropertyIPTCByline` |
| XMP | dc:creator | XMP ordered array |

These can have different values in the same file if software writes to one
but not the others.

**MWG Reconciliation:**

The Metadata Working Group (MWG) specifies reading precedence:

1. **XMP `dc:creator`** -- preferred source
2. **IPTC By-line** -- fallback
3. **EXIF Artist** -- last resort

When writing, update all three to keep them in sync.

**Additional complication:** EXIF Artist is a single ASCII string. XMP
`dc:creator` is an ordered array (supports multiple creators). IPTC By-line
also supports multiple values. The MWG recommends joining multiple values
with `"; "` (semicolon-space) when writing to the EXIF Artist tag.

```swift
// Writing creator to all three locations
let creators = ["Jane Smith", "John Doe"]

let properties: [String: Any] = [
    kCGImagePropertyTIFFDictionary as String: [
        // EXIF Artist: single string, semicolon-separated
        kCGImagePropertyTIFFArtist as String: creators.joined(separator: "; ")
    ],
    kCGImagePropertyIPTCDictionary as String: [
        // IPTC By-line: array of strings
        kCGImagePropertyIPTCByline as String: creators
    ]
]

// Also set XMP dc:creator via CGImageMetadata API:
let metadata = CGImageMetadataCreateMutable()
let tag = CGImageMetadataTagCreate(
    "http://purl.org/dc/elements/1.1/" as CFString,  // Dublin Core namespace
    "dc" as CFString,                                  // prefix
    "creator" as CFString,                             // name
    .arrayOrdered,                                     // ordered array
    creators as CFArray                                // value
)
if let tag = tag {
    CGImageMetadataSetTagWithPath(metadata, nil, "dc:creator" as CFString, tag)
}
```

---

## Copyright vs IPTC CopyrightNotice vs XMP dc:rights

**The problem:** Copyright information exists in three places:

| Standard | Field | Key / Path |
|----------|-------|-----------|
| TIFF/EXIF | Copyright | `kCGImagePropertyTIFFCopyright` |
| IPTC IIM | CopyrightNotice | `kCGImagePropertyIPTCCopyrightNotice` |
| XMP | dc:rights | XMP language alternative |

**MWG Reconciliation:**

1. **XMP `dc:rights`** -- preferred source
2. **IPTC CopyrightNotice** -- fallback
3. **EXIF Copyright** -- last resort

**EXIF Copyright format quirk:** The EXIF spec defines a special
photographer/editor format using null-byte separators (see
[`tag-reference.md`](tag-reference.md#copyright)), but ImageIO returns a
single string. The photographer/editor distinction is largely ignored in
modern workflows -- use a single copyright string.

**XMP dc:rights is a language alternative** (`rdf:Alt` with `xml:lang`
attributes), meaning it can store copyright notices in multiple languages.
The TIFF and IPTC fields are plain strings. When synchronizing, use the
`x-default` language entry for conversion.

---

## ImageDescription vs IPTC Caption vs XMP dc:description

**The problem:** Image description/caption exists in three places:

| Standard | Field | Key / Path |
|----------|-------|-----------|
| TIFF/EXIF | ImageDescription | `kCGImagePropertyTIFFImageDescription` |
| IPTC IIM | Caption-Abstract | `kCGImagePropertyIPTCCaptionAbstract` |
| XMP | dc:description | XMP language alternative |

**MWG Reconciliation:**

1. **XMP `dc:description`** -- preferred source
2. **IPTC Caption-Abstract** -- fallback
3. **EXIF ImageDescription** -- last resort

**Complication with XMP:** `dc:description` is a language alternative
(`rdf:Alt` with `xml:lang` attributes), while TIFF ImageDescription and IPTC
Caption-Abstract are plain strings. When converting, the plain string becomes
the `x-default` language entry.

**AI/Accessibility note:** Image descriptions are increasingly used for:
- AI-generated alt text for accessibility
- Image search and categorization
- Photo library organization

If your app writes image descriptions, consider writing to all three
locations for maximum compatibility. New code should prefer the XMP path
(`dc:description`) as it supports Unicode and language alternatives.

---

## Resolution Units

**The problem:** The ResolutionUnit tag has three possible values:

| Value | Unit | Meaning |
|-------|------|---------|
| 1 | No absolute unit | Pixels have no physical size; ratio only |
| 2 | Inch | Pixels per inch (PPI/DPI) |
| 3 | Centimeter | Pixels per centimeter |

**Impact:** Software that assumes ResolutionUnit=2 (inch) without checking
will compute incorrect physical dimensions when the unit is 3 (centimeter)
or meaningless dimensions when the unit is 1.

**Default:** If ResolutionUnit is absent, the default is 2 (inch) per the
TIFF 6.0 specification. Most cameras write ResolutionUnit=2 with
XResolution=YResolution=72 -- this is a legacy convention from early
Macintosh displays (72 PPI) and does not represent the actual sensor density.

**Print resolution:** For print workflows, 300 DPI (ResolutionUnit=2,
XResolution=300, YResolution=300) is standard. Some scanners use
ResolutionUnit=3 with values in pixels per centimeter. Always check the unit
before computing physical dimensions:

```swift
func physicalWidthInInches(
    pixelWidth: Int,
    xResolution: Double,
    resolutionUnit: Int
) -> Double? {
    switch resolutionUnit {
    case 1: return nil  // No physical size
    case 2: return Double(pixelWidth) / xResolution  // Already inches
    case 3: return Double(pixelWidth) / (xResolution * 2.54)  // cm -> inches
    default: return nil
    }
}
```

**Non-square pixels:** If XResolution and YResolution differ, the pixels
are non-square. This is common in anamorphic video frames and some scanner
configurations. Most photo software assumes square pixels and ignores
differing values.

---

## BigTIFF Not Supported

**The problem:** Apple's ImageIO framework does **not** support BigTIFF
(64-bit TIFF). BigTIFF files use magic number 43 (vs. classic TIFF's 42) and
64-bit offsets, allowing files larger than 4 GB.

**Impact:** Attempting to open a BigTIFF file with `CGImageSourceCreateWithURL`
will fail -- `CGImageSourceGetStatus` returns `.statusUnknownType`. This
affects:

- Scientific imaging (microscopy, satellite)
- GIS (geospatial raster data)
- Medical imaging (pathology whole-slide images)
- Any TIFF file exceeding 4 GB

**Detection:**

```swift
func isBigTIFF(at url: URL) -> Bool {
    guard let data = try? Data(contentsOf: url, options: .mappedIfSafe),
          data.count >= 4
    else { return false }

    let byte0 = data[0]
    let byte1 = data[1]

    // Check byte order marker
    guard (byte0 == 0x49 && byte1 == 0x49) ||  // "II" (little-endian)
          (byte0 == 0x4D && byte1 == 0x4D)      // "MM" (big-endian)
    else { return false }

    // Read magic number based on byte order
    if byte0 == 0x49 {  // Little-endian
        return data[2] == 0x2B && data[3] == 0x00  // 43 in LE
    } else {  // Big-endian
        return data[2] == 0x00 && data[3] == 0x2B  // 43 in BE
    }
}
```

**Workaround:** For BigTIFF support on Apple platforms, use a third-party
library such as LibTIFF (via C interop) or a specialized framework. For
typical photography workflows (JPEG, HEIC, standard TIFF), this limitation
is not relevant.

---

## TIFF ASCII Fields and UTF-8

**The problem:** TIFF 6.0 defines all text tags (Make, Model, Software,
Artist, Copyright, ImageDescription, DocumentName, HostComputer, DateTime)
as ASCII type -- strictly 7-bit characters.

**In practice:** Many tools write UTF-8 text into these ASCII fields, and
most readers (including ImageIO) silently accept it. However:

- Strict TIFF validators will flag UTF-8 in ASCII fields as non-conformant
- Some legacy software may truncate at the first non-ASCII byte
- Round-tripping through strict tools may corrupt non-ASCII characters

**Best practice:** Keep TIFF ASCII fields as pure ASCII whenever possible.
For non-ASCII text, use:
- EXIF 3.0 UTF-8 tags (`ImageTitle`, `Photographer`, etc.) -- but adoption
  is still limited
- XMP properties (natively Unicode) -- best cross-platform option
- IPTC IIM with CodedCharacterSet set to UTF-8 -- supported but legacy

**Validation:**

```swift
func isASCIIOnly(_ string: String) -> Bool {
    return string.allSatisfy { $0.isASCII }
}

// Before writing to a TIFF ASCII field:
let artist = "Jose Garcia"
if !isASCIIOnly(artist) {
    // Write to XMP dc:creator instead (or in addition)
    print("Warning: Artist contains non-ASCII characters")
}
```

---

## HostComputer Duplication on iOS

**The problem:** iOS writes the device model name (e.g., `"iPhone 16 Pro"`)
to **both** the Model tag and the HostComputer tag:

| Tag | iOS Value | Intended Purpose (per TIFF spec) |
|-----|-----------|------|
| Make | `"Apple"` | Device manufacturer |
| Model | `"iPhone 16 Pro"` | Device/camera model |
| HostComputer | `"iPhone 16 Pro"` | Computer that created the image |
| Software | `"18.3.2"` | Software/firmware version |

The TIFF spec intended HostComputer for the computer system (e.g.,
`"ENIAC"`, `"macOS 14.3"`, or the workstation name). iOS using it to
duplicate the device model is non-standard but harmless.

**Impact:** Code that reads HostComputer expecting an operating system name
or computer hostname will get a phone model instead. Do not rely on
HostComputer for identifying the OS -- use Software for that on iOS devices.

**Identifying iOS version from metadata:**

```swift
// Software tag contains the iOS version
let software = tiff[kCGImagePropertyTIFFSoftware as String] as? String
// "18.3.2" -- this is the iOS version, not an app name

// To identify the device:
let model = tiff[kCGImagePropertyTIFFModel as String] as? String
// "iPhone 16 Pro" -- use this for device identification
```

---

## Summary Table

| Pitfall | Severity | Key | Workaround |
|---------|----------|-----|-----------|
| Orientation in two places | **High** | Duplication | Set both top-level and TIFF dict when writing |
| DateTime has no timezone | **High** | Ambiguity | Use EXIF OffsetTime* tags; fall back to GPS for timezone |
| Artist/Copyright/Description triplication | **Medium** | Sync | Write to all three (TIFF + IPTC + XMP) per MWG rules |
| ResolutionUnit assumptions | **Medium** | Incorrect | Check unit value before computing physical dimensions |
| ASCII-only text fields | **Low** | Encoding | Use XMP or EXIF 3.0 for Unicode text |
| BigTIFF not supported | **Low** | Compatibility | Use LibTIFF for BigTIFF; rarely affects photography |
| HostComputer duplication on iOS | **Low** | Confusion | Informational; use Model for device, Software for OS version |
| Make/Model ASCII encoding | **Low** | Encoding | Rarely an issue; manufacturers use ASCII names |

### Pitfall Interaction Map

Several pitfalls interact with each other and with pitfalls documented
in other reference sections:

```
Orientation Duplication
  +-- See also: ../exif/orientation.md (values 1-8)
  +-- See also: ../imageio/pitfalls.md (UIImage metadata loss)

DateTime No Timezone
  +-- See also: ../exif/pitfalls.md (DateTime timezone)
  +-- Related: GPS timestamps are always UTC (GPSTimeStamp + GPSDateStamp)

Artist/Copyright/Description Triplication
  +-- See also: ../iptc/ (IPTC IIM fields)
  +-- See also: ../interoperability/ (MWG reconciliation rules)
  +-- XMP is the authoritative source per MWG
```
