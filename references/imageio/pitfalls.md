# Common Pitfalls, Thread Safety & PhotoKit Integration

---

## Metadata Loss Through UIImage

**The #1 pitfall.** `UIImage` strips all metadata except orientation.

```swift
// ❌ Metadata is LOST
let image = UIImage(data: jpegData)
let newData = image.jpegData(compressionQuality: 0.8)  // no EXIF, no GPS, no IPTC

// ❌ Also loses metadata
let image = UIImage(named: "photo")
let image = UIImage(contentsOfFile: path)
```

`CGImage` also does not carry metadata — it's just a pixel buffer.

**Solution:** Always use `CGImageSource` / `CGImageDestination` when metadata
matters. Read metadata separately, process pixels as needed, then write both
back together.

```swift
// ✓ Preserve metadata
let source = CGImageSourceCreateWithData(jpegData as CFData, nil)!
let metadata = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil)!

// ... process cgImage ...

let dest = CGImageDestinationCreateWithData(output, kUTTypeJPEG, 1, nil)!
CGImageDestinationAddImage(dest, processedImage, metadata)
CGImageDestinationFinalize(dest)
```

---

## Orientation Confusion

Three different orientation systems exist on Apple platforms:

### EXIF Orientation (1–8)

Used by ImageIO (`kCGImagePropertyOrientation`) and stored in image files.

| Value | Transform | Common Source |
|-------|-----------|---------------|
| 1 | None (up) | Landscape photo, home button right |
| 3 | 180° rotation | Landscape, home button left |
| 6 | 90° CW | Portrait, home button bottom |
| 8 | 90° CCW | Portrait, home button top |

### CGImagePropertyOrientation enum

Same values 1–8, same meaning. Used with `kCGImageSourceCreateThumbnailWithTransform`.

### UIImage.imageOrientation (0–7)

**Different numbering!** Do not use interchangeably with EXIF values.

| UIImage | EXIF | Transform |
|---------|------|-----------|
| `.up` (0) | 1 | None |
| `.down` (1) | 3 | 180° |
| `.right` (6→mapped) | 6 | 90° CW |
| `.left` (8→mapped) | 8 | 90° CCW |

> When creating thumbnails, set `kCGImageSourceCreateThumbnailWithTransform: true`
> to get correctly oriented output without manual rotation.

### Orientation Pitfalls

- **Duplication:** Orientation exists in IFD0 (tag 0x0112) and may be duplicated at other levels (XMP `tiff:Orientation`, thumbnail IFD1) by editing software. Ensure all copies stay in sync when editing.
- **Pixel data vs display:** The orientation tag does **not** change stored pixels — it tells viewers how to transform on display. Some software "bakes in" the rotation (rewrites pixels) and resets orientation to 1. After such a round-trip the tag is gone.
- **Thumbnail mismatch:** The embedded thumbnail in IFD1 may have a different orientation than the main image if software only updated one of them.

---

## GPS Stripping Does Not Remove MakerNote Location Data

`kCGImageMetadataShouldExcludeGPS` strips GPS data from the EXIF GPS IFD and
corresponding XMP tags, but it does **NOT** filter:
- Proprietary location data embedded in manufacturer **MakerNote** EXIF fields
- Custom XMP properties that might contain coordinates
- Apple's MakerNote which can contain location-related processing metadata

For complete location removal, strip MakerNote data as well, or write a new
image from pixels only (no metadata copy).

---

## GPS Coordinate Convention

ImageIO uses **absolute values + reference letters**, not signed decimals.

```swift
// ❌ Wrong — negative longitude won't work
let gps: [String: Any] = [
    kCGImagePropertyGPSLatitude: 37.7749,
    kCGImagePropertyGPSLongitude: -122.4194  // ImageIO ignores the sign
]

// ✓ Correct
let gps: [String: Any] = [
    kCGImagePropertyGPSLatitude: 37.7749,
    kCGImagePropertyGPSLatitudeRef: "N",
    kCGImagePropertyGPSLongitude: 122.4194,
    kCGImagePropertyGPSLongitudeRef: "W"
]
```

### Conversion helper

```swift
func gpsDict(latitude: Double, longitude: Double) -> [CFString: Any] {
    return [
        kCGImagePropertyGPSLatitude: abs(latitude),
        kCGImagePropertyGPSLatitudeRef: latitude >= 0 ? "N" : "S",
        kCGImagePropertyGPSLongitude: abs(longitude),
        kCGImagePropertyGPSLongitudeRef: longitude >= 0 ? "E" : "W"
    ]
}
```

---

## EXIF DateTime Timezone Handling

EXIF `DateTimeOriginal` is a **naive timestamp** — no timezone info.

```
"2024:06:15 14:30:00"   ← What timezone? Unknown from this field alone.
```

Modern cameras (including all iPhones) also write `OffsetTimeOriginal`:

```
"2024:06:15 14:30:00"   ← DateTimeOriginal
"+05:30"                 ← OffsetTimeOriginal (UTC offset)
```

**Always check for `OffsetTime*` keys** when reconstructing absolute timestamps.
Many third-party cameras omit these, making the datetime ambiguous.

```swift
let exif = props[kCGImagePropertyExifDictionary as String] as? [String: Any]
let dateStr = exif?[kCGImagePropertyExifDateTimeOriginal as String] as? String
let offset  = exif?[kCGImagePropertyExifOffsetTimeOriginal as String] as? String

// Combine for absolute time
let formatter = DateFormatter()
if let offset = offset {
    formatter.dateFormat = "yyyy:MM:dd HH:mm:ssxxx"
    let combined = "\(dateStr!)\(offset)"
} else {
    // Timezone unknown — assume device local or GPS-derived timezone
    formatter.dateFormat = "yyyy:MM:dd HH:mm:ss"
}
```

---

## IPTC Charset Issues

IPTC IIM uses a `CodedCharacterSet` field to indicate encoding. If missing,
the encoding is ambiguous (could be Latin-1, UTF-8, or platform-specific).

ImageIO generally assumes UTF-8 for IPTC text, which can produce garbled
output when reading files with Latin-1 encoded IPTC from older software.

> For modern workflows, prefer IPTC via XMP (`kCGImageMetadataNamespaceIPTCCore`)
> which is always UTF-8.

---

## CIImage.properties vs CGImageSource

| | `CGImageSourceCopyPropertiesAtIndex` | `CIImage.properties` |
|---|---|---|
| **Purpose** | Dedicated metadata extraction | Metadata as side effect of CIImage init |
| **Completeness** | Full EXIF, IPTC, GPS, TIFF, format-specific | Subset; primarily EXIF and orientation |
| **Pixel decode** | No | Yes (lazy, but allocated) |
| **Use when** | You need metadata only | You're already in a Core Image pipeline |

---

## Lossless Metadata Update Limitations

`CGImageDestinationCopyImageSource` can update metadata without re-encoding
pixels, but only for certain formats:

| Format | Lossless metadata update | Notes |
|--------|-------------------------|-------|
| JPEG | ✓ | Full support |
| PNG | ✓ | Full support |
| TIFF | ✓ | Full support |
| PSD | ✓ | Full support |
| HEIC/HEIF | ✗ | Must re-encode |
| WebP | ✗ | Read-only anyway |
| DNG | ✗ | Must re-encode |

---

## Thread Safety

- A **single `CGImageSource` instance** is NOT thread-safe. Do not access the
  same source concurrently from multiple threads.
- **Multiple instances** of `CGImageSource` (even for the same file) can operate
  concurrently on different threads.
- **Recommendation:** Create a separate `CGImageSource` per thread, or
  synchronize access to a shared instance.

---

## Caching Behavior

| Option | Default | Effect |
|--------|---------|--------|
| `kCGImageSourceShouldCache` | true (64-bit) | Cache decoded image in memory after first render |
| `kCGImageSourceShouldCacheImmediately` | false | Decode at creation time (not at first render) |

**Performance tip:** For background metadata extraction, leave caching off:

```swift
let options: [CFString: Any] = [
    kCGImageSourceShouldCache: false
]
let source = CGImageSourceCreateWithURL(url as CFURL, options as CFDictionary)
// Read metadata only — no pixel decode, no memory overhead
let props = CGImageSourceCopyPropertiesAtIndex(source!, 0, nil)
```

**Performance tip:** For thumbnail grids, use subsample factor:

```swift
let options: [CFString: Any] = [
    kCGImageSourceCreateThumbnailFromImageAlways: true,
    kCGImageSourceThumbnailMaxPixelSize: 200,
    kCGImageSourceSubsampleFactor: 4,  // decode at 1/4 resolution first
    kCGImageSourceCreateThumbnailWithTransform: true
]
```

---

## PhotoKit Integration

### Getting full metadata from PHAsset

`PHAsset` does not directly expose EXIF/IPTC metadata. Use the content
editing input to get a file URL, then read with ImageIO:

```swift
let options = PHContentEditingInputRequestOptions()
options.isNetworkAccessAllowed = true

asset.requestContentEditingInput(with: options) { input, info in
    guard let url = input?.fullSizeImageURL else { return }

    let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
    let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any]

    // Full EXIF, GPS, TIFF, IPTC, MakerNote available here
    let exif = props?[kCGImagePropertyExifDictionary as String]
    let gps  = props?[kCGImagePropertyGPSDictionary as String]
}
```

### PHAsset.location vs EXIF GPS

- `PHAsset.location` — `CLLocation` object, always in signed decimal degrees,
  may be reverse-geocoded or corrected by Photos
- EXIF GPS — raw camera-recorded coordinates in absolute-value + reference format

They usually agree, but can differ if the user edited the location in Photos.

### Metadata immutability

`PHAsset` metadata is immutable through PhotoKit. Edits are stored separately
in `PHAdjustmentData`. The original image metadata is always preserved.

To write modified metadata, export the image (e.g., via
`PHImageManager.requestImageDataAndOrientation`) and write a new file
using `CGImageDestination`.

---

## LangAlt Tags Created via TagCreate Are Silently Dropped

Tags created with `CGImageMetadataTagCreate(.alternateText, CFDictionary)` are
accepted by `SetTagWithPath` (returns `true`) but **silently discarded** by
`CGImageDestinationCopyImageSource`. The tag does not appear in the output
file's XMP, and no corresponding IIM field is created.

This affects `dc:title`, `dc:description`, and `dc:rights` — the three most
important IPTC fields that use the `langAlt` (`rdf:Alt` with `xml:lang`) type.

Use `SetValueWithPath` with a plain string (single-language) or parse from an
XMP snippet via `CGImageMetadataCreateFromXMPData` (multi-language) instead.
See [cgimage-metadata.md](cgimage-metadata.md#alternate-text) for working
code examples.

---

## RemoveTagWithPath Does Not Work with Merge Mode

`CGImageMetadataRemoveTagWithPath` successfully removes a tag from an
in-memory `CGMutableImageMetadata` object, but when written via
`CGImageDestinationCopyImageSource` with `kCGImageDestinationMergeMetadata:
true`, **the removed tag reappears** from the source image. Merge mode
overlays provided metadata onto the source — tags absent from the provided
metadata are preserved from the source, not removed.

To remove a tag in merge mode, set its value to `kCFNull` instead:

```swift
CGImageMetadataSetValueWithPath(metadata, nil, "photoshop:City" as CFString, kCFNull)
```

This signals to `CopyImageSource` that the tag should be actively removed
rather than preserved from the source.

---

## Clean JPEG Baseline

Even a "clean" JPEG (1×1 pixel, no metadata written) gets synthetic EXIF
fields from Apple: `PixelXDimension` and `PixelYDimension` are populated from
the image dimensions. Tests that check for empty EXIF dictionaries on clean
images will fail. Always compare against a known baseline rather than checking
`isEmpty`.

---

## IPTC IIM Date Field Sync Limitation

`photoshop:DateCreated` written as an ISO 8601 string (e.g.,
`"2024-06-15T14:30:00+02:00"`) does **not** sync to IIM `DateCreated` /
`TimeCreated` fields. Apple does not convert from ISO 8601 to the IIM format
(`YYYYMMDD` + `HHMMSS±HHMM`). The XMP tag is written correctly, but no IIM
date fields are created. If IIM date compatibility is required, write the IIM
fields separately via property dictionaries.
