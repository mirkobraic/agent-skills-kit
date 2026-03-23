# Interoperability Pitfalls

> Part of [Interoperability Reference](README.md)

Common problems that arise when metadata crosses standard boundaries,
traverses different APIs, or passes through format conversions. These pitfalls
are distinct from single-standard issues (covered in per-standard pitfall
files) and focus on cross-standard and cross-tool interaction problems.

---

## 1. IPTC IIM Charset: Latin-1 vs UTF-8

### The Problem

IPTC IIM text fields do not have a universally enforced encoding. The IIM
specification uses ISO 2022 escape sequences in Dataset 1:90
(CodedCharacterSet) to declare the encoding of subsequent text datasets.

| CodedCharacterSet Value | Encoding | ESC Sequence |
|------------------------|----------|--------------|
| `ESC % G` (hex: `1B 25 47`) | UTF-8 | ISO 2022 designation for UTF-8 |
| Not present | Ambiguous (could be Latin-1, Windows-1252, or platform-default) | -- |
| Other ISO 2022 sequences | Various (ISO 8859 variants, JIS, etc.) | Various |

### How Different Tools Handle This

| Tool | No CodedCharacterSet | With CodedCharacterSet |
|------|---------------------|----------------------|
| **Apple ImageIO** | Assumes UTF-8 | Ignores CodedCharacterSet; still assumes UTF-8 |
| **ExifTool** | Assumes Windows Latin-1 (cp1252) | Respects the declared encoding |
| **Adobe Lightroom** | Checks heuristically | Respects CodedCharacterSet |
| **Adobe Photoshop** | Writes UTF-8 with ESC sequence | Respects CodedCharacterSet |
| **Many older tools** | Write Latin-1 or platform-default | Do not write CodedCharacterSet |

### Impact

A file written by an older Windows tool with Latin-1 IPTC captions
(e.g., `"Caf\xe9"` for "Cafe") will be read by ImageIO as if it were UTF-8.
The single byte `0xe9` is not valid UTF-8 on its own, producing either a
replacement character or garbled multi-byte interpretation.

Real-world example:
```
Latin-1 bytes:    43 61 66 E9           ("Cafe" with e-acute)
ImageIO reads:    43 61 66 EF BF BD     ("Caf" + replacement character)
ExifTool reads:   "Cafe"                (correctly interprets as Latin-1)
```

### Mitigation

1. **For new code:** Always use IPTC via XMP namespaces (`Iptc4xmpCore`,
   `photoshop:`, `dc:`) which are always UTF-8. Avoid writing IPTC IIM
   directly.
2. **When reading legacy files with garbled IPTC text:** Check for invalid
   UTF-8 sequences and attempt re-interpretation as Latin-1:
   ```swift
   let iptcCaption = iptcDict["Caption-Abstract"] as? String
   // If garbled, try re-interpreting raw bytes as Latin-1
   if let data = iptcCaption?.data(using: .utf8),
      !data.isValidUTF8 {
       let latin1 = String(data: data, encoding: .isoLatin1)
   }
   ```
3. **When writing IPTC IIM directly via property dictionaries:** ImageIO
   writes UTF-8 with proper CodedCharacterSet. This is correct for modern
   workflows but may confuse old tools that expect Latin-1.

---

## 2. Metadata Loss Through UIImage

### The Problem

`UIImage` strips almost all metadata when creating an image from data and
re-encoding it. Only orientation survives, and even that is baked into the
pixels rather than preserved as a tag.

### What Survives a UIImage Round-Trip

| Metadata | Preserved? | Details |
|----------|-----------|---------|
| Pixel data | Yes | Re-encoded at specified quality |
| Orientation | Partially | Applied to pixels; EXIF tag reset to 1 (Normal) |
| Color space | Partially | May be converted to sRGB depending on context |
| EXIF | **No** | Camera settings, timestamps, lens info all lost |
| GPS | **No** | Location data lost |
| IPTC IIM | **No** | Caption, keywords, copyright all lost |
| XMP | **No** | All XMP namespaces lost |
| ICC Profile | Partially | sRGB is assumed; wide-gamut profiles may be lost |
| MakerNote | **No** | Vendor-specific data lost |
| Thumbnail | **No** | Embedded EXIF thumbnail lost |
| Depth/Gain map | **No** | Auxiliary data lost |

### The Destructive Pipeline

```swift
// This pipeline destroys ALL metadata except pixel data
let image = UIImage(data: jpegData)        // Step 1: Metadata read internally, not exposed
let newData = image!.jpegData(compressionQuality: 0.8)  // Step 2: New JPEG, no metadata

// Also destructive:
let image = UIImage(contentsOfFile: path)
let image = UIImage(named: "photo")
let renderer = UIGraphicsImageRenderer(size: size)
let renderedData = renderer.jpegData(withCompressionQuality: 0.8) { ctx in
    image.draw(in: rect)  // Metadata lost in the draw
}
```

### Safe Alternative: Metadata-Preserving Pipeline

```swift
// Read metadata and pixels separately
let source = CGImageSourceCreateWithData(jpegData as CFData, nil)!
let metadata = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)!
let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil)!

// Process pixels if needed (e.g., through CIImage filters)
let processedImage = cgImage  // or apply filters

// Write with preserved metadata
let output = NSMutableData()
let dest = CGImageDestinationCreateWithData(output, kUTTypeJPEG, 1, nil)!
CGImageDestinationAddImage(dest, processedImage, metadata)
CGImageDestinationFinalize(dest)
```

### Lossless Metadata-Only Update

If you only need to change metadata (not pixels), use `CopyImageSource`:

```swift
let source = CGImageSourceCreateWithData(jpegData as CFData, nil)!
let output = NSMutableData()
let dest = CGImageDestinationCreateWithData(output, CGImageSourceGetType(source)!, 1, nil)!

let xmp = CGImageMetadataCreateMutable()
CGImageMetadataSetValueWithPath(xmp, nil, "dc:description" as CFString, "New caption" as CFString)

var error: Unmanaged<CFError>?
CGImageDestinationCopyImageSource(dest, source, [
    kCGImageDestinationMetadata: xmp,
    kCGImageDestinationMergeMetadata: kCFBooleanTrue!
] as CFDictionary, &error)
```

---

## 3. Metadata Loss Through CIImage Pipeline

### The Problem

Core Image (`CIImage`) is a recipe-based image processing pipeline. When an
image is loaded into `CIImage`, processed through filters, rendered to
`CGImage`, and converted back, all file-level metadata is lost.

### The Pipeline

```
File data -> CIImage -> CIFilter chain -> CIContext.createCGImage -> CGImage
```

`CIImage.properties` provides a subset of metadata (primarily EXIF and
orientation) but this is:
1. Not automatically carried through the render pipeline
2. Incomplete (missing IPTC, XMP, MakerNote, etc.)
3. Read-only (modifications are not supported)

`CGImage` is a pixel buffer with no metadata attachment.

### Mitigation

```swift
// Step 1: Read metadata BEFORE entering CIImage pipeline
let source = CGImageSourceCreateWithData(data as CFData, nil)!
let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)!
let xmpMetadata = CGImageSourceCopyMetadataAtIndex(source, 0, nil)

// Step 2: Process through Core Image
let ciImage = CIImage(data: data)!
let filtered = ciImage.applyingFilter("CIPhotoEffectNoir")
let context = CIContext()
let cgImage = context.createCGImage(filtered, from: filtered.extent)!

// Step 3: Write with original metadata preserved
let output = NSMutableData()
let dest = CGImageDestinationCreateWithData(output, kUTTypeJPEG, 1, nil)!

// Update modification date to reflect processing
var mutableProps = properties as! [String: Any]
var tiffDict = mutableProps[kCGImagePropertyTIFFDictionary as String] as? [String: Any] ?? [:]
tiffDict[kCGImagePropertyTIFFSoftware as String] = "MyApp 1.0"
mutableProps[kCGImagePropertyTIFFDictionary as String] = tiffDict

CGImageDestinationAddImage(dest, cgImage, mutableProps as CFDictionary)
CGImageDestinationFinalize(dest)
```

---

## 4. Social Media and Messaging Metadata Stripping

### Platform Behavior

| Platform | EXIF Stripped | GPS Stripped | IPTC/XMP Stripped | Notes |
|----------|-------------|-------------|-------------------|-------|
| **Instagram** | Yes | Yes | Yes | Strips all metadata; re-encodes images |
| **Facebook** | Yes | Yes | Yes | Strips from public images; retains internally on servers |
| **Twitter/X** | Mostly | Yes | Yes | Has stripped GPS since 2019; other EXIF partially preserved |
| **WhatsApp (image mode)** | Yes | Yes | Yes | Standard image sharing compresses and strips |
| **WhatsApp (document mode)** | **No** | **No** | **No** | "Send as document" preserves everything |
| **iMessage** | **No** | **No** | **No** | Does not strip metadata at all |
| **Signal** | Yes | Yes | Yes | Strips by default; user setting to preserve |
| **Telegram (image mode)** | Yes | Yes | Yes | Standard sharing strips |
| **Telegram (file mode)** | **No** | **No** | **No** | "Send as file" preserves everything |
| **Slack** | Mostly | Mostly | Mostly | Behavior varies by plan and settings |
| **Discord** | Mostly | Yes | Mostly | Strips GPS; other EXIF may survive |
| **LinkedIn** | Yes | Yes | Yes | Strips all metadata |
| **Google Photos (sharing)** | Mostly | Configurable | Mostly | GPS removal is a sharing setting |

### Privacy Implications

- Apps that strip metadata protect user privacy but destroy provenance
  information (authorship, copyright, creation date).
- **iMessage is a notable exception:** Photos sent via iMessage retain full
  GPS coordinates and all other metadata. This is a significant privacy
  consideration.
- **"Send as Document" modes** in WhatsApp and Telegram preserve all
  metadata including GPS. Users may not realize location data is preserved
  when choosing this option.
- Even when embedded GPS is stripped, platforms may still have location data
  from IP addresses, app telemetry, or manual location tags.

### Impact on Round-Trip Workflows

Images that pass through social media or messaging lose their metadata
permanently. This affects:

- Professional photographers sharing work for review
- News organizations receiving field photos
- Any workflow where metadata provenance matters
- Copyright enforcement (copyright notices stripped)

**Mitigation:** Use sidecar files or out-of-band metadata transfer for
workflows where metadata must survive platform sharing. For iMessage,
consider stripping GPS before sending if privacy is a concern.

---

## 5. XMP Sidecar vs Embedded: Priority Confusion

### The Problem

When an image has both embedded XMP metadata and a `.xmp` sidecar file,
which takes priority? There is no universal standard — behavior is
application-dependent.

### Application Behavior

| Application | Priority | Notes |
|-------------|----------|-------|
| Adobe Lightroom | Catalog > sidecar > embedded | Lightroom uses its own catalog; sidecar for interop |
| Adobe Bridge | Sidecar > embedded (for RAW) | Embedded > sidecar for non-RAW |
| ExifTool | Embedded (default) | Can read sidecar with `-ext xmp` or explicit path |
| Apple Photos | Embedded only | Ignores sidecar files entirely |
| Apple ImageIO | Embedded only | No sidecar awareness in API |
| darktable | Sidecar > embedded | Always creates/reads `.xmp` sidecar files |
| Capture One | Catalog > sidecar > embedded | Similar to Lightroom model |
| digiKam | Database > sidecar > embedded | Uses XMP sidecar as interchange format |

### Mitigation

- When using ImageIO, you must manually read and merge sidecar files:
  ```swift
  let sidecarURL = imageURL.deletingPathExtension().appendingPathExtension("xmp")
  if FileManager.default.fileExists(atPath: sidecarURL.path) {
      let sidecarData = try Data(contentsOf: sidecarURL)
      let sidecarMeta = CGImageMetadataCreateFromXMPData(sidecarData as CFData)
      // Manually merge with embedded metadata
  }
  ```
- Document your application's priority behavior clearly for users.
- For maximum interoperability, keep embedded and sidecar in sync.
- RAW files commonly use sidecar files because the RAW file itself should
  not be modified. Your app should expect sidecar files alongside RAW
  formats (`.cr2`, `.nef`, `.arw`, `.dng`).

---

## 6. Orientation Inconsistency Across Apps

### The Problem

Different applications handle EXIF orientation differently, leading to
images appearing rotated or flipped in some viewers but not others.

### Common Scenarios

| Scenario | Result |
|----------|--------|
| App reads orientation and applies transform | Image displays correctly |
| App ignores orientation tag | Image displays with raw pixel orientation (often sideways for phone photos) |
| App applies orientation to pixels and resets tag to 1 | Image displays correctly everywhere, but original tag value is lost |
| App applies orientation to pixels but leaves tag unchanged | **Double-rotation** in apps that honor the tag |

### Which Apps Honor Orientation

| Application | Honors EXIF Orientation |
|-------------|------------------------|
| Safari / WebKit | Yes |
| Chrome | Yes (since 2020; previously only with CSS) |
| Firefox | Yes |
| Preview.app | Yes |
| UIImageView | Yes (via UIImage.imageOrientation) |
| `CGImage` display | **No** (raw pixels, no orientation awareness) |
| CSS `image-orientation` | `from-image` is now the default in all major browsers |
| Terminal image viewers | Varies (iTerm2 yes, others may not) |
| Windows Photo Viewer (legacy) | **No** (fixed in Windows 10 Photos app) |
| Windows Explorer thumbnails | Yes (modern Windows) |

### Mitigation

- Use `kCGImageSourceCreateThumbnailWithTransform: true` to get
  correctly-oriented thumbnails without manual rotation.
- When saving processed images for sharing, bake orientation into pixels and
  set the tag to 1 to maximize compatibility across viewers.
- See [orientation-mapping.md](orientation-mapping.md) for conversion code.

---

## 7. Multi-Value Field Separator Confusion

### The Problem

Multi-value fields (Creator, Keywords) use different storage mechanisms
across standards, leading to incorrect splitting or joining when converting.

| Standard | Storage Method | Example |
|----------|---------------|---------|
| EXIF Artist | Single string, semicolon-space separated | `"Jane Doe; John Smith"` |
| IPTC IIM By-line | Repeating datasets | `[2:80 "Jane Doe"] [2:80 "John Smith"]` |
| IPTC IIM Keywords | Repeating datasets | `[2:25 "sunset"] [2:25 "ocean"]` |
| XMP dc:creator | `rdf:Seq` (ordered array) | `<rdf:li>Jane Doe</rdf:li>` |
| XMP dc:subject | `rdf:Bag` (unordered set) | `<rdf:li>sunset</rdf:li>` |

### Common Bugs

1. **Treating EXIF Artist as a single value.** If EXIF Artist is
   `"Jane Doe; John Smith"`, reading it as one creator name is incorrect.
   It should be split into an array of two creators.
2. **Joining keywords with semicolons in a single IPTC dataset.** Writing
   `"sunset; ocean"` as one 2:25 dataset creates a single keyword containing
   a semicolon, not two keywords. Each keyword must be a separate dataset.
3. **Not quoting creators with semicolons.** If a creator name is
   `"Doe; Jane Inc."`, it must be quoted in the EXIF Artist string to avoid
   being split incorrectly.
4. **Splitting on semicolons without space.** The MWG convention is
   semicolon-space (`; `), not just semicolon. A name like `"O'Brien;Ltd"`
   should not be split.
5. **ImageIO does not implement MWG quoting.** When ImageIO reads EXIF
   Artist, it returns the raw string without splitting. When writing,
   it does not join arrays with semicolons. The application must implement
   this convention.

### Mitigation

```swift
// Parsing EXIF Artist (MWG semicolon-space convention)
func parseExifArtist(_ artist: String) -> [String] {
    // Simple split (does not handle quoted names with semicolons)
    return artist.components(separatedBy: "; ")
}

// Writing EXIF Artist from array
func formatExifArtist(_ creators: [String]) -> String {
    return creators.map { name in
        if name.contains(";") {
            return "\"\(name.replacingOccurrences(of: "\"", with: "\"\""))\""
        }
        return name
    }.joined(separator: "; ")
}
```

---

## 8. Date Format Inconsistencies

### The Problem

Three different date/time formats across three standards, with different
precision and timezone handling.

| Standard | Format | Example | TZ | Fractional Sec |
|----------|--------|---------|-----|----------------|
| EXIF | `YYYY:MM:DD HH:MM:SS` | `2024:06:15 14:30:00` | Separate tag (2.31+) | Separate tag |
| IPTC IIM Date | `YYYYMMDD` | `20240615` | -- | -- |
| IPTC IIM Time | `HHMMSS±HHMM` | `143000+0530` | In field | No |
| XMP | ISO 8601 | `2024-06-15T14:30:00.123+05:30` | In field | Yes |

### Common Bugs

1. **Parsing EXIF dates with ISO 8601 parser.** The colon-separated date
   (`2024:06:15`) is not ISO 8601 compliant (`2024-06-15`). Most ISO 8601
   parsers will reject it. Use a dedicated EXIF date parser or replace
   colons with hyphens in the date portion.

2. **Losing timezone when copying from XMP to EXIF.** EXIF DateTimeOriginal
   has no timezone field in pre-2.31 images. The timezone is lost unless
   OffsetTimeOriginal is also written. Many apps silently drop the timezone.

3. **Losing fractional seconds.** IPTC IIM TimeCreated does not support
   fractional seconds. Converting from XMP (which has `.123`) to IPTC IIM
   loses this precision silently.

4. **ImageIO date sync gap.** `photoshop:DateCreated` written via XMP does
   not auto-sync to IPTC IIM DateCreated/TimeCreated. The ISO 8601 format
   is not converted to IIM's separate date+time format. This is the most
   commonly encountered ImageIO interoperability gap.

5. **Ambiguous timezone.** EXIF DateTimeOriginal without OffsetTimeOriginal
   is timezone-naive. Interpreting it in UTC, device local time, or GPS-
   derived timezone produces different absolute times. There is no correct
   answer — the timezone is genuinely unknown.

6. **XMP partial dates.** XMP allows `"2024"` (year only) or `"2024-06"`
   (year-month), but EXIF requires exactly `"YYYY:MM:DD HH:MM:SS"`.
   Converting a partial XMP date to EXIF requires zero-padding:
   `"2024:00:00 00:00:00"`.

### Parsing Code

```swift
// EXIF date string -> Date
func parseExifDate(_ dateStr: String, offset: String? = nil,
                   subSec: String? = nil) -> Date? {
    let formatter = DateFormatter()
    formatter.locale = Locale(identifier: "en_US_POSIX")

    var combined = dateStr
    if let subSec = subSec {
        combined += ".\(subSec)"
    }
    if let offset = offset {
        combined += offset
        formatter.dateFormat = subSec != nil
            ? "yyyy:MM:dd HH:mm:ss.SSSxxx"
            : "yyyy:MM:dd HH:mm:ssxxx"
    } else {
        formatter.dateFormat = subSec != nil
            ? "yyyy:MM:dd HH:mm:ss.SSS"
            : "yyyy:MM:dd HH:mm:ss"
        // WARNING: This will interpret as device local timezone
    }
    return formatter.date(from: combined)
}

// XMP date string -> Date (ISO 8601)
func parseXMPDate(_ dateStr: String) -> Date? {
    let formatter = ISO8601DateFormatter()
    formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
    if let date = formatter.date(from: dateStr) { return date }

    // Fallback: try without fractional seconds
    formatter.formatOptions = [.withInternetDateTime]
    if let date = formatter.date(from: dateStr) { return date }

    // Fallback: try date-only
    formatter.formatOptions = [.withFullDate]
    return formatter.date(from: dateStr)
}
```

---

## 9. GPS: Signed vs Unsigned Across Standards

### The Problem

GPS coordinates are stored differently across standards and APIs:

| Standard / API | Format | South/West Convention |
|----------------|--------|----------------------|
| EXIF GPS IFD | Absolute value + Ref letter | `Latitude: 33.8688`, `LatitudeRef: "S"` |
| ImageIO property dict | Same as EXIF (absolute + ref) | Same as EXIF |
| XMP exif:GPSLatitude | DMS string with direction | `"33,52.128S"` or `"33,52,7.68S"` |
| CLLocationCoordinate2D | Signed decimal degrees | `latitude: -33.8688` |
| GeoJSON / Web APIs | Signed decimal degrees | `[-33.8688, 151.2093]` |

### Common Bugs

1. **Writing negative values to ImageIO GPS properties.** ImageIO ignores
   the sign on GPS values. Writing `-33.8688` produces incorrect results.
   You must use absolute values + reference letters.

2. **Forgetting to write reference letters.** A latitude without
   `GPSLatitudeRef` is ambiguous and will typically be treated as North by
   readers.

3. **Converting XMP GPS strings incorrectly.** The XMP GPS format
   `"DDD,MM.MMK"` or `"DDD,MM,SS.SSK"` requires parsing the direction
   letter at the end (K = N/S/E/W).

4. **Converting XMP GPS to decimal without handling DMS.** The XMP format
   `"33,52,7.68S"` means 33 degrees, 52 minutes, 7.68 seconds South, not
   the decimal number 33.527.68.

### ImageIO GPS Conversion Helper

```swift
import CoreLocation

func imageIOGPS(from coordinate: CLLocationCoordinate2D) -> [CFString: Any] {
    return [
        kCGImagePropertyGPSLatitude: abs(coordinate.latitude),
        kCGImagePropertyGPSLatitudeRef: coordinate.latitude >= 0 ? "N" : "S",
        kCGImagePropertyGPSLongitude: abs(coordinate.longitude),
        kCGImagePropertyGPSLongitudeRef: coordinate.longitude >= 0 ? "E" : "W"
    ]
}

func coordinate(from gpsDict: [String: Any]) -> CLLocationCoordinate2D? {
    guard let lat = gpsDict[kCGImagePropertyGPSLatitude as String] as? Double,
          let latRef = gpsDict[kCGImagePropertyGPSLatitudeRef as String] as? String,
          let lon = gpsDict[kCGImagePropertyGPSLongitude as String] as? Double,
          let lonRef = gpsDict[kCGImagePropertyGPSLongitudeRef as String] as? String
    else { return nil }

    let latitude = latRef == "S" ? -lat : lat
    let longitude = lonRef == "W" ? -lon : lon
    return CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
}
```

### XMP GPS String Parsing

```swift
func parseXMPGPS(_ xmpString: String) -> Double? {
    // Format: "DDD,MM.MMK" or "DDD,MM,SS.SSK"
    guard let last = xmpString.last else { return nil }
    let direction = String(last)
    let numPart = String(xmpString.dropLast())

    let components = numPart.components(separatedBy: ",")
    guard let degrees = Double(components[0]) else { return nil }

    var decimal = degrees
    if components.count == 2 {
        // DDD,MM.MMK format
        guard let minutes = Double(components[1]) else { return nil }
        decimal += minutes / 60.0
    } else if components.count == 3 {
        // DDD,MM,SS.SSK format
        guard let minutes = Double(components[1]),
              let seconds = Double(components[2]) else { return nil }
        decimal += minutes / 60.0 + seconds / 3600.0
    }

    if direction == "S" || direction == "W" {
        decimal = -decimal
    }
    return decimal
}
```

---

## 10. Metadata Preservation During Format Conversion

### JPEG -> HEIC

| Metadata | Preserved | Notes |
|----------|----------|-------|
| EXIF | Yes | Re-encoded into HEIF EXIF box |
| GPS | Yes | Within EXIF |
| XMP | Yes | Embedded in HEIF container |
| IPTC IIM | **Lost** | HEIF does not support IPTC IIM |
| ICC Profile | Yes | Embedded in HEIF |
| MakerNote | Partially | Depends on tool; internal offsets may break |
| Thumbnail | Lost | New thumbnail generated by HEIF encoder |
| Depth map | N/A | JPEG typically does not have depth maps |

### HEIC -> JPEG

| Metadata | Preserved | Notes |
|----------|----------|-------|
| EXIF | Yes | Written to JPEG APP1 segment |
| GPS | Yes | Within EXIF APP1 |
| XMP | Yes | Written to JPEG APP1 segment |
| IPTC IIM | May be generated | ImageIO synthesizes from XMP; ExifTool only if `-use MWG` |
| ICC Profile | Yes | Written to JPEG APP2 segment |
| Auxiliary data (depth, gain map) | **Lost** | JPEG cannot store these natively |
| Portrait effects matte | **Lost** | No JPEG equivalent |

### JPEG/HEIC -> PNG

| Metadata | Preserved | Notes |
|----------|----------|-------|
| EXIF | **Lost** | PNG does not support EXIF natively (some tools embed in iTXt) |
| GPS | **Lost** | No standard GPS storage in PNG |
| XMP | Yes | Embedded in PNG iTXt chunk |
| IPTC IIM | **Lost** | PNG does not support IPTC IIM |
| ICC Profile | Yes | Embedded in PNG iCCP chunk |

### Any Format -> GIF

| Metadata | Preserved | Notes |
|----------|----------|-------|
| All metadata | **Lost** | GIF has no standard metadata storage |
| ICC Profile | **Lost** | GIF does not support ICC profiles |
| Color depth | Reduced | GIF is limited to 256 colors |

### Key Issues

1. **IPTC IIM loss in HEIF.** HEIF does not support IPTC IIM. Converting
   JPEG -> HEIC loses IPTC IIM data unless it is also present in XMP.
   This is why modern workflows should always have IPTC data in XMP.

2. **MakerNote fragility.** MakerNote data uses internal offsets that
   reference positions in the original file. Moving MakerNote to a different
   file structure can invalidate these offsets, making MakerNote data
   unreadable. Some tools (ExifTool) attempt to fix up offsets during
   conversion; ImageIO does not.

3. **Auxiliary data loss.** Depth maps, gain maps, portrait mattes, and
   semantic segmentation mattes from HEIF are lost when converting to JPEG
   (unless the tool explicitly handles them as separate images).

4. **PNG metadata limitations.** PNG only supports XMP and ICC profiles
   natively. Converting to PNG loses EXIF and IPTC IIM. Some tools embed
   EXIF in PNG iTXt chunks (non-standard), but this is not universally
   supported.

5. **Color space conversion.** Converting between formats may trigger
   color space conversion. For example, an HEIC file in Display P3 color
   space converted to JPEG with `kCGImageDestinationOptimizeColorForSharing`
   will be converted to sRGB, which can visibly alter colors.

---

## 11. ExifTool vs ImageIO: Different Default Behaviors

### Writing Defaults

| Behavior | ImageIO | ExifTool (default) | ExifTool (MWG) |
|----------|---------|-------------------|---------------|
| Default write target | XMP (via `CGImageMetadata`) | Specified location only | All overlapping locations |
| IPTC IIM creation | Creates from XMP regardless | Only if specified | Only if IIM already exists |
| IPTCDigest management | Not maintained | Not maintained | Automatically maintained |
| UTF-8 in EXIF ASCII | Written naturally | Written with `-charset exif=UTF8` | Written per MWG recommendation |
| Multi-value EXIF Artist | Array handling (no semicolons) | Raw string | Semicolon convention |

### Reading Defaults

| Behavior | ImageIO | ExifTool (default) | ExifTool (MWG) |
|----------|---------|-------------------|---------------|
| Cross-standard synthesis | Automatic (both APIs see all data) | No synthesis (reads each tag separately) | MWG composite tags reconcile |
| IPTCDigest validation | Not performed | Not performed | Performed and used for priority |
| Charset detection | Assumes UTF-8 always | Checks CodedCharacterSet, defaults to Latin-1 | Same as default |
| Non-standard locations | Read from all locations | Read from all locations | Ignored with warnings |

### Practical Impact

1. **File written by ImageIO, read by ExifTool:** ExifTool sees XMP and
   regenerated IPTC IIM but no IPTCDigest. Without MWG module, it reads
   each independently. With MWG, absent digest means "prefer XMP" which
   is correct.

2. **File written by ExifTool (default), read by ImageIO:** If ExifTool wrote
   only to IPTC IIM (no XMP), ImageIO synthesizes XMP on read. This works
   seamlessly.

3. **Files with Latin-1 IPTC:** ExifTool reads correctly (detects encoding).
   ImageIO may produce garbled text (assumes UTF-8).

4. **Files with conflicting EXIF and IPTC:** ExifTool with MWG detects via
   IPTCDigest and prefers the newer value. ImageIO ignores the digest and
   may serve stale data.

---

## 12. LangAlt Fields: The Silent Write Bug

### The Problem

Three important IPTC fields use `langAlt` (language alternative) type in
XMP: `dc:title`, `dc:description`, and `dc:rights`. Creating these via
`CGImageMetadataTagCreate(.alternateText, CFDictionary)` produces tags that
are **silently dropped** by `CGImageDestinationCopyImageSource`. The API
returns `true` (success) when setting the tag, but the tag does not appear
in the output file.

### Affected Fields

| XMP Path | IPTC IIM Equivalent | Type | Impact |
|----------|-------------------|------|--------|
| `dc:title` | ObjectName (2:5) | `langAlt` | Title silently lost |
| `dc:description` | Caption-Abstract (2:120) | `langAlt` | Description silently lost |
| `dc:rights` | CopyrightNotice (2:116) | `langAlt` | Copyright silently lost |

### Working Alternatives

**Option 1: Use `SetValueWithPath` with a plain string (single language):**

```swift
// Apple auto-creates proper langAlt structure internally
CGImageMetadataSetValueWithPath(metadata, nil,
    "dc:title" as CFString,
    "My Title" as CFString)
// This WORKS — the tag survives CopyImageSource
```

**Option 2: Parse from XMP snippet (multi-language):**

```swift
let xmpSnippet = """
    <x:xmpmeta xmlns:x="adobe:ns:meta/">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title><rdf:Alt>
    <rdf:li xml:lang="x-default">English title</rdf:li>
    <rdf:li xml:lang="de">Deutscher Titel</rdf:li>
    <rdf:li xml:lang="ja">日本語のタイトル</rdf:li>
    </rdf:Alt></dc:title>
    </rdf:Description></rdf:RDF></x:xmpmeta>
    """
let tempMeta = CGImageMetadataCreateFromXMPData(Data(xmpSnippet.utf8) as CFData)!
let tag = CGImageMetadataCopyTagWithPath(tempMeta, nil, "dc:title" as CFString)!
CGImageMetadataSetTagWithPath(mutableMeta, nil, "dc:title" as CFString, tag)
// This WORKS — tags parsed from XMP survive CopyImageSource
```

See [../imageio/cgimage-metadata.md](../imageio/cgimage-metadata.md) for
full details on the bug and workarounds.

---

## 13. Tag Removal in Merge Mode Does Not Persist

### The Problem

`CGImageMetadataRemoveTagWithPath` successfully removes a tag from an
in-memory `CGMutableImageMetadata` object. However, when written via
`CGImageDestinationCopyImageSource` with `kCGImageDestinationMergeMetadata:
true`, the removed tag **reappears** from the source image.

This is because merge mode overlays provided metadata onto the source.
Tags absent from the provided metadata are preserved from the source, not
removed.

### Working Alternative

Set the tag value to `kCFNull` instead of removing it:

```swift
// Does NOT work in merge mode:
CGImageMetadataRemoveTagWithPath(metadata, nil, "photoshop:City" as CFString)

// WORKS in merge mode:
CGImageMetadataSetValueWithPath(metadata, nil,
    "photoshop:City" as CFString,
    kCFNull)
// kCFNull signals "actively remove this tag" rather than "tag not present"
```

---

## 14. HEIC Lossless Metadata Update Not Supported

### The Problem

`CGImageDestinationCopyImageSource` — the lossless metadata update API —
does not support HEIC/HEIF format. Attempting it silently fails or produces
an error.

### Workaround

For HEIC, you must re-encode the entire image to update metadata:

```swift
let source = CGImageSourceCreateWithURL(heicURL as CFURL, nil)!
let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil)!
let metadata = CGImageSourceCopyMetadataAtIndex(source, 0, nil)!

// Modify metadata
let mutable = CGImageMetadataCreateMutableCopy(metadata)!
CGImageMetadataSetValueWithPath(mutable, nil,
    "dc:description" as CFString,
    "Updated description" as CFString)

// Re-encode (lossy!)
let output = NSMutableData()
let dest = CGImageDestinationCreateWithData(output, "public.heic" as CFString, 1, nil)!
CGImageDestinationAddImageAndMetadata(dest, cgImage, mutable, [
    kCGImageDestinationLossyCompressionQuality: 0.95
] as CFDictionary)
CGImageDestinationFinalize(dest)
```

This re-encodes the pixel data, causing generation loss. For workflows that
require lossless metadata editing of HEIC files, consider:
- Using ExifTool (which can modify HEIC metadata without re-encoding)
- Converting to JPEG for metadata editing, then back to HEIC
- Storing metadata in a sidecar file

---

## 15. Clean JPEG Baseline: Phantom EXIF Fields

Even a "clean" JPEG (1x1 pixel, no metadata written) gets synthetic EXIF
fields from Apple: `PixelXDimension` and `PixelYDimension` are populated
from the image dimensions. Tests that check for empty EXIF dictionaries
on clean images will fail.

```swift
// Creating a minimal JPEG
let dest = CGImageDestinationCreateWithData(data, kUTTypeJPEG, 1, nil)!
CGImageDestinationAddImage(dest, onePxImage, [:] as CFDictionary)
CGImageDestinationFinalize(dest)

// Reading back
let source = CGImageSourceCreateWithData(data as CFData, nil)!
let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any]
let exif = props?[kCGImagePropertyExifDictionary as String] as? [String: Any]
// exif is NOT nil — contains PixelXDimension and PixelYDimension
```

Always compare against a known baseline rather than checking `isEmpty`.

---

## Cross-References

- [overlapping-fields.md](overlapping-fields.md) — Complete field mapping
  tables
- [mwg-guidelines.md](mwg-guidelines.md) — MWG reconciliation rules
- [imageio-behavior.md](imageio-behavior.md) — ImageIO cross-standard
  behavior
- [orientation-mapping.md](orientation-mapping.md) — Three orientation systems
- [../imageio/pitfalls.md](../imageio/pitfalls.md) — ImageIO-specific pitfalls
- [../exif/pitfalls.md](../exif/pitfalls.md) — EXIF-specific pitfalls
