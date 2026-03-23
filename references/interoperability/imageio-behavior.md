# Apple ImageIO Cross-Standard Behavior

> Part of [Interoperability Reference](README.md)

How Apple's ImageIO framework handles the interaction between its two metadata
APIs (property dictionaries and XMP tree), cross-standard auto-synthesis,
and conflict resolution. Most of this behavior is **observed but not
documented by Apple as a guaranteed contract** — re-validate on your target
OS versions.

---

## The Two Metadata APIs

ImageIO exposes metadata through two parallel APIs that are not fully
independent:

| API | Read Function | Write Function | Scope |
|-----|--------------|---------------|-------|
| **Property Dictionaries** | `CGImageSourceCopyPropertiesAtIndex` | `CGImageDestinationAddImage` | EXIF, TIFF, GPS, IPTC IIM, format-specific |
| **XMP Metadata Tree** | `CGImageSourceCopyMetadataAtIndex` | `CGImageDestinationAddImageAndMetadata` | Any XMP namespace |

### Bridge Functions

Two functions explicitly connect the two APIs:

| Function | Direction | Purpose |
|----------|-----------|---------|
| `CGImageMetadataCopyTagMatchingImageProperty` | Property dict key -> XMP tag | Read: find XMP tag corresponding to a property dict key |
| `CGImageMetadataSetValueMatchingImageProperty` | Property dict naming -> XMP | Write: set XMP value using property dict key names |

These bridge functions use Apple's internal mapping tables to translate
between property dictionary keys (e.g., `kCGImagePropertyExifDictionary` +
`kCGImagePropertyExifDateTimeOriginal`) and their XMP equivalents (e.g.,
`exif:DateTimeOriginal`).

### Bridge Function Mapping Coverage

Not all property dictionary keys have XMP equivalents. The bridge functions
cover:

| Property Dictionary | Mapped to XMP Namespace | Coverage |
|--------------------|------------------------|----------|
| `kCGImagePropertyExifDictionary` | `exif:` | Most tags mapped |
| `kCGImagePropertyExifAuxDictionary` | `aux:` | All tags mapped |
| `kCGImagePropertyTIFFDictionary` | `tiff:` | Key tags mapped (Make, Model, Orientation, Software, Artist, Copyright, ImageDescription, DateTime) |
| `kCGImagePropertyGPSDictionary` | `exif:GPS*` | Major GPS fields mapped |
| `kCGImagePropertyIPTCDictionary` | `photoshop:`, `dc:`, `Iptc4xmpCore:` | Most IPTC fields mapped |
| Format-specific dictionaries (JFIF, PNG, GIF, etc.) | None | **Not mapped** — format-specific properties have no XMP equivalents |
| MakerNote dictionaries | None | **Not mapped** — proprietary data has no XMP representation |

---

## Auto-Synthesis on Read

When reading an image, ImageIO synthesizes metadata across APIs so that
either read path sees data from both sources. This is not documented by
Apple as a contract but is consistently observed behavior.

### IPTC IIM -> Synthesized XMP

An image containing only IPTC IIM data (no XMP packet) will return:

- **Via property dictionaries:** IPTC IIM values in
  `kCGImagePropertyIPTCDictionary` as expected.
- **Via XMP tree:** Synthetic XMP tags for the corresponding IPTC fields.
  Specifically:
  - IPTC Caption-Abstract becomes `dc:description` with proper `langAlt`
    structure (`x-default` variant)
  - IPTC Keywords become `dc:subject` as `rdf:Bag`
  - IPTC By-line becomes `dc:creator` as `rdf:Seq`
  - IPTC ObjectName becomes `dc:title` as `langAlt`
  - IPTC CopyrightNotice becomes `dc:rights` as `langAlt`
  - IPTC City/State/Country become `photoshop:City`/`photoshop:State`/
    `photoshop:Country`
  - IPTC CountryCode becomes `Iptc4xmpCore:CountryCode`
  - IPTC Sub-location becomes `Iptc4xmpCore:Location`

### XMP -> Synthesized IPTC IIM

An image containing only XMP data (no IPTC IIM block) will return:

- **Via XMP tree:** XMP tags as expected.
- **Via property dictionaries:** Synthesized IPTC IIM values in
  `kCGImagePropertyIPTCDictionary`. For example:
  - `dc:description` (`x-default` value) appears as IPTC Caption-Abstract
  - `dc:subject` bag elements appear as IPTC Keywords array
  - `dc:creator` sequence elements appear as IPTC By-line array
  - `photoshop:City` appears as IPTC City

### EXIF <-> XMP Synthesis

Similarly, EXIF binary data is synthesized to XMP and vice versa:

- An image with only EXIF data returns synthetic `exif:*` and `tiff:*`
  XMP tags via the XMP tree API.
- An image with only XMP `exif:*` tags returns synthesized EXIF property
  dictionary values.

### GPS <-> XMP Synthesis

- EXIF GPS IFD data (absolute values + reference letters) is synthesized to
  XMP GPS tags (`exif:GPSLatitude`, etc.) in DMS format.
- XMP GPS tags are synthesized to property dictionary GPS values.

### What This Means for Developers

**You do not need to read both APIs to get complete metadata.** Either
`CGImageSourceCopyPropertiesAtIndex` or `CGImageSourceCopyMetadataAtIndex`
will return a view of all metadata present in the file, regardless of which
binary format it was originally stored in.

However, the synthesized values may differ slightly from the originals due
to type coercion (see below).

---

## Auto-Synthesis Type Coercion

When synthesizing across APIs, Apple performs type conversions that may
subtly change values:

| From | To | Coercion | Reversible? |
|------|----|----------|-------------|
| EXIF Rational (e.g., `28/10`) | XMP string | `"28/10"` (rational string) | Yes |
| XMP rational string `"28/10"` | EXIF property dict | `2.8` (CFNumber) | Lossy (denominator lost) |
| IPTC string (single value) | XMP `langAlt` | `{"x-default": "value"}` | Yes |
| XMP `langAlt` `{"x-default": "value", "de": "Wert"}` | IPTC string | `"value"` (only x-default) | Lossy (other langs lost) |
| IPTC repeating datasets | XMP `rdf:Bag` or `rdf:Seq` | Array of strings | Yes |
| XMP `rdf:Bag` | IPTC repeating datasets | Multiple dataset records | Yes |
| EXIF GPS DMS rationals + Ref | XMP GPS string | `"DDD,MM,SS.SSK"` format | Yes |
| XMP GPS DMS string | EXIF property dict | Decimal CFNumber + Ref string | Precision may change |
| EXIF DateTime `"YYYY:MM:DD HH:MM:SS"` | XMP Date | ISO 8601 format | Yes |
| XMP ISO 8601 Date | EXIF DateTime | `"YYYY:MM:DD HH:MM:SS"` (TZ stripped) | Lossy (timezone lost if no OffsetTime) |
| EXIF Flash bitfield (uint16) | XMP Flash structure | Named fields (Fired, Return, Mode, etc.) | Yes |
| XMP Flash structure | EXIF Flash bitfield | Reconstructed uint16 | Yes |

### Precision Loss Examples

```swift
// EXIF stores FNumber as RATIONAL 28/10
// Synthesized XMP: "28/10" (exact)
// Read back as property dict: 2.8 (CFNumber Double — denominator lost)

// XMP stores dc:description with langAlt {"x-default": "English", "de": "Deutsch"}
// Synthesized IPTC Caption-Abstract: "English" (German variant lost)

// XMP stores photoshop:DateCreated "2024-06-15T14:30:00+05:30"
// Synthesized EXIF DateTimeOriginal: "2024:06:15 14:30:00" (timezone in separate tag)
```

---

## Writing Behavior

### CGImageDestinationAddImage (Re-encoding Write)

When writing with property dictionaries via `CGImageDestinationAddImage`:

- The provided property dictionary values are written to the appropriate
  binary segments (EXIF APP1, IPTC APP13, TIFF header, etc.).
- **XMP is also generated** from the property dictionary values. The output
  file will contain both binary metadata and an XMP packet.
- Property dict values **override** any values read from a source image.
  Unspecified keys are not preserved from the source (this is a new image
  write, not a merge).

### CGImageDestinationAddImageAndMetadata (Re-encoding Write with XMP)

When writing with XMP tree via `CGImageDestinationAddImageAndMetadata`:

- The provided `CGImageMetadata` XMP tree is embedded in the output.
- **Binary segments are also generated** from the XMP values where mappings
  exist. EXIF, TIFF, GPS, and IPTC IIM binary data is synthesized from XMP.
- The XMP tree takes precedence if both XMP and a property dictionary are
  provided (via the options parameter).

### CGImageDestinationCopyImageSource (Lossless Metadata Update)

This is the most complex writing path and the most relevant for metadata
interoperability.

**Supported formats:** JPEG, PNG, TIFF, PSD only. HEIC/HEIF requires
re-encoding via `AddImage` or `AddImageAndMetadata`.

#### Merge Mode (`kCGImageDestinationMergeMetadata: true`)

| Component | Behavior |
|-----------|----------|
| Written XMP tags | Updated to new values |
| Unwritten XMP tags | Preserved from source |
| IPTC IIM | **Regenerated** entirely from final merged XMP state |
| EXIF/TIFF/GPS binary | Preserved from source (not regenerated from XMP) |

**Critical implications:**

1. In merge mode, IPTC IIM is rebuilt entirely from the final XMP state. If
   a field exists in old IPTC IIM but has no corresponding XMP tag in the
   merged result, that IPTC IIM field is **lost**. Apple does not merge
   IPTC IIM separately from XMP.

2. Because EXIF/TIFF/GPS binary is preserved from the source (not
   regenerated from XMP), writing an XMP `exif:*` tag does NOT update the
   corresponding EXIF binary value. To update EXIF binary values, you need
   a separate write pass via property dictionaries.

3. Tag removal via `CGImageMetadataRemoveTagWithPath` does **not** work in
   merge mode. Removed tags reappear from the source. Use
   `CGImageMetadataSetValueWithPath(..., kCFNull)` to actively remove a tag.

#### Replace Mode (`kCGImageDestinationMergeMetadata: false`)

| Component | Behavior |
|-----------|----------|
| Written XMP tags | Written to output |
| Unwritten XMP tags | **Stripped** |
| IPTC IIM | Regenerated from written XMP only |
| EXIF/TIFF/GPS binary | **Stripped** |

Replace mode is highly destructive. It strips EXIF, TIFF, and GPS binary
segments in addition to unwritten XMP. It is essentially a metadata reset.
Only use when intentionally overwriting all metadata.

#### XMP -> Binary Sync Table (CopyImageSource)

When `CopyImageSource` regenerates binary segments from XMP:

| XMP Source | Binary Destination | Type Coercion |
|------------|-------------------|---------------|
| `photoshop:*` fields (City, Headline, Credit, etc.) | `kCGImagePropertyIPTCDictionary` | String -> String |
| `Iptc4xmpCore:*` fields (Location, CountryCode, etc.) | `kCGImagePropertyIPTCDictionary` | String -> String |
| `dc:subject` (bag) | `kCGImagePropertyIPTCDictionary` Keywords | Bag elements -> repeating datasets |
| `dc:creator` (seq) | `kCGImagePropertyIPTCDictionary` By-line | Seq elements -> repeating datasets |
| `dc:title` (langAlt) | `kCGImagePropertyIPTCDictionary` ObjectName | x-default extracted |
| `dc:description` (langAlt) | `kCGImagePropertyIPTCDictionary` Caption-Abstract | x-default extracted |
| `dc:rights` (langAlt) | `kCGImagePropertyIPTCDictionary` CopyrightNotice | x-default extracted |
| `exif:*` fields (FNumber, ExposureTime, etc.) | `kCGImagePropertyExifDictionary` | Rational strings -> numeric (e.g., `"28/10"` -> `2.8`) |
| `tiff:*` fields (Make, Model, Orientation, etc.) | `kCGImagePropertyTIFFDictionary` | String/rational -> appropriate type |
| `exif:GPS*` fields | `kCGImagePropertyGPSDictionary` | DMS format -> decimal + reference |
| `aux:*` fields (LensModel, SerialNumber) | `kCGImagePropertyExifAuxDictionary` | Requires explicit namespace registration |

#### What Does NOT Sync (Known Gaps)

| XMP Field | Issue | Workaround |
|-----------|-------|------------|
| `photoshop:DateCreated` | ISO 8601 format NOT converted to IPTC IIM `YYYYMMDD` + `HHMMSS±HHMM` | Write IIM date fields separately via property dictionaries |
| `photoshop:LegacyIPTCDigest` | Not updated by ImageIO (digest is not maintained) | Compute and write digest manually, or accept stale digest |
| `kCGImageProperty8BIMDictionary` | Not created from `photoshop:*` namespace writes | Write 8BIM properties separately if needed |
| MakerNote dictionaries | Not created from any XMP writes | MakerNote is read-only; cannot be recreated from XMP |
| EXIF binary in merge mode | Not regenerated from XMP (preserved from source) | Use property dictionaries for EXIF binary updates |

---

## Conflict Resolution on Read

When the same field has different values in EXIF, IPTC IIM, and XMP within
the same file, ImageIO's observed behavior differs between the two APIs:

### Property Dictionary API

`CGImageSourceCopyPropertiesAtIndex` returns separate dictionaries for each
standard. There is **no automatic reconciliation** — you get the EXIF value
in the EXIF dictionary and the IPTC value in the IPTC dictionary
simultaneously. If they conflict, the application must decide which to prefer.

```swift
let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any]
let exifArtist = (props?[kCGImagePropertyTIFFDictionary as String] as? [String: Any])?["Artist"]
let iptcByline = (props?[kCGImagePropertyIPTCDictionary as String] as? [String: Any])?["Byline"]
// exifArtist and iptcByline may be different!
```

### XMP Tree API

`CGImageSourceCopyMetadataAtIndex` returns a unified XMP view. When both
binary data and an XMP packet exist:

- **XMP packet values take precedence** for XMP-native namespaces
- For synthesized tags (e.g., IPTC-only data promoted to XMP when no XMP
  packet exists), the synthesized values reflect the binary source
- If an XMP packet exists AND binary data exists AND they conflict, the
  XMP packet values win

### No IPTCDigest Check

Unlike MWG-conformant applications, ImageIO does **not** check
`photoshop:LegacyIPTCDigest` to determine sync status between XMP and IPTC
IIM. Its synthesis behavior is based on presence/absence of data, not digest
validation. This means:

- ImageIO cannot detect when a non-MWG tool has updated IPTC IIM without
  updating XMP
- In such cases, ImageIO will serve the XMP value (which may be stale)
  rather than the newer IPTC IIM value
- This is the correct behavior most of the time but can produce incorrect
  results for files edited by IPTC-only tools

---

## Lossless Metadata Update Details

### Supported Formats

| Format | Lossless Update | Notes |
|--------|----------------|-------|
| JPEG | Yes | Full support via `CopyImageSource` |
| PNG | Yes | Full support via `CopyImageSource` |
| TIFF | Yes | Full support via `CopyImageSource` |
| PSD | Yes | Full support via `CopyImageSource` |
| HEIC/HEIF | **No** | Must re-encode via `AddImage` or `AddImageAndMetadata` |
| WebP | **No** | Read-only in ImageIO (no write support at all) |
| DNG | **No** | Must re-encode |
| AVIF | **No** | Read-only or limited write |

### What Gets Regenerated During Lossless JPEG Update

When `CopyImageSource` performs a lossless metadata update on JPEG:

1. **JPEG scan data** (pixel payload) is copied byte-for-byte. No
   decompression or recompression occurs.
2. **XMP APP1 segment** is replaced with the new XMP packet (the merged
   or replaced result).
3. **IPTC IIM APP13 segment** is **regenerated** from the final XMP state.
   The old IPTC IIM segment is discarded.
4. **EXIF APP1 segment** handling depends on merge/replace mode:
   - Merge: EXIF preserved from source (byte-for-byte copy)
   - Replace: EXIF stripped entirely
5. **JFIF APP0 segment** is preserved from source.
6. **ICC profile APP2 segment** is preserved from source.
7. **JPEG comment (COM) marker** is preserved from source.
8. **Thumbnail** is preserved from source (within EXIF APP1).

### What Gets Regenerated During Lossless TIFF Update

TIFF is more complex because metadata and pixel data are interleaved in the
IFD structure:

1. **Pixel strip/tile data** is copied byte-for-byte.
2. **IFD entries** are rebuilt to incorporate new metadata.
3. **XMP** is embedded as a TIFF tag (XMP tag 700).
4. **IPTC IIM** is embedded as a TIFF tag (IPTC tag 33723), regenerated
   from XMP.
5. **EXIF sub-IFD** handling follows merge/replace rules.

### Mutual Exclusivity: DateTime/Orientation vs Metadata

`kCGImageDestinationDateTime` and `kCGImageDestinationOrientation` are
**mutually exclusive** with `kCGImageDestinationMetadata`. If you provide
`kCGImageDestinationMetadata` in the options dictionary, you cannot also
use `kCGImageDestinationDateTime` or `kCGImageDestinationOrientation` in
the same call. Use separate `CopyImageSource` calls, or set the datetime
and orientation via XMP tags within the metadata object.

---

## ImageIO Regeneration Behavior: IPTC IIM Creation

An important difference from MWG guidelines: ImageIO's `CopyImageSource`
will regenerate an IPTC IIM block from XMP **regardless of whether the
original file contained IPTC IIM**. The MWG says "don't create IIM if it
didn't exist," but ImageIO creates it whenever XMP contains fields that
map to IIM datasets.

This means:
- A JPEG with only XMP metadata, processed through `CopyImageSource` with
  merge mode, will gain an IPTC IIM APP13 segment in the output.
- A HEIC converted to JPEG via `AddImageAndMetadata` will have IPTC IIM
  synthesized from XMP, even though HEIC has no concept of IPTC IIM.

This is generally harmless (more metadata locations = more compatibility)
but differs from strict MWG conformance.

---

## Testing Methodology

To verify ImageIO's cross-standard behavior on your target OS:

### Test 1: Read Synthesis (IIM -> XMP)

```swift
// Create a JPEG with ONLY IPTC IIM (no XMP) using ExifTool:
//   exiftool -XMP:all= -IPTC:Caption-Abstract="Test caption" photo.jpg

let source = CGImageSourceCreateWithURL(url as CFURL, nil)!

// Check property dict — should have IPTC
let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any]
let iptc = props?[kCGImagePropertyIPTCDictionary as String] as? [String: Any]
print("IPTC Caption:", iptc?["Caption-Abstract"])  // Should exist

// Check XMP tree — should have synthesized dc:description
let metadata = CGImageSourceCopyMetadataAtIndex(source, 0, nil)!
let desc = CGImageMetadataCopyStringValueWithPath(metadata, nil, "dc:description" as CFString)
print("XMP dc:description:", desc)  // Should exist via synthesis
```

### Test 2: Read Synthesis (XMP -> IIM)

```swift
// Create a JPEG with ONLY XMP (no IPTC IIM) using ExifTool:
//   exiftool -IPTC:all= -XMP:Description="Test description" photo.jpg

let source = CGImageSourceCreateWithURL(url as CFURL, nil)!

// Check XMP tree — should have dc:description
let metadata = CGImageSourceCopyMetadataAtIndex(source, 0, nil)!
let desc = CGImageMetadataCopyStringValueWithPath(metadata, nil, "dc:description" as CFString)
print("XMP dc:description:", desc)  // Should exist

// Check property dict — should have synthesized IPTC
let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any]
let iptc = props?[kCGImagePropertyIPTCDictionary as String] as? [String: Any]
print("Synthesized IPTC Caption:", iptc?["Caption-Abstract"])  // Should exist
```

### Test 3: Write Sync (XMP -> IPTC IIM via CopyImageSource)

```swift
let source = CGImageSourceCreateWithURL(inputURL as CFURL, nil)!
let dest = CGImageDestinationCreateWithURL(outputURL as CFURL, kUTTypeJPEG, 1, nil)!

let xmp = CGImageMetadataCreateMutable()
CGImageMetadataSetValueWithPath(xmp, nil, "dc:description" as CFString, "Test" as CFString)

let options: [CFString: Any] = [
    kCGImageDestinationMetadata: xmp,
    kCGImageDestinationMergeMetadata: kCFBooleanTrue!
]
var error: Unmanaged<CFError>?
CGImageDestinationCopyImageSource(dest, source, options as CFDictionary, &error)

// Read back and check IPTC
let outSource = CGImageSourceCreateWithURL(outputURL as CFURL, nil)!
let outProps = CGImageSourceCopyPropertiesAtIndex(outSource, 0, nil) as? [String: Any]
let outIptc = outProps?[kCGImagePropertyIPTCDictionary as String] as? [String: Any]
print("Output IPTC Caption:", outIptc?["Caption-Abstract"])  // Should exist
```

### Test 4: Date Sync Gap

```swift
// Write photoshop:DateCreated via XMP
let xmp = CGImageMetadataCreateMutable()
CGImageMetadataSetValueWithPath(xmp, nil,
    "photoshop:DateCreated" as CFString,
    "2024-06-15T14:30:00+05:30" as CFString)

// ... write via CopyImageSource and read back ...
// IPTC DateCreated will likely be absent (known sync gap)
// IPTC TimeCreated will also be absent
```

### Test 5: Merge Mode EXIF Preservation

```swift
// Verify that EXIF binary is preserved (not regenerated) in merge mode
// Write an XMP exif:FNumber value that differs from the EXIF binary FNumber
let xmp = CGImageMetadataCreateMutable()
CGImageMetadataSetValueWithPath(xmp, nil,
    "exif:FNumber" as CFString,
    "56/10" as CFString)  // f/5.6

// ... write via CopyImageSource merge mode ...
// EXIF binary FNumber should still be the original value
// XMP exif:FNumber should be "56/10"
// This demonstrates that merge mode does NOT regenerate EXIF from XMP
```

---

## Comparison: ImageIO vs ExifTool

| Behavior | ImageIO | ExifTool (with MWG) | ExifTool (default) |
|----------|---------|--------------------|--------------------|
| Read synthesis | Auto-synthesis between APIs | MWG Composite tags reconcile | Reads each tag independently |
| IPTCDigest check | No | Yes (validates sync) | Only reads, does not validate |
| Write sync | XMP -> IPTC IIM regeneration | Updates all locations explicitly | Writes to specified location only |
| IPTCDigest update | No | Yes (automatic) | Not maintained |
| Date format sync | Gap (ISO 8601 not -> IIM format) | Full conversion | Full conversion |
| Multi-value Creator | Array handling (no semicolon convention) | Semicolon convention in EXIF | No convention enforced |
| IPTC IIM creation | Creates from XMP regardless | Only if IIM already exists (strict) | Only if specified |
| Strict conformance | No | Yes (when MWG module loaded) | No |
| Default write target | XMP (with binary regeneration) | EXIF first, then IPTC, then XMP | Specified location |
| langAlt handling | Bug: TagCreate alternateText silently dropped | Full support | Full support |
| EXIF binary update via XMP | No (merge mode preserves source) | N/A (writes directly) | N/A |

### Key Practical Differences

1. **A file written by ImageIO** may have XMP and regenerated IPTC IIM but
   no IPTCDigest. ExifTool with MWG will treat the absent digest as "prefer
   XMP" — which is usually correct.

2. **A file written by ExifTool** (without MWG) may have IPTC IIM as the
   primary metadata location with no XMP. ImageIO will synthesize XMP on
   read, so this works seamlessly.

3. **Files with Latin-1 IPTC** (from older tools) will read correctly in
   ExifTool (which checks CodedCharacterSet) but may show garbled text in
   ImageIO (which assumes UTF-8).

4. **Files with conflicting EXIF and IPTC** (edited by an IPTC-only tool):
   ExifTool with MWG detects this via IPTCDigest and prefers the newer IPTC
   values. ImageIO does not check the digest and may serve stale XMP values.

---

## Recommendations for iOS Developers

1. **Use the XMP tree API (`CGImageMetadata`) as your primary write path.**
   ImageIO's `CopyImageSource` will regenerate IPTC IIM from XMP
   automatically. This gives you the broadest compatibility with one write.

2. **Do not rely on IPTC IIM date sync.** If IPTC IIM date compatibility
   is required (e.g., for wire service workflows), write IPTC date fields
   explicitly via property dictionaries in a separate pass.

3. **Read from either API.** Auto-synthesis means property dictionaries and
   XMP tree both see all metadata. Use whichever is more convenient:
   - Property dictionaries for quick access to common fields (EXIF, GPS)
   - XMP tree for IPTC Core/Extension, Dublin Core, custom namespaces

4. **Validate on your target OS.** Auto-synthesis is observed behavior, not
   a documented contract. Test with images containing metadata in only one
   standard to verify synthesis works as expected on your minimum deployment
   target.

5. **Prefer merge mode for metadata updates.** Replace mode strips
   EXIF/TIFF/GPS binary data, which is rarely desired.

6. **Handle the `langAlt` write bug.** Tags created with
   `CGImageMetadataTagCreate(.alternateText, ...)` are silently dropped by
   `CopyImageSource`. Use `SetValueWithPath` with a plain string instead.
   See [../imageio/cgimage-metadata.md](../imageio/cgimage-metadata.md).

7. **Use `kCFNull` for tag removal in merge mode.** `RemoveTagWithPath`
   does not persist through `CopyImageSource` merge mode.

8. **For complete MWG conformance, supplement ImageIO with manual logic:**
   - Compute and write IPTCDigest after IPTC IIM modifications
   - Implement EXIF Artist semicolon convention for multi-value creators
   - Convert ISO 8601 dates to IPTC IIM format for date fields
   - Check IPTCDigest on read to detect IPTC-only edits

---

## Cross-References

- [../imageio/README.md](../imageio/README.md) — Two-API overview
- [../imageio/cgimage-metadata.md](../imageio/cgimage-metadata.md) — XMP tree
  API details, bridge functions, langAlt bug
- [../imageio/cgimagedestination.md](../imageio/cgimagedestination.md) — Write
  behavior, merge vs replace, option keys
- [../imageio/pitfalls.md](../imageio/pitfalls.md) — UIImage metadata loss,
  orientation, GPS, threading
- [mwg-guidelines.md](mwg-guidelines.md) — MWG reconciliation rules
- [overlapping-fields.md](overlapping-fields.md) — Field mapping tables
