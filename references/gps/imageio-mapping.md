# ImageIO GPS Mapping

> Part of [GPS Reference](README.md)

How Apple's ImageIO framework exposes GPS IFD data: all
`kCGImagePropertyGPS*` constants, reading and writing GPS metadata in Swift,
`PHAsset.location` vs EXIF GPS, and how to strip location data.

---

## All kCGImagePropertyGPS* Constants

Complete list of GPS dictionary keys defined in `CGImageProperties.h`. All
are available since iOS 4.0 unless noted.

### Coordinates

| ImageIO Constant | CFType | EXIF Tag | Notes |
|------------------|--------|----------|-------|
| `kCGImagePropertyGPSLatitude` | CFNumber (Double) | 0x0002 GPSLatitude | Absolute value in decimal degrees. ImageIO converts three RATIONALs to one Double. |
| `kCGImagePropertyGPSLatitudeRef` | CFString | 0x0001 GPSLatitudeRef | `"N"` or `"S"` |
| `kCGImagePropertyGPSLongitude` | CFNumber (Double) | 0x0004 GPSLongitude | Absolute value in decimal degrees |
| `kCGImagePropertyGPSLongitudeRef` | CFString | 0x0003 GPSLongitudeRef | `"E"` or `"W"` |
| `kCGImagePropertyGPSAltitude` | CFNumber (Double) | 0x0006 GPSAltitude | Meters (always positive) |
| `kCGImagePropertyGPSAltitudeRef` | CFNumber (Int) | 0x0005 GPSAltitudeRef | 0=above, 1=below sea level |

### Timestamps

| ImageIO Constant | CFType | EXIF Tag | Notes |
|------------------|--------|----------|-------|
| `kCGImagePropertyGPSTimeStamp` | CFString | 0x0007 GPSTimeStamp | `"HH:MM:SS.SS"` format. ImageIO converts from/to three RATIONALs transparently. |
| `kCGImagePropertyGPSDateStamp` | CFString | 0x001D GPSDateStamp | `"YYYY:MM:DD"` (colon-separated, not hyphens) |

### Speed and Movement

| ImageIO Constant | CFType | EXIF Tag | Notes |
|------------------|--------|----------|-------|
| `kCGImagePropertyGPSSpeed` | CFNumber (Double) | 0x000D GPSSpeed | Speed value in the unit specified by SpeedRef |
| `kCGImagePropertyGPSSpeedRef` | CFString | 0x000C GPSSpeedRef | `"K"` km/h, `"M"` mph, `"N"` knots |
| `kCGImagePropertyGPSTrack` | CFNumber (Double) | 0x000F GPSTrack | Direction of movement (0--359.99 degrees) |
| `kCGImagePropertyGPSTrackRef` | CFString | 0x000E GPSTrackRef | `"T"` true north, `"M"` magnetic north |

### Image Direction

| ImageIO Constant | CFType | EXIF Tag | Notes |
|------------------|--------|----------|-------|
| `kCGImagePropertyGPSImgDirection` | CFNumber (Double) | 0x0011 GPSImgDirection | Direction camera faces (0--359.99 degrees) |
| `kCGImagePropertyGPSImgDirectionRef` | CFString | 0x0010 GPSImgDirectionRef | `"T"` true north, `"M"` magnetic north |

### Destination

| ImageIO Constant | CFType | EXIF Tag | Notes |
|------------------|--------|----------|-------|
| `kCGImagePropertyGPSDestLatitude` | CFNumber (Double) | 0x0014 GPSDestLatitude | Absolute decimal degrees |
| `kCGImagePropertyGPSDestLatitudeRef` | CFString | 0x0013 GPSDestLatitudeRef | `"N"` or `"S"` |
| `kCGImagePropertyGPSDestLongitude` | CFNumber (Double) | 0x0016 GPSDestLongitude | Absolute decimal degrees |
| `kCGImagePropertyGPSDestLongitudeRef` | CFString | 0x0015 GPSDestLongitudeRef | `"E"` or `"W"` |
| `kCGImagePropertyGPSDestBearing` | CFNumber (Double) | 0x0018 GPSDestBearing | Degrees (0--359.99) |
| `kCGImagePropertyGPSDestBearingRef` | CFString | 0x0017 GPSDestBearingRef | `"T"` or `"M"` |
| `kCGImagePropertyGPSDestDistance` | CFNumber (Double) | 0x001A GPSDestDistance | Distance value |
| `kCGImagePropertyGPSDestDistanceRef` | CFString | 0x0019 GPSDestDistanceRef | `"K"` km, `"M"` miles, `"N"` naut. mi |

### Quality and System

| ImageIO Constant | CFType | EXIF Tag | Notes |
|------------------|--------|----------|-------|
| `kCGImagePropertyGPSStatus` | CFString | 0x0009 GPSStatus | `"A"` active, `"V"` void |
| `kCGImagePropertyGPSMeasureMode` | CFString | 0x000A GPSMeasureMode | `"2"` 2D, `"3"` 3D |
| `kCGImagePropertyGPSSatellites` | CFString | 0x0008 GPSSatellites | Free-form satellite info |
| `kCGImagePropertyGPSDOP` | CFNumber (Double) | 0x000B GPSDOP | Dilution of precision |
| `kCGImagePropertyGPSMapDatum` | CFString | 0x0012 GPSMapDatum | e.g., `"WGS-84"` |
| `kCGImagePropertyGPSVersion` | CFArray | 0x0000 GPSVersionID | Array of 4 CFNumber ints: `[2,3,0,0]` |
| `kCGImagePropertyGPSProcessingMethod` | CFString | 0x001B GPSProcessingMethod | Method name (charset prefix stripped by ImageIO) |
| `kCGImagePropertyGPSAreaInformation` | CFString | 0x001C GPSAreaInformation | Area name (charset prefix stripped by ImageIO) |
| `kCGImagePropertyGPSHPositioningError` | CFNumber (Double) | 0x001F GPSHPositioningError | Meters. iOS 8.0+ constant. EXIF 2.31+ tag. |
| `kCGImagePropertyGPSDifferental` | CFNumber (Int) | 0x001E GPSDifferential | 0 or 1. **Note misspelling** in constant name. |

> **Spelling note:** `kCGImagePropertyGPSDifferental` is missing an 'i' in
> "Diferental". This is a known Apple SDK typo preserved for backward
> compatibility. The EXIF tag name is "GPSDifferential".

### Type Conversion Summary

ImageIO performs these conversions between EXIF binary and CFType:

| EXIF Type | CFType | Conversion |
|-----------|--------|------------|
| 3x RATIONAL (coordinates) | CFNumber (Double) | DMS to decimal degrees |
| 3x RATIONAL (timestamp) | CFString | `"HH:MM:SS.SS"` |
| 1x RATIONAL (altitude, speed, etc.) | CFNumber (Double) | numerator/denominator |
| ASCII (2-char ref) | CFString | Direct (null terminator stripped) |
| BYTE (version, alt ref) | CFNumber (Int) or CFArray | Direct |
| UNDEFINED (processing, area) | CFString | Charset prefix stripped |
| SHORT (differential) | CFNumber (Int) | Direct |

---

## Reading GPS from an Image

### Extract GPS Dictionary

```swift
import ImageIO

func readGPS(from data: Data) -> [String: Any]? {
    guard let source = CGImageSourceCreateWithData(data as CFData, nil) else {
        return nil
    }

    // Disable pixel caching -- we only want metadata
    let options = [kCGImageSourceShouldCache: false] as CFDictionary
    guard let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, options)
            as? [String: Any] else {
        return nil
    }

    return properties[kCGImagePropertyGPSDictionary as String] as? [String: Any]
}
```

### Extract CLLocation from GPS Dictionary

```swift
import CoreLocation

func extractLocation(from gpsDict: [String: Any]) -> CLLocation? {
    guard
        let lat    = gpsDict[kCGImagePropertyGPSLatitude as String] as? Double,
        let latRef = gpsDict[kCGImagePropertyGPSLatitudeRef as String] as? String,
        let lon    = gpsDict[kCGImagePropertyGPSLongitude as String] as? Double,
        let lonRef = gpsDict[kCGImagePropertyGPSLongitudeRef as String] as? String
    else { return nil }

    let signedLat = (latRef == "S") ? -lat : lat
    let signedLon = (lonRef == "W") ? -lon : lon

    // Altitude
    var altitude: Double = 0
    if let alt = gpsDict[kCGImagePropertyGPSAltitude as String] as? Double {
        let altRef = gpsDict[kCGImagePropertyGPSAltitudeRef as String] as? Int ?? 0
        altitude = (altRef == 1) ? -alt : alt
    }

    // Accuracy
    let hAccuracy = gpsDict[kCGImagePropertyGPSHPositioningError as String] as? Double ?? 0

    let coordinate = CLLocationCoordinate2D(latitude: signedLat, longitude: signedLon)

    return CLLocation(
        coordinate: coordinate,
        altitude: altitude,
        horizontalAccuracy: hAccuracy,
        verticalAccuracy: -1,
        timestamp: Date()  // See coordinate-conventions.md for full timestamp parsing
    )
}
```

### Read GPS from a File URL

```swift
func readGPS(from url: URL) -> CLLocation? {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil) else {
        return nil
    }
    guard let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
            as? [String: Any],
          let gps = props[kCGImagePropertyGPSDictionary as String]
            as? [String: Any] else {
        return nil
    }
    return extractLocation(from: gps)
}
```

### Check if GPS Metadata Exists

```swift
func hasGPSMetadata(in data: Data) -> Bool {
    guard let source = CGImageSourceCreateWithData(data as CFData, nil),
          let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
            as? [String: Any] else {
        return false
    }
    return props[kCGImagePropertyGPSDictionary as String] != nil
}
```

---

## Writing GPS to an Image

### Write GPS to New Image (Re-encoding)

```swift
import ImageIO
import CoreLocation
import UniformTypeIdentifiers

func writeGPS(
    to imageData: Data,
    location: CLLocation,
    outputType: CFString = UTType.jpeg.identifier as CFString
) -> Data? {
    guard let source = CGImageSourceCreateWithData(imageData as CFData, nil),
          let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        return nil
    }

    // Read existing metadata
    var properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
        as? [String: Any] ?? [:]

    // Build GPS dictionary (see coordinate-conventions.md for gpsDictionary())
    let gpsDict = gpsDictionary(from: location)
    properties[kCGImagePropertyGPSDictionary as String] = gpsDict

    // Write to new data
    let output = NSMutableData()
    guard let dest = CGImageDestinationCreateWithData(
        output, outputType, 1, nil
    ) else { return nil }

    CGImageDestinationAddImage(dest, cgImage, properties as CFDictionary)

    guard CGImageDestinationFinalize(dest) else { return nil }
    return output as Data
}
```

### Lossless GPS Update (JPEG, PNG, TIFF, PSD only)

For formats that support lossless metadata update, use
`CGImageDestinationCopyImageSource` to avoid re-encoding pixels:

```swift
func updateGPSLossless(
    in imageData: Data,
    location: CLLocation
) -> Data? {
    guard let source = CGImageSourceCreateWithData(imageData as CFData, nil),
          let uti = CGImageSourceGetType(source) else {
        return nil
    }

    let output = NSMutableData()
    guard let dest = CGImageDestinationCreateWithData(
        output, uti, 0, nil  // count=0 for CopyImageSource
    ) else { return nil }

    // Build metadata with GPS
    let gpsDict = gpsDictionary(from: location)

    let metadata: [CFString: Any] = [
        kCGImageDestinationMergeMetadata: true,
        kCGImagePropertyGPSDictionary: gpsDict
    ]

    var error: Unmanaged<CFError>?
    let success = CGImageDestinationCopyImageSource(
        dest, source, metadata as CFDictionary, &error
    )

    guard success else {
        print("Lossless update failed: \(error?.takeRetainedValue() as Any)")
        return nil
    }

    return output as Data
}
```

> **Important:** Lossless metadata update is only supported for JPEG, PNG,
> TIFF, and PSD. HEIC requires full re-encoding. For lossless-capable formats,
> this is the preferred approach -- it avoids quality loss from JPEG
> recompression and is faster since no pixel decoding/encoding occurs.

### Update GPS via XMP (CGImageMetadata API)

For fine-grained control or when working with XMP directly:

```swift
import ImageIO

func updateGPSViaXMP(
    in imageData: Data,
    latitude: Double,
    longitude: Double
) -> Data? {
    guard let source = CGImageSourceCreateWithData(imageData as CFData, nil),
          let uti = CGImageSourceGetType(source) else {
        return nil
    }

    let metadata = CGImageMetadataCreateMutable()

    // Set GPS coordinates via bridge function
    CGImageMetadataSetValueMatchingImageProperty(
        metadata,
        kCGImagePropertyGPSDictionary,
        kCGImagePropertyGPSLatitude,
        abs(latitude) as CFNumber
    )
    CGImageMetadataSetValueMatchingImageProperty(
        metadata,
        kCGImagePropertyGPSDictionary,
        kCGImagePropertyGPSLatitudeRef,
        (latitude >= 0 ? "N" : "S") as CFString
    )
    CGImageMetadataSetValueMatchingImageProperty(
        metadata,
        kCGImagePropertyGPSDictionary,
        kCGImagePropertyGPSLongitude,
        abs(longitude) as CFNumber
    )
    CGImageMetadataSetValueMatchingImageProperty(
        metadata,
        kCGImagePropertyGPSDictionary,
        kCGImagePropertyGPSLongitudeRef,
        (longitude >= 0 ? "E" : "W") as CFString
    )

    let output = NSMutableData()
    guard let dest = CGImageDestinationCreateWithData(
        output, uti, 0, nil
    ) else { return nil }

    let options: [CFString: Any] = [
        kCGImageDestinationMergeMetadata: true,
        kCGImageDestinationMetadata: metadata
    ]

    var error: Unmanaged<CFError>?
    guard CGImageDestinationCopyImageSource(
        dest, source, options as CFDictionary, &error
    ) else { return nil }

    return output as Data
}
```

### The gpsDictionary Helper

See [coordinate-conventions.md](coordinate-conventions.md) for the full
`gpsDictionary(from:)` function that converts `CLLocation` to an ImageIO
GPS dictionary, including altitude, timestamp, speed, course, and accuracy.

---

## PHAsset.location vs EXIF GPS

`PHAsset.location` and EXIF GPS metadata are **separate data stores** that
usually agree but can diverge.

### Comparison

| Aspect | `PHAsset.location` | EXIF GPS |
|--------|-------------------|----------|
| **Storage** | Photos library database (SQLite) | Embedded in image file bytes |
| **Format** | `CLLocation` (signed decimal degrees) | Unsigned values + reference letters |
| **Access API** | PhotoKit (`PHAsset.location`) | ImageIO (`kCGImagePropertyGPSDictionary`) |
| **Mutability** | Read-only via PhotoKit API | Read/write via ImageIO |
| **Survives export** | No (database only) | Yes (in file) |
| **Survives import** | Set from EXIF on import | Always in file |
| **User-editable** | Yes (Photos app, iOS 15+) | Not directly via Photos app |
| **Accuracy info** | Full `CLLocation` (h/v accuracy, speed, course) | Limited (GPSHPositioningError for horizontal only) |
| **Altitude source** | `CLLocation.altitude` (WGS-84 ellipsoid) | `GPSAltitude` (may be WGS-84 or MSL) |
| **Timezone** | `Date` object (absolute time) | UTC only (GPSTimeStamp/DateStamp) |

### When They Differ

1. **User edited location in Photos.** iOS 15+ allows manual location
   editing. This updates `PHAsset.location` but does NOT change the EXIF
   GPS in the original file. The original metadata is preserved; the edit
   is stored separately in `PHAdjustmentData`.

2. **Reverse-geocoding correction.** Photos may adjust `PHAsset.location`
   based on Wi-Fi positioning, nearby photos, or manual corrections. The
   EXIF GPS remains as the camera recorded it.

3. **Third-party import.** Images imported from non-camera sources may have
   EXIF GPS but no `PHAsset.location`, or vice versa.

4. **GPS not available at capture.** The camera may write approximate
   coordinates from cell tower triangulation. `PHAsset.location` might be
   refined later by the Photos framework.

5. **Location stripped on share.** If the user shared without location,
   then added to their library, the file EXIF may lack GPS while
   `PHAsset.location` may still be populated from the original capture.

### Which to Use

| Scenario | Recommended Source |
|----------|-------------------|
| Display photo location to user | `PHAsset.location` (may be user-corrected) |
| Export/share with accurate original metadata | EXIF GPS (via `requestContentEditingInput`) |
| Programmatic location analysis | EXIF GPS (raw camera data) |
| Checking if user edited location | Compare both sources |
| Cross-platform compatibility | EXIF GPS (survives export/import) |

### Accessing EXIF GPS from PHAsset

```swift
import Photos
import ImageIO

func getExifGPS(from asset: PHAsset, completion: @escaping ([String: Any]?) -> Void) {
    let options = PHContentEditingInputRequestOptions()
    options.isNetworkAccessAllowed = true  // Allow iCloud download

    asset.requestContentEditingInput(with: options) { input, _ in
        guard let url = input?.fullSizeImageURL,
              let source = CGImageSourceCreateWithURL(url as CFURL, nil),
              let props = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
                as? [String: Any] else {
            completion(nil)
            return
        }
        let gps = props[kCGImagePropertyGPSDictionary as String] as? [String: Any]
        completion(gps)
    }
}
```

### Comparing PHAsset.location with EXIF GPS

```swift
/// Check if the user has edited the location in Photos.
/// Returns true if PHAsset.location differs significantly from EXIF GPS.
func isLocationEdited(asset: PHAsset, exifGPS: [String: Any]) -> Bool {
    guard let assetLocation = asset.location else { return false }

    guard let lat = exifGPS[kCGImagePropertyGPSLatitude as String] as? Double,
          let latRef = exifGPS[kCGImagePropertyGPSLatitudeRef as String] as? String,
          let lon = exifGPS[kCGImagePropertyGPSLongitude as String] as? Double,
          let lonRef = exifGPS[kCGImagePropertyGPSLongitudeRef as String] as? String
    else { return true }  // No EXIF GPS but PHAsset has location

    let exifLat = (latRef == "S") ? -lat : lat
    let exifLon = (lonRef == "W") ? -lon : lon

    let threshold = 0.0001  // ~11 meters
    return abs(assetLocation.coordinate.latitude - exifLat) > threshold ||
           abs(assetLocation.coordinate.longitude - exifLon) > threshold
}
```

---

## CLLocation Properties --> GPS Dictionary Key Mapping

Complete mapping between `CLLocation` / `CLHeading` properties and ImageIO
GPS dictionary keys:

| CLLocation Property | ImageIO Key | Conversion | Notes |
|--------------------|-------------|------------|-------|
| `coordinate.latitude` | `kCGImagePropertyGPSLatitude` | `abs(value)` | Always positive |
| (sign of latitude) | `kCGImagePropertyGPSLatitudeRef` | `>= 0 ? "N" : "S"` | |
| `coordinate.longitude` | `kCGImagePropertyGPSLongitude` | `abs(value)` | Always positive |
| (sign of longitude) | `kCGImagePropertyGPSLongitudeRef` | `>= 0 ? "E" : "W"` | |
| `altitude` | `kCGImagePropertyGPSAltitude` | `abs(value)` | Meters |
| (sign of altitude) | `kCGImagePropertyGPSAltitudeRef` | `>= 0 ? 0 : 1` | 0=above, 1=below |
| `horizontalAccuracy` | `kCGImagePropertyGPSHPositioningError` | Direct (meters) | Skip if < 0 (invalid) |
| `speed` | `kCGImagePropertyGPSSpeed` | `value * 3.6` | m/s to km/h; skip if < 0 |
| (speed unit) | `kCGImagePropertyGPSSpeedRef` | `"K"` | km/h |
| `course` | `kCGImagePropertyGPSTrack` | Direct (degrees) | Skip if < 0 (invalid) |
| (course reference) | `kCGImagePropertyGPSTrackRef` | `"T"` | True north |
| `timestamp` | `kCGImagePropertyGPSTimeStamp` | UTC `"HH:MM:SS.SS"` | Must convert to UTC |
| `timestamp` | `kCGImagePropertyGPSDateStamp` | UTC `"YYYY:MM:DD"` | Colon separators |

| CLHeading Property | ImageIO Key | Conversion | Notes |
|-------------------|-------------|------------|-------|
| `trueHeading` | `kCGImagePropertyGPSImgDirection` | Direct (degrees) | Prefer true over magnetic |
| (heading reference) | `kCGImagePropertyGPSImgDirectionRef` | `"T"` | True north |
| `magneticHeading` | `kCGImagePropertyGPSImgDirection` | Direct (degrees) | Fallback if no true heading |
| (heading reference) | `kCGImagePropertyGPSImgDirectionRef` | `"M"` | Magnetic north |

### CLLocation Properties with No EXIF GPS Equivalent

| CLLocation Property | Notes |
|--------------------|-------|
| `verticalAccuracy` | No GPS IFD tag exists for vertical accuracy |
| `speedAccuracy` (iOS 10+) | No GPS IFD tag exists |
| `courseAccuracy` (iOS 13.4+) | No GPS IFD tag exists |
| `floor` (iOS 8+) | No GPS IFD tag exists (indoor positioning) |
| `sourceInformation` (iOS 15+) | No GPS IFD tag exists |
| `ellipsoidalAltitude` (iOS 15+) | GPS altitude is already ellipsoidal; no separate tag |
| `headingAccuracy` (CLHeading) | No GPS IFD tag exists |

---

## GPS Stripping: Removing Location Data

### Method 1: kCGImageMetadataShouldExcludeGPS (Lossless)

Use with `CGImageDestinationCopyImageSource` for lossless GPS removal
from JPEG, PNG, TIFF, and PSD:

```swift
func stripGPS(from imageData: Data) -> Data? {
    guard let source = CGImageSourceCreateWithData(imageData as CFData, nil),
          let uti = CGImageSourceGetType(source) else {
        return nil
    }

    let output = NSMutableData()
    guard let dest = CGImageDestinationCreateWithData(
        output, uti, 0, nil
    ) else { return nil }

    let options: [CFString: Any] = [
        kCGImageMetadataShouldExcludeGPS: true
    ]

    var error: Unmanaged<CFError>?
    let success = CGImageDestinationCopyImageSource(
        dest, source, options as CFDictionary, &error
    )

    guard success else { return nil }
    return output as Data
}
```

**This removes:**
- All `kCGImagePropertyGPSDictionary` keys from the EXIF GPS IFD
- Corresponding XMP GPS tags (`exif:GPSLatitude`, `exif:GPSLongitude`, etc.)

**This does NOT remove:**
- Location data embedded in Apple MakerNote (tag 0x927C)
- Custom XMP properties that may contain coordinates
- IPTC IIM location fields (City, State/Province, Country, Sub-location)
- Location data in other vendor MakerNotes

### Method 2: Manual GPS Dictionary Removal (Re-encoding)

Remove the GPS dictionary while preserving other metadata. Requires pixel
re-encoding, so JPEG quality may degrade:

```swift
func stripGPSManual(from imageData: Data) -> Data? {
    guard let source = CGImageSourceCreateWithData(imageData as CFData, nil),
          let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        return nil
    }

    var properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
        as? [String: Any] ?? [:]

    // Remove GPS dictionary entirely
    properties.removeValue(forKey: kCGImagePropertyGPSDictionary as String)

    let output = NSMutableData()
    guard let uti = CGImageSourceGetType(source),
          let dest = CGImageDestinationCreateWithData(
              output, uti, 1, nil
          ) else { return nil }

    CGImageDestinationAddImage(dest, cgImage, properties as CFDictionary)
    guard CGImageDestinationFinalize(dest) else { return nil }
    return output as Data
}
```

### Method 3: Nuclear Option (Strip ALL Metadata)

Write pixels only -- no metadata at all. Safest for privacy but loses
everything (EXIF, IPTC, XMP, MakerNote, ICC profile):

```swift
func stripAllMetadata(from imageData: Data) -> Data? {
    guard let source = CGImageSourceCreateWithData(imageData as CFData, nil),
          let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        return nil
    }

    let output = NSMutableData()
    guard let dest = CGImageDestinationCreateWithData(
        output, kUTTypeJPEG, 1, nil
    ) else { return nil }

    // No metadata dictionary passed -- only pixels
    CGImageDestinationAddImage(dest, cgImage, nil)
    guard CGImageDestinationFinalize(dest) else { return nil }
    return output as Data
}
```

> Even the "nuclear option" generates synthetic EXIF tags
> (`PixelXDimension`, `PixelYDimension`) from the image dimensions. See
> [`../imageio/pitfalls.md`](../imageio/pitfalls.md) -- "Clean JPEG Baseline".

### Method Comparison

| Method | Lossless | Strips GPS IFD | Strips XMP GPS | Strips MakerNote | Strips IPTC Location | Format Support |
|--------|----------|---------------|----------------|-------------------|---------------------|----------------|
| `kCGImageMetadataShouldExcludeGPS` | Yes | Yes | Yes | No | No | JPEG, PNG, TIFF, PSD |
| Manual dictionary removal | No (re-encode) | Yes | Partial | No | No | Any writable format |
| Nuclear (pixels only) | No (re-encode) | Yes | Yes | Yes | Yes | Any writable format |

### Comprehensive Location Stripping

For apps with strict privacy requirements, combine approaches:

```swift
func stripAllLocationData(from imageData: Data) -> Data? {
    guard let source = CGImageSourceCreateWithData(imageData as CFData, nil),
          let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        return nil
    }

    var properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
        as? [String: Any] ?? [:]

    // 1. Remove GPS dictionary
    properties.removeValue(forKey: kCGImagePropertyGPSDictionary as String)

    // 2. Remove IPTC location fields
    if var iptc = properties[kCGImagePropertyIPTCDictionary as String] as? [String: Any] {
        iptc.removeValue(forKey: kCGImagePropertyIPTCCity as String)
        iptc.removeValue(forKey: kCGImagePropertyIPTCProvinceState as String)
        iptc.removeValue(forKey: kCGImagePropertyIPTCCountryPrimaryLocationName as String)
        iptc.removeValue(forKey: kCGImagePropertyIPTCCountryPrimaryLocationCode as String)
        iptc.removeValue(forKey: kCGImagePropertyIPTCSubLocation as String)
        properties[kCGImagePropertyIPTCDictionary as String] = iptc
    }

    // 3. Remove EXIF MakerNote (may contain location-adjacent data)
    if var exif = properties[kCGImagePropertyExifDictionary as String] as? [String: Any] {
        exif.removeValue(forKey: kCGImagePropertyExifMakerNote as String)
        properties[kCGImagePropertyExifDictionary as String] = exif
    }

    let output = NSMutableData()
    guard let uti = CGImageSourceGetType(source),
          let dest = CGImageDestinationCreateWithData(output, uti, 1, nil)
    else { return nil }

    CGImageDestinationAddImage(dest, cgImage, properties as CFDictionary)
    guard CGImageDestinationFinalize(dest) else { return nil }
    return output as Data
}
```

---

## iOS Sharing Behavior and GPS

### Share Sheet (iOS 13+)

When sharing photos from the Photos app, the share sheet includes an
"Options" button at the top. Under "Include", the "Location" toggle controls
whether GPS metadata is embedded in the shared copy:

- **Location ON (default):** GPS metadata is included in the shared file.
- **Location OFF:** GPS metadata is stripped from the shared copy. Original
  file in the Photos library is unaffected.

This setting resets to ON each time the share sheet is opened. There is no
persistent preference to always strip location.

### Platform-Specific Behavior

| Sharing Method | GPS Preserved? | Notes |
|----------------|---------------|-------|
| AirDrop | Yes (by default) | "All Photos Data" option includes full metadata |
| iMessage | Yes | Full EXIF preserved in attachment |
| Mail | Yes | Full EXIF preserved in attachment |
| iCloud Photo Sharing | Yes | Full metadata in shared albums |
| iCloud Link | Yes | Full metadata included |
| WhatsApp | Stripped | Compresses and strips EXIF on upload |
| Facebook/Instagram | Stripped | Social platforms strip EXIF on upload |
| Signal | Stripped | Privacy-focused: strips metadata |
| Telegram | Depends | "Send as File" preserves; default send strips |
| Slack | Stripped | Compresses and strips most EXIF |

### Programmatic GPS Control

When your app shares images programmatically, you control whether GPS is
included by managing the metadata before creating the share data. Use the
stripping methods above before passing data to `UIActivityViewController`.

```swift
// Example: Share photo with GPS stripped
let strippedData = stripGPS(from: originalJPEGData)
let activityVC = UIActivityViewController(
    activityItems: [strippedData as Any],
    applicationActivities: nil
)
present(activityVC, animated: true)
```

### Camera App Settings

Users can prevent GPS from being recorded in the first place:
**Settings > Privacy & Security > Location Services > Camera > Never**

When location access is disabled for Camera, the iPhone writes no GPS IFD
at all. The EXIF still contains all other metadata (timestamp, camera
settings, etc.), but `kCGImagePropertyGPSDictionary` will be absent.
