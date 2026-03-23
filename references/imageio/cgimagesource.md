# CGImageSource — Reading Images & Metadata

`CGImageSource` is the read-side entry point for ImageIO. It can open any
supported image format and provide metadata, thumbnails, pixel data, and
auxiliary data (depth, gain maps, mattes) without loading the full image.

---

## Creation Functions

| Function | Purpose | iOS |
|----------|---------|-----|
| `CGImageSourceCreateWithURL(_:_:)` | Create from file URL | 4.0+ |
| `CGImageSourceCreateWithData(_:_:)` | Create from `CFData` | 4.0+ |
| `CGImageSourceCreateWithDataProvider(_:_:)` | Create from `CGDataProvider` | 4.0+ |
| `CGImageSourceCreateIncremental(_:)` | Create empty source for progressive loading | 4.0+ |

The second parameter on the first three is an options dictionary (see
[Creation & Decode Options](#creation--decode-options) below).

---

## Querying

| Function | Returns | iOS |
|----------|---------|-----|
| `CGImageSourceGetType(_:)` | UTI string of the image format (e.g. `public.jpeg`) | 4.0+ |
| `CGImageSourceGetCount(_:)` | Number of images in the source (>1 for multi-image HEIF, animated GIF, etc.) | 4.0+ |
| `CGImageSourceGetPrimaryImageIndex(_:)` | Index of the primary image (useful for HEIF where primary ≠ 0) | 12.0+ |
| `CGImageSourceGetStatus(_:)` | Overall source status (see [Status Codes](#status-codes)) | 4.0+ |
| `CGImageSourceGetStatusAtIndex(_:_:)` | Status for a specific image index | 4.0+ |
| `CGImageSourceCopyTypeIdentifiers()` | Array of all UTIs the system can **read** | 4.0+ |
| `CGImageSourceGetTypeID()` | Core Foundation type ID | 4.0+ |

---

## Properties & Metadata

| Function | Returns | iOS |
|----------|---------|-----|
| `CGImageSourceCopyProperties(_:_:)` | Container-level properties (file size, image count) | 4.0+ |
| `CGImageSourceCopyPropertiesAtIndex(_:_:_:)` | Property dictionaries for image at index (EXIF, GPS, TIFF, IPTC, etc.) | 4.0+ |
| `CGImageSourceCopyMetadataAtIndex(_:_:_:)` | `CGImageMetadata` XMP tree for image at index | 7.0+ |

### Reading property dictionaries — typical pattern

```swift
guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else { return }
guard let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any] else { return }

// Top-level keys
let width  = props[kCGImagePropertyPixelWidth as String] as? Int
let height = props[kCGImagePropertyPixelHeight as String] as? Int

// Nested dictionaries
let exif = props[kCGImagePropertyExifDictionary as String] as? [String: Any]
let gps  = props[kCGImagePropertyGPSDictionary as String] as? [String: Any]
let tiff = props[kCGImagePropertyTIFFDictionary as String] as? [String: Any]
let iptc = props[kCGImagePropertyIPTCDictionary as String] as? [String: Any]
```

> **Performance note:** `CGImageSourceCopyPropertiesAtIndex` reads metadata
> only — it does **not** decode pixel data. Safe to call on the main thread
> for metadata inspection.

---

## Image Creation

| Function | Purpose | iOS |
|----------|---------|-----|
| `CGImageSourceCreateImageAtIndex(_:_:_:)` | Decode full `CGImage` at index | 4.0+ |
| `CGImageSourceCreateThumbnailAtIndex(_:_:_:)` | Generate a thumbnail (with options) | 4.0+ |

### Thumbnail options

```swift
let options: [CFString: Any] = [
    kCGImageSourceCreateThumbnailFromImageAlways: true,
    kCGImageSourceThumbnailMaxPixelSize: 300,
    kCGImageSourceCreateThumbnailWithTransform: true  // apply EXIF orientation
]
let thumb = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary)
```

---

## Auxiliary Data

| Function | Purpose | iOS |
|----------|---------|-----|
| `CGImageSourceCopyAuxiliaryDataInfoAtIndex(_:_:_:)` | Read auxiliary data (depth, disparity, mattes, gain maps) | 11.0+ |

Returns a `CFDictionary` with these keys:
- `kCGImageAuxiliaryDataInfoData` — raw pixel/bitmap data (`CFData`)
- `kCGImageAuxiliaryDataInfoDataDescription` — format/dimensions metadata
- `kCGImageAuxiliaryDataInfoMetadata` — `CGImageMetadata` for the auxiliary data

See [auxiliary-data.md](auxiliary-data.md) for full details on data types and
workflows.

---

## Incremental Loading

For progressive image display (e.g., streaming a JPEG over the network):

```swift
let source = CGImageSourceCreateIncremental(nil)

// As data arrives — IMPORTANT: each call must provide ALL accumulated data so far, not just the new chunk:
CGImageSourceUpdateData(source, allDataSoFar as CFData, isFinal)

// Check status:
let status = CGImageSourceGetStatusAtIndex(source, 0)
if status == .statusComplete {
    let image = CGImageSourceCreateImageAtIndex(source, 0, nil)
}
```

| Function | Purpose | iOS |
|----------|---------|-----|
| `CGImageSourceUpdateData(_:_:_:)` | Feed new data to incremental source | 4.0+ |
| `CGImageSourceUpdateDataProvider(_:_:_:)` | Feed via data provider | 4.0+ |

---

## Animation

| Function | Purpose | iOS |
|----------|---------|-----|
| `CGAnimateImageAtURLWithBlock(_:_:_:)` | Animate GIF/APNG from URL | 13.0+ |
| `CGAnimateImageDataWithBlock(_:_:_:)` | Animate GIF/APNG from data | 13.0+ |

### Animation option keys

| Key | Type | Purpose |
|-----|------|---------|
| `kCGImageAnimationDelayTime` | CFNumber (seconds) | Override frame delay |
| `kCGImageAnimationLoopCount` | CFNumber | Number of loops (0 = infinite) |
| `kCGImageAnimationStartIndex` | CFNumber | Starting frame index |

> **Note:** In Xcode 11+, implicit Swift bridging is disabled for these
> functions. You may need an Objective-C wrapper or explicit bridging.
>
> For animated WebP, prefer iterating frames with `CGImageSourceGetCount` and
> `CGImageSourceCreateImageAtIndex` because Apple documents `CGAnimateImage*`
> specifically for GIF/APNG.

---

## Cache Management

| Function | Purpose | iOS |
|----------|---------|-----|
| `CGImageSourceRemoveCacheAtIndex(_:_:)` | Evict cached decoded data at index | 7.0+ |

---

## Creation & Decode Options

These option keys can be passed to creation functions and
`CGImageSourceCreateImageAtIndex` / `CGImageSourceCreateThumbnailAtIndex`:

| Key | Type | Default | Purpose | iOS |
|-----|------|---------|---------|-----|
| `kCGImageSourceTypeIdentifierHint` | CFString | — | Hint the image format UTI | 4.0+ |
| `kCGImageSourceShouldAllowFloat` | CFBoolean | false | Allow floating-point pixel components | 4.0+ |
| `kCGImageSourceShouldCache` | CFBoolean | true (64-bit) | Cache decoded image data in memory | 4.0+ |
| `kCGImageSourceShouldCacheImmediately` | CFBoolean | false | Force decode at creation (not at render) | 7.0+ |
| `kCGImageSourceSubsampleFactor` | CFNumber | — | Downsample during decode (2, 4, or 8). JPEG, HEIF, TIFF, and PNG. | 9.0+ |
| `kCGImageSourceDecodeRequest` | CFString | — | Request HDR or SDR decode (value: `kCGImageSourceDecodeToHDR` or `kCGImageSourceDecodeToSDR`) | 17.0+ |
| `kCGImageSourceDecodeToHDR` | CFString | — | Value for `kCGImageSourceDecodeRequest` to decode as HDR | 17.0+ |
| `kCGImageSourceDecodeToSDR` | CFString | — | Value for `kCGImageSourceDecodeRequest` to decode as SDR | 17.0+ |
| `kCGImageSourceGenerateImageSpecificLumaScaling` | CFBoolean | — | Generate image-specific luma scaling | 18.0+ |

### Thumbnail-specific options

| Key | Type | Default | Purpose | iOS |
|-----|------|---------|---------|-----|
| `kCGImageSourceCreateThumbnailFromImageIfAbsent` | CFBoolean | false | Create thumb from pixels if file has none | 4.0+ |
| `kCGImageSourceCreateThumbnailFromImageAlways` | CFBoolean | false | Always create from pixels (ignore embedded) | 4.0+ |
| `kCGImageSourceThumbnailMaxPixelSize` | CFNumber | — | Max width or height in pixels | 4.0+ |
| `kCGImageSourceCreateThumbnailWithTransform` | CFBoolean | false | Apply EXIF orientation to thumbnail | 4.0+ |

---

## Status Codes

Returned by `CGImageSourceGetStatus` and `CGImageSourceGetStatusAtIndex`:

| Value | Constant | Meaning |
|-------|----------|---------|
| 0 | `kCGImageStatusComplete` | Fully loaded |
| -1 | `kCGImageStatusIncomplete` | Being decoded (incremental) |
| -2 | `kCGImageStatusReadingHeader` | Reading file header |
| -3 | `kCGImageStatusUnknownType` | Unknown/unsupported format |
| -4 | `kCGImageStatusInvalidData` | Corrupt or invalid data |
| -5 | `kCGImageStatusUnexpectedEOF` | Unexpected end of file |
