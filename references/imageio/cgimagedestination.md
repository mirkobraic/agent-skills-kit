# CGImageDestination — Writing Images & Metadata

`CGImageDestination` is the write-side API for ImageIO. It creates image files
with embedded metadata, auxiliary data (depth, gain maps), and supports both
lossy re-encoding and lossless metadata-only updates.

---

## Creation Functions

| Function | Purpose | iOS |
|----------|---------|-----|
| `CGImageDestinationCreateWithURL(_:_:_:_:)` | Write to file URL | 4.0+ |
| `CGImageDestinationCreateWithData(_:_:_:_:)` | Write to `CFMutableData` | 4.0+ |
| `CGImageDestinationCreateWithDataConsumer(_:_:_:_:)` | Write to `CGDataConsumer` | 4.0+ |
| `CGImageDestinationCopyTypeIdentifiers()` | Array of all UTIs the system can **write** | 4.0+ |
| `CGImageDestinationGetTypeID()` | Core Foundation type ID | 4.0+ |

Parameters:
- `type`: UTI string (e.g. `public.jpeg`, `public.heic`, `public.png`)
- `count`: Number of images (1 for single image, >1 for multi-image HEIF/animated GIF)
- `options`: Reserved, pass `nil`

---

## Adding Images

### Basic: Add CGImage with property dictionaries

```swift
CGImageDestinationAddImage(destination, cgImage, properties as CFDictionary)
```

The `properties` dictionary can include any `kCGImageProperty*Dictionary` keys
(EXIF, GPS, TIFF, IPTC) plus destination option keys.

### From source: Lossless copy from CGImageSource

```swift
CGImageDestinationAddImageFromSource(destination, source, index, properties as CFDictionary)
```

Copies an image from an existing source. May avoid full re-decode/re-encode
depending on format compatibility.

### With XMP metadata

```swift
CGImageDestinationAddImageAndMetadata(destination, cgImage, xmpMetadata, options as CFDictionary)
```

Attaches a `CGImageMetadata` XMP tree to the image. Available since iOS 7.0.

### Lossless metadata-only update (no pixel re-encoding)

```swift
var error: Unmanaged<CFError>?
let success = CGImageDestinationCopyImageSource(
    destination,
    source,
    [
        kCGImageDestinationMetadata: xmpMetadata,
        kCGImageDestinationMergeMetadata: kCFBooleanTrue
    ] as CFDictionary,
    &error
)
```

> `kCGImageDestinationDateTime` and `kCGImageDestinationOrientation` are
> mutually exclusive with `kCGImageDestinationMetadata`. Use them in a separate
> `CopyImageSource` call that does not include `kCGImageDestinationMetadata`.

**Supported formats for lossless copy:** JPEG, PNG, PSD, TIFF.
**Not supported:** HEIC/HEIF (must re-encode).

### CopyImageSource cross-format sync behavior (observed)

When `CopyImageSource` writes XMP metadata, it does not simply modify the XMP
packet — it **regenerates binary property dictionary segments** (IPTC IIM,
EXIF, TIFF, GPS) from the final XMP state. This means writing XMP
automatically keeps property dictionaries in sync.

**What syncs (XMP → property dictionaries):**

| XMP namespace | Property dictionary | Type coercion |
|---------------|-------------------|---------------|
| `photoshop:` fields (City, Headline, Credit, etc.) | `kCGImagePropertyIPTCDictionary` | String → String |
| `Iptc4xmpCore:` fields (Location, CountryCode, etc.) | `kCGImagePropertyIPTCDictionary` | String → String |
| `dc:subject` (bag), `dc:creator` (seq) | `kCGImagePropertyIPTCDictionary` | Array → Array |
| `dc:title`, `dc:description`, `dc:rights` | `kCGImagePropertyIPTCDictionary` | LangAlt → String (x-default) |
| `exif:` fields (FNumber, ExposureTime, etc.) | `kCGImagePropertyExifDictionary` | Rational strings → numeric (e.g., `"28/10"` → `2.8`) |
| `tiff:` fields (Make, Model, Orientation, etc.) | `kCGImagePropertyTIFFDictionary` | String/rational → appropriate type |
| `exif:GPSLatitude`, `exif:GPSLongitude`, etc. | `kCGImagePropertyGPSDictionary` | DMS format → decimal + reference |
| `aux:` fields (LensModel, SerialNumber) | `kCGImagePropertyExifAuxDictionary` | Requires explicit namespace registration |

**What does NOT sync:**

| XMP field | Issue |
|-----------|-------|
| `photoshop:DateCreated` | ISO 8601 format is NOT converted to IIM `YYYYMMDD` + `HHMMSS±HHMM` format |
| `kCGImageProperty8BIMDictionary` | Not created from `photoshop:` namespace writes |
| Maker note dictionaries | Not created from any XMP writes |

**Observed on macOS 14 (arm64e).** This behavior is not explicitly guaranteed
by Apple as a cross-format contract and should be re-validated on target OS
versions.

---

## Adding Auxiliary Data

```swift
CGImageDestinationAddAuxiliaryDataInfo(destination, auxiliaryDataType, infoDictionary as CFDictionary)
```

See [auxiliary-data.md](auxiliary-data.md) for data types and dictionary keys.

---

## Setting Container Properties

```swift
CGImageDestinationSetProperties(destination, properties as CFDictionary)
```

Sets properties that apply to all images (e.g., loop count for animated GIF).

---

## Finalizing

```swift
let success = CGImageDestinationFinalize(destination)
```

**Must be called** after adding all images. Returns `true` on success.
After finalization the destination cannot be reused.

---

## All Functions Summary

| Function | iOS | Purpose |
|----------|-----|---------|
| `CGImageDestinationCreateWithURL` | 4.0+ | Create for file output |
| `CGImageDestinationCreateWithData` | 4.0+ | Create for data output |
| `CGImageDestinationCreateWithDataConsumer` | 4.0+ | Create for consumer output |
| `CGImageDestinationAddImage` | 4.0+ | Add CGImage with properties |
| `CGImageDestinationAddImageFromSource` | 4.0+ | Add image from CGImageSource |
| `CGImageDestinationAddImageAndMetadata` | 7.0+ | Add CGImage with XMP metadata |
| `CGImageDestinationCopyImageSource` | 7.0+ | Lossless copy with metadata merge |
| `CGImageDestinationAddAuxiliaryDataInfo` | 11.0+ | Add depth/matte/gain map data |
| `CGImageDestinationSetProperties` | 4.0+ | Set container-level properties |
| `CGImageDestinationFinalize` | 4.0+ | Flush and finalize output |
| `CGImageDestinationCopyTypeIdentifiers` | 4.0+ | List writable UTIs |
| `CGImageDestinationGetTypeID` | 4.0+ | Core Foundation type ID |

---

## Destination Option Keys

### Compression & Sizing

| Key | Type | Purpose | iOS |
|-----|------|---------|-----|
| `kCGImageDestinationLossyCompressionQuality` | CFNumber (0.0–1.0) | JPEG/HEIF quality (1.0 = lossless if supported) | 4.0+ |
| `kCGImageDestinationImageMaxPixelSize` | CFNumber | Scale to fit max dimension | 8.0+ |
| `kCGImageDestinationEmbedThumbnail` | CFBoolean | Embed thumbnail in JPEG/HEIF | 8.0+ |

### Color

| Key | Type | Purpose | iOS |
|-----|------|---------|-----|
| `kCGImageDestinationBackgroundColor` | CGColor | Composite alpha onto this color | 4.0+ |
| `kCGImageDestinationOptimizeColorForSharing` | CFBoolean | Convert to sRGB for legacy compatibility | 9.3+ |

### Metadata Control (for `CopyImageSource`)

| Key | Type | Purpose | iOS |
|-----|------|---------|-----|
| `kCGImageDestinationMetadata` | CGImageMetadata | XMP metadata to apply. See merge vs replace behavior below | 7.0+ |
| `kCGImageDestinationMergeMetadata` | CFBoolean | Merge with existing (vs replace). See merge vs replace behavior below | 7.0+ |
| `kCGImageMetadataShouldExcludeXMP` | CFBoolean | Strip XMP packets (preserves EXIF/IPTC) | 7.0+ |
| `kCGImageMetadataShouldExcludeGPS` | CFBoolean | Strip GPS/location data (**does NOT filter proprietary location data in MakerNote**) | 8.0+ |
| `kCGImageDestinationDateTime` | CFString or CFData | Set/update creation datetime (EXIF DateTime or ISO 8601 format). **Mutually exclusive with `kCGImageDestinationMetadata`** | 7.0+ |
| `kCGImageDestinationOrientation` | CFNumber (1–8) | Set EXIF orientation. **Mutually exclusive with `kCGImageDestinationMetadata`** | 7.0+ |

### HDR / Gain Map (iOS 17+)

| Key | Type | Purpose | iOS |
|-----|------|---------|-----|
| `kCGImageDestinationPreserveGainMap` | CFBoolean | Preserve HDR gain map (also scales gain map if `ImageMaxPixelSize` used) | 14.1+ |
| `kCGImageDestinationEncodeRequest` | CFString | HDR encoding preference (value: one of the EncodeToXxx constants below) | 18.0+ |
| `kCGImageDestinationEncodeRequestOptions` | CFDictionary | Options for the encode request | 18.0+ |
| `kCGImageDestinationEncodeToSDR` | CFString | Value for EncodeRequest: encode as SDR | 18.0+ |
| `kCGImageDestinationEncodeToISOHDR` | CFString | Value for EncodeRequest: encode ISO 21496-1 HDR | 18.0+ |
| `kCGImageDestinationEncodeToISOGainmap` | CFString | Value for EncodeRequest: encode ISO gain map | 18.0+ |
| `kCGImageDestinationEncodeBaseIsSDR` | CFBoolean | Whether the base image is SDR | 18.0+ |
| `kCGImageDestinationEncodeTonemapMode` | CFString | Tonemap mode for HDR encoding | 18.0+ |

### Merge vs Replace Behavior

The `kCGImageDestinationMergeMetadata` flag controls how `CopyImageSource`
handles existing metadata. The two modes have very different consequences:

**Merge mode** (`kCFBooleanTrue`):

| Aspect | Behavior |
|--------|----------|
| Written XMP fields | Updated to new values |
| Unwritten XMP fields | **Preserved** from source image |
| IPTC IIM dictionary | **Regenerated** from final merged XMP state |
| EXIF/TIFF/GPS dicts | Preserved from source image |
| Tag removal | `RemoveTagWithPath` does not work — removed tags reappear from source. Use `SetValueWithPath` with `kCFNull` to remove a tag |

> IIM regeneration in merge mode can cause subtle data loss: if a field exists
> in old IIM but has no corresponding XMP tag in the merged result, that IIM
> field will be lost. Apple rebuilds IIM entirely from XMP, it does not merge
> IIM separately.

**Replace mode** (`kCFBooleanFalse`):

| Aspect | Behavior |
|--------|----------|
| Written XMP fields | Written to output |
| Unwritten XMP fields | **Stripped** — only written tags survive |
| IPTC IIM dictionary | Regenerated from written XMP only |
| EXIF/TIFF/GPS dicts | **Stripped** — binary segments do not survive replace mode |

> Replace mode is highly destructive — it strips EXIF, TIFF, and GPS binary
> segments in addition to unwritten XMP. It is essentially a metadata reset.
> Only use when intentionally overwriting all metadata.

**Observed on macOS 14 (arm64e).** This behavior is not explicitly guaranteed
by Apple as a cross-format contract and should be re-validated on target OS
versions.

---

## Common Writing Patterns

### Pattern 1 — Write JPEG with EXIF + GPS metadata

```swift
let dest = CGImageDestinationCreateWithURL(url as CFURL, kUTTypeJPEG, 1, nil)!

let properties: [CFString: Any] = [
    kCGImageDestinationLossyCompressionQuality: 0.85,
    kCGImagePropertyExifDictionary: [
        kCGImagePropertyExifDateTimeOriginal: "2024:06:15 14:30:00",
        kCGImagePropertyExifLensModel: "iPhone 15 Pro back triple camera 6.765mm f/1.78"
    ],
    kCGImagePropertyGPSDictionary: [
        kCGImagePropertyGPSLatitude: 37.7749,
        kCGImagePropertyGPSLatitudeRef: "N",
        kCGImagePropertyGPSLongitude: 122.4194,
        kCGImagePropertyGPSLongitudeRef: "W"
    ]
]

CGImageDestinationAddImage(dest, cgImage, properties as CFDictionary)
CGImageDestinationFinalize(dest)
```

### Pattern 2 — Lossless metadata update (JPEG)

```swift
let source = CGImageSourceCreateWithURL(inputURL as CFURL, nil)!
let dest = CGImageDestinationCreateWithURL(outputURL as CFURL, CGImageSourceGetType(source)!, 1, nil)!

let xmp = CGImageMetadataCreateMutable()
// ... add tags to xmp ...

let options: [CFString: Any] = [
    kCGImageDestinationMetadata: xmp,
    kCGImageDestinationMergeMetadata: kCFBooleanTrue!
]

var error: Unmanaged<CFError>?
CGImageDestinationCopyImageSource(dest, source, options as CFDictionary, &error)
```

### Pattern 3 — Strip all metadata

```swift
let dest = CGImageDestinationCreateWithURL(url as CFURL, kUTTypeJPEG, 1, nil)!
// Pass empty dictionary — no metadata keys → stripped output
CGImageDestinationAddImage(dest, cgImage, [:] as CFDictionary)
CGImageDestinationFinalize(dest)
```

### Pattern 4 — Strip GPS only (lossless)

```swift
let options: [CFString: Any] = [
    kCGImageMetadataShouldExcludeGPS: kCFBooleanTrue!
]
var error: Unmanaged<CFError>?
CGImageDestinationCopyImageSource(dest, source, options as CFDictionary, &error)
```
