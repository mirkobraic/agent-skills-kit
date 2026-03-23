# TIFF <> ImageIO Mapping

> Part of [TIFF Reference](README.md)

How Apple's ImageIO framework exposes TIFF IFD tags: all
`kCGImagePropertyTIFF*` constants, Swift code examples for reading and writing,
orientation duplication, DateTime relationships, and XMP mapping through the
`tiff:` namespace.

---

## All kCGImagePropertyTIFF* Constants

Every constant in `kCGImagePropertyTIFFDictionary`, available since iOS 4.0
unless noted otherwise:

| Constant | CFType | TIFF Tag | Tag ID |
|----------|--------|----------|--------|
| `kCGImagePropertyTIFFCompression` | CFNumber | Compression | 259 |
| `kCGImagePropertyTIFFPhotometricInterpretation` | CFNumber | PhotometricInterpretation | 262 |
| `kCGImagePropertyTIFFDocumentName` | CFString | DocumentName | 269 |
| `kCGImagePropertyTIFFImageDescription` | CFString | ImageDescription | 270 |
| `kCGImagePropertyTIFFMake` | CFString | Make | 271 |
| `kCGImagePropertyTIFFModel` | CFString | Model | 272 |
| `kCGImagePropertyTIFFOrientation` | CFNumber | Orientation | 274 |
| `kCGImagePropertyTIFFXResolution` | CFNumber | XResolution | 282 |
| `kCGImagePropertyTIFFYResolution` | CFNumber | YResolution | 283 |
| `kCGImagePropertyTIFFResolutionUnit` | CFNumber | ResolutionUnit | 296 |
| `kCGImagePropertyTIFFTransferFunction` | CFArray | TransferFunction | 301 |
| `kCGImagePropertyTIFFSoftware` | CFString | Software | 305 |
| `kCGImagePropertyTIFFDateTime` | CFString | DateTime | 306 |
| `kCGImagePropertyTIFFArtist` | CFString | Artist | 315 |
| `kCGImagePropertyTIFFHostComputer` | CFString | HostComputer | 316 |
| `kCGImagePropertyTIFFWhitePoint` | CFArray | WhitePoint | 318 |
| `kCGImagePropertyTIFFPrimaryChromaticities` | CFArray | PrimaryChromaticities | 319 |
| `kCGImagePropertyTIFFCopyright` | CFString | Copyright | 33432 |
| `kCGImagePropertyTIFFTileWidth` | CFNumber | TileWidth | 322 |
| `kCGImagePropertyTIFFTileLength` | CFNumber | TileLength | 323 |

`TileWidth` and `TileLength` are documented for macOS 10.11+. They appear
in the header file but are not listed in iOS-specific documentation.

---

## Reading TIFF Metadata

### Reading All TIFF Properties

```swift
import ImageIO

func readTIFFMetadata(from url: URL) -> [String: Any]? {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else {
        return nil
    }

    guard let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
            as? [String: Any] else {
        return nil
    }

    // TIFF dictionary is one of several sub-dictionaries
    let tiff = properties[kCGImagePropertyTIFFDictionary as String] as? [String: Any]
    return tiff
}
```

### Reading Specific TIFF Tags

```swift
func readDeviceInfo(from url: URL) -> (make: String?, model: String?, software: String?) {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any],
          let tiff = props[kCGImagePropertyTIFFDictionary as String] as? [String: Any]
    else {
        return (nil, nil, nil)
    }

    let make = tiff[kCGImagePropertyTIFFMake as String] as? String
    let model = tiff[kCGImagePropertyTIFFModel as String] as? String
    let software = tiff[kCGImagePropertyTIFFSoftware as String] as? String

    return (make, model, software)
}

// Usage:
// let info = readDeviceInfo(from: imageURL)
// info.make     -> "Apple"
// info.model    -> "iPhone 16 Pro"
// info.software -> "18.3.2"
```

### Reading DateTime

```swift
func readDateTime(from url: URL) -> String? {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any],
          let tiff = props[kCGImagePropertyTIFFDictionary as String] as? [String: Any]
    else {
        return nil
    }

    // Format: "YYYY:MM:DD HH:MM:SS"
    // WARNING: No timezone information. Use EXIF OffsetTime* for timezone.
    return tiff[kCGImagePropertyTIFFDateTime as String] as? String
}
```

### Reading All Properties at Once (TIFF + EXIF + GPS)

```swift
func readAllMetadata(from url: URL) {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
            as? [String: Any]
    else { return }

    // These all come from the same underlying TIFF/IFD structure
    let tiff = props[kCGImagePropertyTIFFDictionary as String] as? [String: Any]
    let exif = props[kCGImagePropertyExifDictionary as String] as? [String: Any]
    let gps  = props[kCGImagePropertyGPSDictionary as String] as? [String: Any]

    // Top-level properties (also derived from TIFF structure)
    let width = props[kCGImagePropertyPixelWidth as String] as? Int
    let height = props[kCGImagePropertyPixelHeight as String] as? Int
    let orientation = props[kCGImagePropertyOrientation as String] as? Int
    let depth = props[kCGImagePropertyDepth as String] as? Int
    let colorModel = props[kCGImagePropertyColorModel as String] as? String
    let profileName = props[kCGImagePropertyProfileName as String] as? String
}
```

---

## Writing TIFF Metadata

### Writing Metadata to a New Image

```swift
import ImageIO
import UniformTypeIdentifiers

func writeImageWithTIFFMetadata(
    image: CGImage,
    tiffMetadata: [String: Any],
    to url: URL
) {
    guard let dest = CGImageDestinationCreateWithURL(
        url as CFURL,
        UTType.jpeg.identifier as CFString,
        1,
        nil
    ) else { return }

    let properties: [String: Any] = [
        kCGImagePropertyTIFFDictionary as String: tiffMetadata
    ]

    CGImageDestinationAddImage(dest, image, properties as CFDictionary)
    CGImageDestinationFinalize(dest)
}

// Usage:
let tiff: [String: Any] = [
    kCGImagePropertyTIFFArtist as String: "Jane Smith",
    kCGImagePropertyTIFFCopyright as String: "(c) 2025 Jane Smith",
    kCGImagePropertyTIFFMake as String: "Apple",
    kCGImagePropertyTIFFModel as String: "iPhone 16 Pro",
    kCGImagePropertyTIFFSoftware as String: "MyApp 2.0",
    kCGImagePropertyTIFFDateTime as String: "2025:03:15 14:30:22"
]
// writeImageWithTIFFMetadata(image: cgImage, tiffMetadata: tiff, to: outputURL)
```

### Lossless Metadata Update (No Re-encoding)

Available for JPEG, PNG, TIFF, and PSD formats (iOS 7.0+). This preserves
pixel data exactly -- no quality loss from re-compression:

```swift
func updateTIFFMetadataLosslessly(
    at url: URL,
    updates: [String: Any]
) -> Bool {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let uti = CGImageSourceGetType(source)
    else { return false }

    let tempURL = url.deletingLastPathComponent()
        .appendingPathComponent(UUID().uuidString)
        .appendingPathExtension(url.pathExtension)

    guard let dest = CGImageDestinationCreateWithURL(
        tempURL as CFURL, uti, 1, nil
    ) else { return false }

    let metadata: [String: Any] = [
        kCGImagePropertyTIFFDictionary as String: updates
    ]

    var error: Unmanaged<CFError>?
    let success = CGImageDestinationCopyImageSource(
        dest, source, metadata as CFDictionary, &error
    )

    if success {
        try? FileManager.default.removeItem(at: url)
        try? FileManager.default.moveItem(at: tempURL, to: url)
    } else {
        try? FileManager.default.removeItem(at: tempURL)
    }

    return success
}

// Usage -- update artist without re-encoding:
// updateTIFFMetadataLosslessly(
//     at: imageURL,
//     updates: [kCGImagePropertyTIFFArtist as String: "Updated Artist"]
// )
```

**Important:** Lossless update is NOT available for HEIC/HEIF. Writing
metadata to HEIC requires re-encoding the image, which introduces a
generation loss. See [`../imageio/cgimagedestination.md`](../imageio/cgimagedestination.md)
for details.

### Writing Multiple Dictionaries Together

When writing metadata, you can set TIFF, EXIF, GPS, and IPTC dictionaries
in a single properties dictionary:

```swift
let properties: [String: Any] = [
    // Top-level orientation
    kCGImagePropertyOrientation as String: 1,

    // TIFF dictionary
    kCGImagePropertyTIFFDictionary as String: [
        kCGImagePropertyTIFFArtist as String: "Jane Smith",
        kCGImagePropertyTIFFCopyright as String: "(c) 2025 Jane Smith",
        kCGImagePropertyTIFFOrientation as String: 1,
        kCGImagePropertyTIFFSoftware as String: "MyApp 2.0"
    ] as [String: Any],

    // EXIF dictionary
    kCGImagePropertyExifDictionary as String: [
        kCGImagePropertyExifDateTimeOriginal as String: "2025:03:15 14:30:22",
        kCGImagePropertyExifOffsetTimeOriginal as String: "-05:00"
    ] as [String: Any],

    // IPTC dictionary (for sync with TIFF Artist/Copyright)
    kCGImagePropertyIPTCDictionary as String: [
        kCGImagePropertyIPTCByline as String: ["Jane Smith"],
        kCGImagePropertyIPTCCopyrightNotice as String: "(c) 2025 Jane Smith"
    ] as [String: Any]
]
```

### Writing Orientation

```swift
// Set orientation when writing a new image
let properties: [String: Any] = [
    // Top-level orientation (preferred -- this is what ImageIO reads first)
    kCGImagePropertyOrientation as String: 6,  // 90 CW

    // TIFF dictionary orientation (should match)
    kCGImagePropertyTIFFDictionary as String: [
        kCGImagePropertyTIFFOrientation as String: 6
    ]
]

CGImageDestinationAddImage(dest, image, properties as CFDictionary)
```

---

## Orientation Duplication

Orientation appears in **two places** in ImageIO's property dictionary:

| Location | Key | Value |
|----------|-----|-------|
| Top-level | `kCGImagePropertyOrientation` | CFNumber (1-8) |
| TIFF dictionary | `kCGImagePropertyTIFFOrientation` | CFNumber (1-8) |

Both use the same 1-8 EXIF orientation values.

### Behavior

- **Reading:** ImageIO populates both from the same IFD0 Orientation tag.
  They should always be identical when reading.
- **Writing:** If you set only one, ImageIO may not propagate the change to
  the other. Best practice is to **set both** when writing.
- **Top-level is canonical:** When ImageIO needs orientation (e.g., for
  `CGImageSourceCreateThumbnailWithTransform`), it reads the top-level
  `kCGImagePropertyOrientation`.

### CGImagePropertyOrientation vs UIImage.Orientation

These are **different enumerations with different numbering:**

| EXIF / CGImagePropertyOrientation | UIImage.Orientation | Transform |
|-----------------------------------|--------------------:|-----------|
| 1 (up) | 0 (.up) | Normal |
| 2 (upMirrored) | 4 (.upMirrored) | H flip |
| 3 (down) | 1 (.down) | 180 |
| 4 (downMirrored) | 5 (.downMirrored) | V flip |
| 5 (leftMirrored) | 6 (.leftMirrored) | Transpose |
| 6 (right) | 3 (.right) | 90 CW |
| 7 (rightMirrored) | 7 (.rightMirrored) | Transverse |
| 8 (left) | 2 (.left) | 90 CCW |

**Never cast between these types directly.** The raw values do not correspond.
Use the conversion initializer:

```swift
extension CGImagePropertyOrientation {
    init(_ uiOrientation: UIImage.Orientation) {
        switch uiOrientation {
        case .up:            self = .up
        case .upMirrored:    self = .upMirrored
        case .down:          self = .down
        case .downMirrored:  self = .downMirrored
        case .left:          self = .left
        case .leftMirrored:  self = .leftMirrored
        case .right:         self = .right
        case .rightMirrored: self = .rightMirrored
        @unknown default:    self = .up
        }
    }
}
```

### Three Orientation Systems in the Apple Ecosystem

| System | Type | Range | Where Used |
|--------|------|-------|------------|
| EXIF / TIFF tag | Integer | 1-8 | Raw metadata, `kCGImagePropertyOrientation`, `kCGImagePropertyTIFFOrientation` |
| `CGImagePropertyOrientation` | Enum | `.up` through `.leftMirrored` | ImageIO, Core Image, Vision, VNImageRequestHandler |
| `UIImage.Orientation` | Enum | `.up` through `.rightMirrored` | UIKit only |

The first two (EXIF and CGImagePropertyOrientation) use the same numbering
and can be freely interconverted. UIImage.Orientation uses different raw
values and requires explicit mapping.

---

## DateTime Relationships

TIFF DateTime is one of **three** date/time fields in image metadata. They
all use the same format but have different meanings:

| Tag | Dictionary | Key | Meaning |
|-----|------------|-----|---------|
| DateTime (0x0132) | TIFF | `kCGImagePropertyTIFFDateTime` | File last modified |
| DateTimeOriginal (0x9003) | EXIF | `kCGImagePropertyExifDateTimeOriginal` | Original capture |
| DateTimeDigitized (0x9004) | EXIF | `kCGImagePropertyExifDateTimeDigitized` | When digitized |

All three use format `"YYYY:MM:DD HH:MM:SS"` with **no timezone**.

For timezone, check the EXIF 2.31+ offset tags:
- `kCGImagePropertyExifOffsetTime` -- offset for TIFF DateTime
- `kCGImagePropertyExifOffsetTimeOriginal` -- offset for DateTimeOriginal
- `kCGImagePropertyExifOffsetTimeDigitized` -- offset for DateTimeDigitized

### Parsing DateTime with Timezone

```swift
// Building a timezone-aware Date from TIFF DateTime + EXIF OffsetTime
func parseDateTime(tiff: [String: Any], exif: [String: Any]) -> Date? {
    guard let dateStr = tiff[kCGImagePropertyTIFFDateTime as String] as? String
    else { return nil }

    let formatter = DateFormatter()
    formatter.locale = Locale(identifier: "en_US_POSIX")

    if let offset = exif[kCGImagePropertyExifOffsetTime as String] as? String {
        // Has timezone: "2025:03:15 14:30:22" + "-05:00"
        formatter.dateFormat = "yyyy:MM:dd HH:mm:ssxxx"
        return formatter.date(from: dateStr + offset)
    } else {
        // No timezone -- ambiguous, assume device local time
        formatter.dateFormat = "yyyy:MM:dd HH:mm:ss"
        return formatter.date(from: dateStr)
    }
}
```

### Formatting DateTime for Writing

```swift
func formatTIFFDateTime(_ date: Date) -> String {
    let formatter = DateFormatter()
    formatter.locale = Locale(identifier: "en_US_POSIX")
    formatter.dateFormat = "yyyy:MM:dd HH:mm:ss"
    // Note: writing local time without timezone -- the TIFF spec has no timezone field
    return formatter.string(from: date)
}

func formatOffsetTime(_ date: Date) -> String {
    let formatter = DateFormatter()
    formatter.locale = Locale(identifier: "en_US_POSIX")
    formatter.dateFormat = "xxx"  // Produces "+HH:MM" or "-HH:MM"
    return formatter.string(from: date)
}

// Write both TIFF DateTime and EXIF OffsetTime together:
let now = Date()
let properties: [String: Any] = [
    kCGImagePropertyTIFFDictionary as String: [
        kCGImagePropertyTIFFDateTime as String: formatTIFFDateTime(now)
    ],
    kCGImagePropertyExifDictionary as String: [
        kCGImagePropertyExifOffsetTime as String: formatOffsetTime(now)
    ]
]
```

---

## Make and Model: What iOS Writes

When an iPhone captures a photo, it populates these TIFF tags:

| Tag | Example Value | Notes |
|-----|---------------|-------|
| Make | `"Apple"` | Always `"Apple"` for all Apple devices |
| Model | `"iPhone 16 Pro"` | Marketing name of the device |
| Software | `"18.3.2"` | iOS version number (not app name) |
| HostComputer | `"iPhone 16 Pro"` | Duplicates Model (Apple-specific behavior) |

For iPad:
- Make: `"Apple"`
- Model: `"iPad Pro (12.9-inch) (6th generation)"`
- HostComputer: `"iPad Pro (12.9-inch) (6th generation)"`

For Mac screenshots:
- Make: typically absent
- Model: typically absent
- Software: `"macOS 14.3 (23D56)"` or similar

### Identifying Device from Metadata

```swift
func identifyDevice(from url: URL) -> String {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any],
          let tiff = props[kCGImagePropertyTIFFDictionary as String] as? [String: Any]
    else { return "Unknown" }

    let make = tiff[kCGImagePropertyTIFFMake as String] as? String ?? ""
    let model = tiff[kCGImagePropertyTIFFModel as String] as? String ?? ""

    // Case-insensitive comparison -- manufacturers are inconsistent
    if make.caseInsensitiveCompare("Apple") == .orderedSame {
        return model  // "iPhone 16 Pro", "iPad Air (5th generation)", etc.
    } else {
        return "\(make) \(model)"  // "Canon Canon EOS R5", "NIKON CORPORATION NIKON Z 9"
    }
}
```

Note: some manufacturers include the brand name in both Make and Model
(e.g., `Make: "Canon", Model: "Canon EOS R5"`), while others use a corporate
name in Make and a product name in Model (e.g., `Make: "NIKON CORPORATION",
Model: "NIKON Z 9"`). Apple uses `Make: "Apple"` with a clean model string.

---

## XMP Mapping for TIFF Tags

TIFF IFD0 tags map to the `tiff:` XMP namespace:

**Namespace URI:** `http://ns.adobe.com/tiff/1.0/`
**Prefix:** `tiff`
**ImageIO Constant:** `kCGImageMetadataNamespaceTIFF`
**ImageIO Prefix Constant:** `kCGImageMetadataPrefixTIFF`

### Complete tiff: Namespace Properties

The XMP `tiff:` namespace includes all TIFF IFD0 tags, including some that
ImageIO does not expose in the TIFF dictionary:

| TIFF Tag | Tag ID | XMP Path | XMP Type | In TIFF Dict? |
|----------|--------|----------|----------|---------------|
| ImageWidth | 0x0100 | `tiff:ImageWidth` | Integer | No (top-level) |
| ImageLength | 0x0101 | `tiff:ImageLength` | Integer | No (top-level) |
| BitsPerSample | 0x0102 | `tiff:BitsPerSample` | Seq Integer | No (top-level) |
| Compression | 0x0103 | `tiff:Compression` | Integer | Yes |
| PhotometricInterpretation | 0x0106 | `tiff:PhotometricInterpretation` | Integer | Yes |
| ImageDescription | 0x010E | `tiff:ImageDescription` | Alt Text | Yes |
| Make | 0x010F | `tiff:Make` | Text | Yes |
| Model | 0x0110 | `tiff:Model` | Text | Yes |
| Orientation | 0x0112 | `tiff:Orientation` | Integer | Yes |
| SamplesPerPixel | 0x0115 | `tiff:SamplesPerPixel` | Integer | No (implicit) |
| XResolution | 0x011A | `tiff:XResolution` | Rational | Yes |
| YResolution | 0x011B | `tiff:YResolution` | Rational | Yes |
| ResolutionUnit | 0x0128 | `tiff:ResolutionUnit` | Integer | Yes |
| TransferFunction | 0x012D | `tiff:TransferFunction` | Seq Integer | Yes |
| Software | 0x0131 | `tiff:Software` | Text (AgentName) | Yes |
| DateTime | 0x0132 | `tiff:DateTime` | Date (ISO 8601) | Yes |
| Artist | 0x013B | `tiff:Artist` | Text (ProperName) | Yes |
| HostComputer | -- | -- | -- | Yes (no XMP equivalent) |
| WhitePoint | 0x013E | `tiff:WhitePoint` | Seq Rational | Yes |
| PrimaryChromaticities | 0x013F | `tiff:PrimaryChromaticities` | Seq Rational | Yes |
| YCbCrCoefficients | 0x0211 | `tiff:YCbCrCoefficients` | Seq Rational | No |
| YCbCrPositioning | 0x0213 | `tiff:YCbCrPositioning` | Integer | No |
| ReferenceBlackWhite | 0x0214 | `tiff:ReferenceBlackWhite` | Seq Rational | No |
| Copyright | 0x8298 | `tiff:Copyright` | Text (Alt) | Yes |
| NativeDigest | -- | `tiff:NativeDigest` | Text | No (XMP only) |

Notes:
- **HostComputer** has no standard XMP equivalent in the `tiff:` namespace.
- **tiff:NativeDigest** is an XMP-only property (no binary TIFF tag) used by
  Adobe software to detect whether binary TIFF tags have changed since XMP
  was last synchronized.
- **YCbCrCoefficients**, **YCbCrPositioning**, and **ReferenceBlackWhite**
  exist in the XMP `tiff:` namespace but are not in ImageIO's TIFF dictionary.

### DateTime Format Difference

The TIFF binary format stores DateTime as `"YYYY:MM:DD HH:MM:SS"`. The XMP
`tiff:DateTime` property stores the same value in **ISO 8601** format:
`"2025-03-15T14:30:22"`. ImageIO handles this conversion automatically when
using the bridge functions.

Additionally, `tiff:DateTime` is equivalent to `xmp:ModifyDate` in the XMP
basic namespace. Both represent the file's last modification time. Adobe
software may write one or both.

### ImageDescription as Language Alternative

In TIFF binary, ImageDescription is a single ASCII string. In XMP,
`tiff:ImageDescription` is a language alternative (`rdf:Alt` with `xml:lang`
attributes). When converting:

- **Binary to XMP:** The ASCII string becomes the `x-default` entry
- **XMP to binary:** The `x-default` entry (or first entry if no default)
  is written as the ASCII string

This is the same pattern used by `dc:description` and `dc:rights`.

### Using Bridge Functions

```swift
import ImageIO

// Read a TIFF tag via XMP bridge
func readTIFFTagViaXMP(source: CGImageSource) -> String? {
    guard let metadata = CGImageSourceCopyMetadataAtIndex(source, 0, nil) else {
        return nil
    }

    // Find the XMP tag matching a TIFF property key
    let tag = CGImageMetadataCopyTagMatchingImageProperty(
        metadata,
        kCGImagePropertyTIFFDictionary,
        kCGImagePropertyTIFFArtist
    )

    return tag.flatMap { CGImageMetadataTagCopyValue($0) as? String }
}

// Write a TIFF tag via XMP bridge
func writeTIFFTagViaXMP(metadata: CGMutableImageMetadata, artist: String) -> Bool {
    return CGImageMetadataSetValueMatchingImageProperty(
        metadata,
        kCGImagePropertyTIFFDictionary,
        kCGImagePropertyTIFFArtist,
        artist as CFString
    )
}
```

### Direct XMP Access (Without Bridge)

For more control, you can access the `tiff:` namespace directly:

```swift
func readTIFFMakeViaXMP(source: CGImageSource) -> String? {
    guard let metadata = CGImageSourceCopyMetadataAtIndex(source, 0, nil) else {
        return nil
    }

    // Create a tag path in the tiff: namespace
    let tag = CGImageMetadataCopyTagWithPath(
        metadata,
        nil,
        "tiff:Make" as CFString
    )

    return tag.flatMap { CGImageMetadataTagCopyValue($0) as? String }
}
```

### Auto-Synthesis

ImageIO automatically synthesizes XMP `tiff:` tags from the binary TIFF
IFD0 data when you call `CGImageSourceCopyMetadataAtIndex`. You do not need
to write XMP separately if you set values in the TIFF property dictionary --
ImageIO will include them in the XMP tree.

However, the reverse is not always true: setting a value via the XMP
metadata API does not automatically update the property dictionary. The two
APIs (property dictionaries and CGImageMetadata) operate somewhat
independently. When writing, prefer the property dictionary path for TIFF
tags.

---

## Complete Properties Example

A typical iPhone photo has this TIFF dictionary content:

```swift
// Properties from CGImageSourceCopyPropertiesAtIndex for an iPhone 16 Pro photo:

// kCGImagePropertyTIFFDictionary:
[
    "Make": "Apple",
    "Model": "iPhone 16 Pro",
    "Software": "18.3.2",
    "HostComputer": "iPhone 16 Pro",
    "DateTime": "2025:03:15 14:30:22",
    "Orientation": 6,                    // Portrait, 90 CW
    "XResolution": 72,
    "YResolution": 72,
    "ResolutionUnit": 2,                 // Inches
    "WhitePoint": [0.3127, 0.3290],      // D65
    "PrimaryChromaticities": [0.68, 0.32, 0.265, 0.69, 0.15, 0.06]  // Display P3
]

// Top-level (also populated from the same TIFF structure):
[
    "Orientation": 6,                    // Same as TIFF Orientation
    "PixelWidth": 4032,
    "PixelHeight": 3024,
    "DPIWidth": 72,
    "DPIHeight": 72,
    "Depth": 8,
    "ColorModel": "RGB",
    "ProfileName": "Display P3"
]
```

### Canon DSLR Example

```swift
// kCGImagePropertyTIFFDictionary from a Canon EOS R5:
[
    "Make": "Canon",
    "Model": "Canon EOS R5",
    "Software": "Firmware Version 2.0.0",
    "DateTime": "2025:06:20 09:15:30",
    "Orientation": 1,                    // Landscape
    "XResolution": 72,
    "YResolution": 72,
    "ResolutionUnit": 2,
    "Copyright": "(c) 2025 Photographer Name",
    "Artist": "Photographer Name"
]
// Note: no HostComputer, no WhitePoint, no PrimaryChromaticities
// (these are less commonly written by non-Apple cameras)
```

### Scanned Document Example

```swift
// kCGImagePropertyTIFFDictionary from a scanner:
[
    "Make": "Epson",
    "Model": "Perfection V600",
    "Software": "Epson Scan 2",
    "DateTime": "2025:01:10 11:00:00",
    "Orientation": 1,
    "XResolution": 300,                  // 300 DPI scan
    "YResolution": 300,
    "ResolutionUnit": 2,
    "DocumentName": "Invoice_2025_001.pdf",
    "ImageDescription": "Scanned invoice"
]
```
