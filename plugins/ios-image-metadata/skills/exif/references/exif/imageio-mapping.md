# EXIF in ImageIO — Apple Framework Integration

> Part of [EXIF Reference](README.md)

How Apple's ImageIO framework surfaces EXIF data: property dictionary keys, XMP
namespace constants, bridge functions, auto-synthesis, auxiliary dictionary, and
ImageIO-specific pitfalls. For the pure EXIF standard, see
[`technical-structure.md`](technical-structure.md) and
[`tag-reference.md`](tag-reference.md).

---

## Property Dictionaries

EXIF data is accessed through two property sub-dictionaries returned by
`CGImageSourceCopyPropertiesAtIndex`:

| Dictionary | Constant | iOS | Content |
|------------|----------|-----|---------|
| **EXIF** | `kCGImagePropertyExifDictionary` | 4.0+ | ~65 keys covering core Exif IFD tags |
| **EXIF Auxiliary** | `kCGImagePropertyExifAuxDictionary` | 4.0+ | 9 keys for supplementary lens/camera data |

```swift
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any]

// EXIF dictionary
let exif = props?[kCGImagePropertyExifDictionary as String] as? [String: Any]
let exposure = exif?[kCGImagePropertyExifExposureTime as String] as? Double

// EXIF Auxiliary dictionary
let exifAux = props?[kCGImagePropertyExifAuxDictionary as String] as? [String: Any]
let lensModel = exifAux?[kCGImagePropertyExifAuxLensModel as String] as? String
```

> **IFD0 tags live in the TIFF dictionary.** Make, Model, Orientation, DateTime,
> Artist, Copyright, and Software are IFD0 tags accessed via
> `kCGImagePropertyTIFFDictionary`, not the EXIF dictionary.

---

## Complete ImageIO Key → EXIF Tag Mapping

### Camera & Exposure

| ImageIO Key | EXIF Tag | Type | Notes |
|-------------|----------|------|-------|
| `kCGImagePropertyExifExposureTime` | 0x829a ExposureTime | Rational | Seconds (e.g., 0.004 = 1/250s) |
| `kCGImagePropertyExifFNumber` | 0x829d FNumber | Rational | F-stop |
| `kCGImagePropertyExifExposureProgram` | 0x8822 ExposureProgram | Short | 0–8 enum. See [`tag-reference.md`](tag-reference.md#camera--exposure) |
| `kCGImagePropertyExifISOSpeedRatings` | 0x8827 ISOSpeedRatings | Short[] | Array of ISO values |
| `kCGImagePropertyExifSensitivityType` | 0x8830 SensitivityType | Short | ISO 12232 parameter type |
| `kCGImagePropertyExifStandardOutputSensitivity` | 0x8831 StandardOutputSensitivity | Long | SOS value |
| `kCGImagePropertyExifRecommendedExposureIndex` | 0x8832 RecommendedExposureIndex | Long | REI value |
| `kCGImagePropertyExifISOSpeed` | 0x8833 ISOSpeed | Long | ISO speed |
| `kCGImagePropertyExifISOSpeedLatitudeyyy` | 0x8834 ISOSpeedLatitudeyyy | Long | ISO latitude yyy |
| `kCGImagePropertyExifISOSpeedLatitudezzz` | 0x8835 ISOSpeedLatitudezzz | Long | ISO latitude zzz |
| `kCGImagePropertyExifExposureIndex` | 0xa215 ExposureIndex | Rational | Camera exposure index |
| `kCGImagePropertyExifExposureMode` | 0xa402 ExposureMode | Short | 0=Auto, 1=Manual, 2=Auto bracket |
| `kCGImagePropertyExifExposureBiasValue` | 0x9204 ExposureBiasValue | SRational | EV compensation |
| `kCGImagePropertyExifSpectralSensitivity` | 0x8824 SpectralSensitivity | ASCII | Per ASTM E-1417 |
| `kCGImagePropertyExifOECF` | 0x8828 OECF | Undefined | Opto-Electronic Conversion Function |

### Brightness, Metering & Flash

| ImageIO Key | EXIF Tag | Type | Notes |
|-------------|----------|------|-------|
| `kCGImagePropertyExifShutterSpeedValue` | 0x9201 ShutterSpeedValue | SRational | APEX. Time = 2^(-value) |
| `kCGImagePropertyExifApertureValue` | 0x9202 ApertureValue | Rational | APEX. FN = 2^(value/2) |
| `kCGImagePropertyExifBrightnessValue` | 0x9203 BrightnessValue | SRational | APEX. -1 = unknown |
| `kCGImagePropertyExifMaxApertureValue` | 0x9205 MaxApertureValue | Rational | Smallest F-number (APEX) |
| `kCGImagePropertyExifMeteringMode` | 0x9207 MeteringMode | Short | 0–6, 255 enum |
| `kCGImagePropertyExifLightSource` | 0x9208 LightSource | Short | 0–24, 255 enum |
| `kCGImagePropertyExifFlash` | 0x9209 Flash | Short | Bitfield. See [`tag-reference.md`](tag-reference.md#flash-bitfield-decode) |
| `kCGImagePropertyExifFlashEnergy` | 0xa20b FlashEnergy | Rational | BCPS |
| `kCGImagePropertyExifGainControl` | 0xa407 GainControl | Short | 0–4 enum |
| `kCGImagePropertyExifSubjectDistance` | 0x9206 SubjectDistance | Rational | Meters |
| `kCGImagePropertyExifSubjectArea` | 0x9214 SubjectArea | Short[] | 2–4 values |
| `kCGImagePropertyExifSubjectLocation` | 0xa214 SubjectLocation | Short[2] | (x, y) |
| `kCGImagePropertyExifSensingMethod` | 0xa217 SensingMethod | Short | 1–8 enum |
| `kCGImagePropertyExifSpatialFrequencyResponse` | 0xa20c SpatialFrequencyResponse | Undefined | SFR table |
| `kCGImagePropertyExifDeviceSettingDescription` | 0xa40b DeviceSettingDescription | Undefined | Device settings |
| `kCGImagePropertyExifCFAPattern` | 0xa302 CFAPattern | Undefined | Color filter array |

### Focal Length & Lens

| ImageIO Key | EXIF Tag | Type | Notes |
|-------------|----------|------|-------|
| `kCGImagePropertyExifFocalLength` | 0x920a FocalLength | Rational | mm |
| `kCGImagePropertyExifFocalLenIn35mmFilm` | 0xa405 FocalLengthIn35mmFilm | Short | 35mm equivalent. 0=unknown |
| `kCGImagePropertyExifLensSpecification` | 0xa432 LensSpecification | Rational[4] | [MinFL, MaxFL, MinFN@MinFL, MinFN@MaxFL] |
| `kCGImagePropertyExifLensMake` | 0xa433 LensMake | ASCII | Manufacturer |
| `kCGImagePropertyExifLensModel` | 0xa434 LensModel | ASCII | Model name/number |
| `kCGImagePropertyExifLensSerialNumber` | 0xa435 LensSerialNumber | ASCII | Serial number |
| `kCGImagePropertyExifFocalPlaneXResolution` | 0xa20e FocalPlaneXResolution | Rational | Sensor pixel density (X) |
| `kCGImagePropertyExifFocalPlaneYResolution` | 0xa20f FocalPlaneYResolution | Rational | Sensor pixel density (Y) |
| `kCGImagePropertyExifFocalPlaneResolutionUnit` | 0xa210 FocalPlaneResolutionUnit | Short | 1=none, 2=inch, 3=cm |

### Image Dimensions & Color

| ImageIO Key | EXIF Tag | Type | Notes |
|-------------|----------|------|-------|
| `kCGImagePropertyExifPixelXDimension` | 0xa002 PixelXDimension | Long | Valid width |
| `kCGImagePropertyExifPixelYDimension` | 0xa003 PixelYDimension | Long | Valid height |
| `kCGImagePropertyExifColorSpace` | 0xa001 ColorSpace | Short | 1=sRGB, 65535=uncalibrated |
| `kCGImagePropertyExifComponentsConfiguration` | 0x9101 ComponentsConfiguration | Undefined[4] | Channel order |
| `kCGImagePropertyExifCompressedBitsPerPixel` | 0x9102 CompressedBitsPerPixel | Rational | Compression ratio |
| `kCGImagePropertyExifGamma` | 0xa500 Gamma | Rational | Gamma coefficient |

### Date & Time

| ImageIO Key | EXIF Tag | Type | Notes |
|-------------|----------|------|-------|
| `kCGImagePropertyExifDateTimeOriginal` | 0x9003 DateTimeOriginal | ASCII | Capture time |
| `kCGImagePropertyExifDateTimeDigitized` | 0x9004 DateTimeDigitized | ASCII | Digitization time |
| `kCGImagePropertyExifSubsecTime` | 0x9290 SubSecTime | ASCII | Fractional seconds for TIFF DateTime |
| `kCGImagePropertyExifSubsecTimeOriginal` | 0x9291 SubSecTimeOriginal | ASCII | Fractional seconds for DateTimeOriginal |
| `kCGImagePropertyExifSubsecTimeDigitized` | 0x9292 SubSecTimeDigitized | ASCII | Fractional seconds for DateTimeDigitized |
| `kCGImagePropertyExifOffsetTime` | 0x9010 OffsetTime | ASCII | UTC offset for TIFF DateTime |
| `kCGImagePropertyExifOffsetTimeOriginal` | 0x9011 OffsetTimeOriginal | ASCII | UTC offset for DateTimeOriginal |
| `kCGImagePropertyExifOffsetTimeDigitized` | 0x9012 OffsetTimeDigitized | ASCII | UTC offset for DateTimeDigitized |

#### Constructing a Full Timestamp

```swift
let exif = props[kCGImagePropertyExifDictionary as String] as? [String: Any]

let dateStr = exif?[kCGImagePropertyExifDateTimeOriginal as String] as? String
// "2024:06:15 14:30:00"

let subsec = exif?[kCGImagePropertyExifSubsecTimeOriginal as String] as? String
// "234"

let offset = exif?[kCGImagePropertyExifOffsetTimeOriginal as String] as? String
// "+05:30"

// Combine: "2024:06:15 14:30:00.234+05:30"
guard let dateStr = dateStr else { return nil }

var full = dateStr
if let subsec = subsec {
    full += ".\(subsec)"
}

let formatter = DateFormatter()
if let offset = offset {
    full += offset
    formatter.dateFormat = subsec != nil
        ? "yyyy:MM:dd HH:mm:ss.SSSxxx"
        : "yyyy:MM:dd HH:mm:ssxxx"
} else {
    // Timezone unknown — assume device local or GPS-derived timezone
    formatter.dateFormat = subsec != nil
        ? "yyyy:MM:dd HH:mm:ss.SSS"
        : "yyyy:MM:dd HH:mm:ss"
}

let date = formatter.date(from: full)
```

### Scene & Processing

| ImageIO Key | EXIF Tag | Type | Notes |
|-------------|----------|------|-------|
| `kCGImagePropertyExifWhiteBalance` | 0xa403 WhiteBalance | Short | 0=Auto, 1=Manual |
| `kCGImagePropertyExifDigitalZoomRatio` | 0xa404 DigitalZoomRatio | Rational | 0=not used |
| `kCGImagePropertyExifSceneCaptureType` | 0xa406 SceneCaptureType | Short | 0–3 enum |
| `kCGImagePropertyExifSceneType` | 0xa301 SceneType | Undefined | 1=directly photographed |
| `kCGImagePropertyExifSubjectDistRange` | 0xa40c SubjectDistanceRange | Short | 0–3 enum |
| `kCGImagePropertyExifContrast` | 0xa408 Contrast | Short | 0–2 enum |
| `kCGImagePropertyExifSaturation` | 0xa409 Saturation | Short | 0–2 enum |
| `kCGImagePropertyExifSharpness` | 0xa40a Sharpness | Short | 0–2 enum |
| `kCGImagePropertyExifCustomRendered` | 0xa401 CustomRendered | Short | 0=Normal, 1=Custom |
| `kCGImagePropertyExifFileSource` | 0xa300 FileSource | Undefined | 1–3 enum |
| `kCGImagePropertyExifRelatedSoundFile` | 0xa004 RelatedSoundFile | ASCII | Audio file name |

### Composite Images (EXIF 2.32+)

| ImageIO Key | EXIF Tag | Type | Notes |
|-------------|----------|------|-------|
| `kCGImagePropertyExifCompositeImage` | 0xa460 CompositeImage | Short | 0–3 enum |
| `kCGImagePropertyExifSourceImageNumberOfCompositeImage` | 0xa461 SourceImageNumberOfCompositeImage | Short[2] | [total, used] |
| `kCGImagePropertyExifSourceExposureTimesOfCompositeImage` | 0xa462 SourceExposureTimesOfCompositeImage | Undefined | Exposure times |

### Version, Identity & Misc

| ImageIO Key | EXIF Tag | Type | Notes |
|-------------|----------|------|-------|
| `kCGImagePropertyExifVersion` | 0x9000 ExifVersion | Undefined[4] | ImageIO returns as CFArray (e.g., [2,3,2]) |
| `kCGImagePropertyExifFlashPixVersion` | 0xa000 FlashpixVersion | Undefined[4] | Usually "0100" |
| `kCGImagePropertyExifMakerNote` | 0x927c MakerNote | Undefined | Opaque vendor blob. See [`makernote.md`](makernote.md) |
| `kCGImagePropertyExifUserComment` | 0x9286 UserComment | Undefined | 8-byte charset prefix + text |
| `kCGImagePropertyExifImageUniqueID` | 0xa420 ImageUniqueID | ASCII | 128-bit hex string |
| `kCGImagePropertyExifCameraOwnerName` | 0xa430 CameraOwnerName | ASCII | Owner name |
| `kCGImagePropertyExifBodySerialNumber` | 0xa431 BodySerialNumber | ASCII | Body serial |
| `kCGImagePropertyExifInteroperabilityDictionary` | — | CFDictionary | Interoperability IFD as sub-dictionary |

---

## EXIF Auxiliary Dictionary

`kCGImagePropertyExifAuxDictionary` stores supplementary camera/lens data that
originated in Adobe's `aux:` XMP namespace before being partially standardized
in EXIF 2.3.

| ImageIO Key | Type | Description |
|-------------|------|-------------|
| `kCGImagePropertyExifAuxLensInfo` | CFArray (4 Rationals) | [MinFL, MaxFL, MinFN@MinFL, MinFN@MaxFL] |
| `kCGImagePropertyExifAuxLensModel` | CFString | Lens model name |
| `kCGImagePropertyExifAuxLensID` | CFNumber | Numeric lens identifier (vendor-specific) |
| `kCGImagePropertyExifAuxLensSerialNumber` | CFString | Lens serial number |
| `kCGImagePropertyExifAuxSerialNumber` | CFString | Camera body serial number |
| `kCGImagePropertyExifAuxImageNumber` | CFNumber | Image sequence number |
| `kCGImagePropertyExifAuxFlashCompensation` | CFNumber | Flash exposure compensation |
| `kCGImagePropertyExifAuxOwnerName` | CFString | Camera owner |
| `kCGImagePropertyExifAuxFirmware` | CFString | Camera firmware version |

### ExifAux ↔ Standard EXIF 2.3+ Overlap

Several ExifAux fields were later standardized. When both exist, prefer the
standard EXIF key:

| ExifAux Key | Standard EXIF Key (2.3+) | Precedence |
|-------------|--------------------------|------------|
| `kCGImagePropertyExifAuxLensInfo` | `kCGImagePropertyExifLensSpecification` (0xa432) | Standard EXIF |
| `kCGImagePropertyExifAuxLensModel` | `kCGImagePropertyExifLensModel` (0xa434) | Standard EXIF |
| `kCGImagePropertyExifAuxLensSerialNumber` | `kCGImagePropertyExifLensSerialNumber` (0xa435) | Standard EXIF |
| `kCGImagePropertyExifAuxSerialNumber` | `kCGImagePropertyExifBodySerialNumber` (0xa431) | Standard EXIF |
| `kCGImagePropertyExifAuxOwnerName` | `kCGImagePropertyExifCameraOwnerName` (0xa430) | Standard EXIF |

Tags with no standard equivalent: `LensID`, `FlashCompensation`, `ImageNumber`,
`Firmware`.

---

## Orientation in ImageIO

EXIF orientation (tag 0x0112) appears in three places:

| Access Method | Key / Path |
|--------------|------------|
| IFD0/TIFF dictionary | `kCGImagePropertyTIFFOrientation` |
| Top-level property (duplicated) | `kCGImagePropertyOrientation` |
| XMP | `tiff:Orientation` |

### ImageIO Orientation Constants

| Constant | Value | EXIF Orientation |
|----------|-------|-----------------|
| `kCGImagePropertyOrientationUp` | 1 | Top-left (normal) |
| `kCGImagePropertyOrientationUpMirrored` | 2 | Top-right (H flip) |
| `kCGImagePropertyOrientationDown` | 3 | Bottom-right (180) |
| `kCGImagePropertyOrientationDownMirrored` | 4 | Bottom-left (V flip) |
| `kCGImagePropertyOrientationLeftMirrored` | 5 | Left-top |
| `kCGImagePropertyOrientationRight` | 6 | Right-top (90 CW) |
| `kCGImagePropertyOrientationRightMirrored` | 7 | Right-bottom |
| `kCGImagePropertyOrientationLeft` | 8 | Left-bottom (90 CCW) |

### Thumbnail Auto-Transform

Set `kCGImageSourceCreateThumbnailWithTransform: true` when creating thumbnails
to get correctly oriented output without manual rotation.

### UIImage Orientation Warning

`UIImage.imageOrientation` uses a **different numbering scheme** than EXIF/ImageIO.
Do not use interchangeably.

| UIImage Orientation | UIImage Raw Value | EXIF Value | Transform |
|--------------------|-------------------|------------|-----------|
| `.up` | 0 | 1 | Normal |
| `.upMirrored` | 4 | 2 | Horizontal flip |
| `.down` | 1 | 3 | 180° |
| `.downMirrored` | 5 | 4 | Vertical flip |
| `.leftMirrored` | 6 | 5 | Transpose |
| `.right` | 3 | 6 | 90° CW |
| `.rightMirrored` | 7 | 7 | Transverse |
| `.left` | 2 | 8 | 90° CCW |

See `../imageio/pitfalls.md` for the full orientation confusion breakdown.

---

## MakerNote Access

ImageIO exposes MakerNote as an opaque `CFData` blob via
`kCGImagePropertyExifMakerNote`. ImageIO also exposes maker-specific
dictionaries for multiple vendors:

- `kCGImagePropertyMakerAppleDictionary` (iOS 7.0+) — contains burst mode info,
  HDR flags, media group UUID, acceleration vector, focus data, content identifier
- `kCGImagePropertyMakerCanonDictionary`
- `kCGImagePropertyMakerNikonDictionary`
- `kCGImagePropertyMakerFujiDictionary`
- `kCGImagePropertyMakerOlympusDictionary`
- `kCGImagePropertyMakerPentaxDictionary`

For vendors without ImageIO dictionary coverage, use external libraries.

See [`makernote.md`](makernote.md) for MakerNote structure and
`../makers/` for vendor-specific keys.

---

## XMP Tree Access

EXIF data is also accessible through the `CGImageMetadata` XMP tree API. Four
XMP namespaces cover EXIF content:

| ImageIO Constant | Namespace URI | Prefix | Scope |
|-----------------|---------------|--------|-------|
| `kCGImageMetadataNamespaceExif` | `http://ns.adobe.com/exif/1.0/` | `exif` | Core Exif IFD tags |
| `kCGImageMetadataNamespaceExifAux` | `http://ns.adobe.com/exif/1.0/aux/` | `aux` | Auxiliary lens/camera data |
| `kCGImageMetadataNamespaceExifEX` | `http://cipa.jp/exif/1.0/` | `exifEX` | EXIF 2.3+ extension tags |
| `kCGImageMetadataNamespaceTIFF` | `http://ns.adobe.com/tiff/1.0/` | `tiff` | IFD0 tags (Make, Model, etc.) |

All four are automatically registered by Apple — no manual registration needed.

### Bridge Functions

Convert between property dictionary keys and XMP tags:

```swift
// Property dict key → XMP tag
let tag = CGImageMetadataCopyTagMatchingImageProperty(
    metadata,
    kCGImagePropertyExifDictionary,
    kCGImagePropertyExifDateTimeOriginal
)
// Returns the XMP tag at path "exif:DateTimeOriginal"

// Set EXIF value via property naming → writes XMP
CGImageMetadataSetValueMatchingImageProperty(
    mutableMetadata,
    kCGImagePropertyExifDictionary,
    kCGImagePropertyExifUserComment,
    "Processed with MyApp" as CFTypeRef
)
```

### Read-Side Auto-Synthesis

Apple synthesizes metadata across APIs on read. An image with only EXIF binary
data (no XMP packet) will still return XMP tags via
`CGImageSourceCopyMetadataAtIndex` — Apple promotes EXIF to synthetic XMP. The
reverse also works: XMP-only data appears in property dictionaries. Both read
paths see metadata from both sources.

### Complete ImageIO Key → XMP Path Tables

See [`xmp-mapping.md`](xmp-mapping.md) for the complete EXIF tag → XMP path
mapping tables (organized by `exif:`, `exifEX:`, `aux:`, and `tiff:`
namespaces).

---

## ImageIO-Specific Pitfalls

> **Guidance, not absolute truth.** Behavior can change across OS versions.
> Always verify against your target OS and test with real images.

### UIImage Strips All Metadata

`UIImage` discards all EXIF, GPS, IPTC, and other metadata (retains only
orientation). Always use `CGImageSource`/`CGImageDestination` when metadata
matters. See `../imageio/pitfalls.md` for details and code examples.

### Deprecated Misspelling

`kCGImagePropertyExifSubsecTimeOrginal` (note: "Orginal") is deprecated.
Use `kCGImagePropertyExifSubsecTimeOriginal` (correct spelling).

### Synthetic Properties on Clean Images

Even a "clean" image (no metadata written) gets synthetic `PixelXDimension`
and `PixelYDimension` from ImageIO. Tests checking for empty EXIF dictionaries
will fail. Compare against known baselines instead.

### Environmental Tags Have No ImageIO Keys

Temperature, Humidity, Pressure, WaterDepth, Acceleration, and
CameraElevationAngle (EXIF 2.31+) have no `kCGImagePropertyExif*` constants.
Access via the XMP tree API using `exif:` namespace paths.

### EXIF 3.0 Identity Tags Have No ImageIO Keys

ImageTitle, Photographer, ImageEditor, CameraFirmware, RAWDevelopingSoftware,
ImageEditingSoftware, and MetadataEditingSoftware (EXIF 3.0) have no
`kCGImagePropertyExif*` constants yet. May require future iOS versions or
direct XMP access.

### ExifAux vs Standard EXIF Lens Tag Duplication

Both `kCGImagePropertyExifAuxLensModel` and `kCGImagePropertyExifLensModel`
may contain lens data. Prefer the standard EXIF key when both exist. See the
[overlap table](#exifaux--standard-exif-23-overlap) above.

### MakerNote Preservation

Use `CGImageDestinationCopyImageSource` for lossless metadata updates to avoid
breaking MakerNote internal offsets. See [`makernote.md`](makernote.md).

### GPS Stripping Limitations

`kCGImageMetadataShouldExcludeGPS` strips GPS from the GPS IFD and XMP, but
does NOT filter proprietary location data in MakerNote fields. For complete
location removal, also strip MakerNote or create a new image from pixels only.
