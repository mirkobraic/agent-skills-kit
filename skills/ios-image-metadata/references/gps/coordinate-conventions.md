# GPS Coordinate Conventions

> Part of [GPS Reference](README.md)

How GPS coordinates are stored in EXIF, how ImageIO exposes them, and how to
convert between the various formats. This document covers the most common
source of GPS metadata bugs: the mismatch between signed decimal degrees
(as used by `CLLocation`) and unsigned-value-plus-reference (as used by EXIF
and ImageIO).

---

## The Core Convention: Absolute Values + Reference Letters

EXIF GPS coordinates are **never** stored as signed numbers. Instead, the
magnitude and hemisphere are separated:

| Component | EXIF Tags | Example (San Francisco) |
|-----------|-----------|------------------------|
| Latitude magnitude | `GPSLatitude` | 37 deg 46' 29.64" |
| Latitude hemisphere | `GPSLatitudeRef` | `"N"` |
| Longitude magnitude | `GPSLongitude` | 122 deg 25' 9.84" |
| Longitude hemisphere | `GPSLongitudeRef` | `"W"` |

The same applies to `GPSDestLatitude`/`GPSDestLongitude` for destination
coordinates.

**Why?** The EXIF specification uses unsigned RATIONAL values (pairs of
unsigned 32-bit integers). There is no way to represent a negative value
in an unsigned RATIONAL. The reference tag carries the sign information.

**In Apple's ImageIO:** The same convention is enforced. Even though ImageIO
converts the three RATIONALs to a single CFNumber (Double), the value is
always positive. The sign is in the separate `*Ref` string. Passing a
negative number as `kCGImagePropertyGPSLongitude` does not produce a western
hemisphere coordinate -- ImageIO takes the absolute value, and without a
`"W"` reference, the point ends up in the eastern hemisphere.

---

## Coordinate Formats

GPS positions can be expressed in several formats. All represent the same
location but differ in how fractional degrees are encoded.

### DMS -- Degrees, Minutes, Seconds

The traditional format and what EXIF stores at the binary level.

```
37° 46' 29.64" N,  122° 25' 9.84" W
```

- Degrees: integer, 0--90 (lat) or 0--180 (lon)
- Minutes: integer, 0--59
- Seconds: real, 0--59.999...

### DD -- Decimal Degrees

The format used by `CLLocationCoordinate2D` and most programming APIs. Sign
indicates hemisphere (positive = N/E, negative = S/W).

```
37.774900, -122.419400
```

### DM -- Degrees, Decimal Minutes

Used by XMP (`GPSCoordinate` type) and some GPS devices.

```
37° 46.494' N,  122° 25.164' W
```

### EXIF RATIONAL Format

Three RATIONAL values per coordinate (degrees, minutes, seconds). Each
RATIONAL is a numerator/denominator pair of unsigned 32-bit integers.

```
GPSLatitude:  37/1, 46/1, 2964/100
GPSLongitude: 122/1, 25/1, 984/100
```

The denominator allows fractional values without floating-point. Common
encodings used by various cameras and tools:

| Style | Degrees | Minutes | Seconds | Precision |
|-------|---------|---------|---------|-----------|
| DMS integer | 37/1 | 46/1 | 30/1 | ~30 meters |
| DMS with fractional seconds | 37/1 | 46/1 | 2964/100 | ~0.3 meters |
| DM only (seconds = 0) | 37/1 | 4649/100 | 0/1 | ~18 meters |
| DD only (minutes = 0, seconds = 0) | 377749/10000 | 0/1 | 0/1 | ~11 meters |

### ImageIO Format

ImageIO simplifies the three RATIONALs into a single `CFNumber` (Double) in
**decimal degrees**. It is always a positive value. The direction is a
separate `CFString` (`"N"`, `"S"`, `"E"`, `"W"`).

```swift
// What ImageIO returns when reading
let lat  = gpsDict[kCGImagePropertyGPSLatitude as String] as? Double    // 37.7749
let latRef = gpsDict[kCGImagePropertyGPSLatitudeRef as String] as? String // "N"
let lon  = gpsDict[kCGImagePropertyGPSLongitude as String] as? Double   // 122.4194
let lonRef = gpsDict[kCGImagePropertyGPSLongitudeRef as String] as? String // "W"
```

---

## Conversion: CLLocation --> EXIF GPS (for Writing)

Split a signed coordinate into absolute value + reference letter, and convert
all CLLocation/CLHeading properties to ImageIO GPS dictionary keys.

```swift
import ImageIO
import CoreLocation

/// Convert a CLLocation to an ImageIO GPS metadata dictionary.
/// Includes coordinates, altitude, timestamp, speed, course, and accuracy.
func gpsDictionary(from location: CLLocation) -> [CFString: Any] {
    let coordinate = location.coordinate
    let altitude = location.altitude
    let timestamp = location.timestamp

    // --- Coordinates ---
    let latitudeRef  = coordinate.latitude >= 0 ? "N" : "S"
    let longitudeRef = coordinate.longitude >= 0 ? "E" : "W"

    // --- Altitude ---
    // AltitudeRef: 0 = above sea level, 1 = below sea level
    let altitudeRef: Int = altitude >= 0 ? 0 : 1

    // --- Timestamp (must be UTC) ---
    let calendar = Calendar(identifier: .gregorian)
    let utc = TimeZone(identifier: "UTC")!
    let components = calendar.dateComponents(in: utc, from: timestamp)
    let timeStamp = String(
        format: "%02d:%02d:%02d.%02d",
        components.hour ?? 0,
        components.minute ?? 0,
        components.second ?? 0,
        (components.nanosecond ?? 0) / 10_000_000  // centiseconds
    )
    let dateStamp = String(
        format: "%04d:%02d:%02d",
        components.year ?? 0,
        components.month ?? 0,
        components.day ?? 0
    )

    var dict: [CFString: Any] = [
        kCGImagePropertyGPSLatitude:      abs(coordinate.latitude),
        kCGImagePropertyGPSLatitudeRef:   latitudeRef,
        kCGImagePropertyGPSLongitude:     abs(coordinate.longitude),
        kCGImagePropertyGPSLongitudeRef:  longitudeRef,
        kCGImagePropertyGPSAltitude:      abs(altitude),
        kCGImagePropertyGPSAltitudeRef:   altitudeRef,
        kCGImagePropertyGPSTimeStamp:     timeStamp,
        kCGImagePropertyGPSDateStamp:     dateStamp,
        kCGImagePropertyGPSVersion:       [2, 3, 0, 0] as [Int],
        kCGImagePropertyGPSMapDatum:      "WGS-84",
    ]

    // --- Horizontal accuracy (EXIF 2.31+) ---
    if location.horizontalAccuracy >= 0 {
        dict[kCGImagePropertyGPSHPositioningError] = location.horizontalAccuracy
    }

    // --- Speed (CLLocation.speed is m/s, convert to km/h) ---
    if location.speed >= 0 {
        dict[kCGImagePropertyGPSSpeed]    = location.speed * 3.6
        dict[kCGImagePropertyGPSSpeedRef] = "K"  // km/h
    }

    // --- Course (direction of travel) ---
    if location.course >= 0 {
        dict[kCGImagePropertyGPSTrack]    = location.course
        dict[kCGImagePropertyGPSTrackRef] = "T"  // true north
    }

    return dict
}

/// Add heading (compass direction camera faces) to an existing GPS dict.
func addHeading(_ heading: CLHeading, to dict: inout [CFString: Any]) {
    if heading.trueHeading >= 0 {
        dict[kCGImagePropertyGPSImgDirection]    = heading.trueHeading
        dict[kCGImagePropertyGPSImgDirectionRef] = "T"
    } else if heading.magneticHeading >= 0 {
        dict[kCGImagePropertyGPSImgDirection]    = heading.magneticHeading
        dict[kCGImagePropertyGPSImgDirectionRef] = "M"
    }
}
```

### Key Points in the Conversion

1. **`abs()` on every coordinate/altitude value.** Never pass signed values.
2. **Sign determines the `*Ref` tag.** `>= 0` for N/E/above, `< 0` for S/W/below.
3. **Timestamp must be UTC.** Use `Calendar.dateComponents(in: utcTimeZone, from:)`.
4. **Speed needs unit conversion.** `CLLocation.speed` is m/s; GPS uses km/h (Ref="K").
5. **Check for valid values.** `speed < 0` and `course < 0` mean invalid; do not write.
6. **Include GPSVersionID and GPSMapDatum.** Required for spec compliance.

---

## Conversion: EXIF GPS --> CLLocation (for Reading)

Reconstruct a `CLLocation` from an ImageIO GPS dictionary:

```swift
import CoreLocation
import ImageIO

/// Extract a CLLocation from an ImageIO GPS metadata dictionary.
/// Handles all available properties: coordinates, altitude, accuracy,
/// speed (with unit conversion), course, and timestamp.
func location(from gpsDict: [String: Any]) -> CLLocation? {
    guard
        let lat    = gpsDict[kCGImagePropertyGPSLatitude as String] as? Double,
        let latRef = gpsDict[kCGImagePropertyGPSLatitudeRef as String] as? String,
        let lon    = gpsDict[kCGImagePropertyGPSLongitude as String] as? Double,
        let lonRef = gpsDict[kCGImagePropertyGPSLongitudeRef as String] as? String
    else { return nil }

    // Apply sign based on reference
    let signedLat = (latRef == "S") ? -lat : lat
    let signedLon = (lonRef == "W") ? -lon : lon

    // Altitude
    var altitude: Double = 0
    if let alt = gpsDict[kCGImagePropertyGPSAltitude as String] as? Double {
        let altRef = gpsDict[kCGImagePropertyGPSAltitudeRef as String] as? Int ?? 0
        altitude = (altRef == 1) ? -alt : alt
    }

    // Horizontal accuracy
    let hAccuracy = gpsDict[kCGImagePropertyGPSHPositioningError as String] as? Double ?? 0

    // Vertical accuracy (not stored in EXIF GPS -- use -1 for unknown)
    let vAccuracy: Double = -1

    // Speed (convert back to m/s from whatever unit is specified)
    var speed: Double = -1
    if let s = gpsDict[kCGImagePropertyGPSSpeed as String] as? Double,
       let sRef = gpsDict[kCGImagePropertyGPSSpeedRef as String] as? String {
        switch sRef {
        case "K": speed = s / 3.6       // km/h --> m/s
        case "M": speed = s * 0.44704   // mph --> m/s
        case "N": speed = s * 0.514444  // knots --> m/s
        default:  speed = s / 3.6       // assume km/h
        }
    }

    // Course (direction of travel)
    let course = gpsDict[kCGImagePropertyGPSTrack as String] as? Double ?? -1

    // Timestamp (reconstruct from DateStamp + TimeStamp)
    var timestamp = Date()
    if let dateStr = gpsDict[kCGImagePropertyGPSDateStamp as String] as? String,
       let timeStr = gpsDict[kCGImagePropertyGPSTimeStamp as String] as? String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy:MM:dd HH:mm:ss"
        formatter.timeZone = TimeZone(identifier: "UTC")
        formatter.locale = Locale(identifier: "en_US_POSIX")
        // TimeStamp may be "14:30:45" or "14:30:45.00" -- strip fractional part
        let cleanTime = timeStr.components(separatedBy: ".").first ?? timeStr
        if let date = formatter.date(from: "\(dateStr) \(cleanTime)") {
            timestamp = date
        }
    }

    let coordinate = CLLocationCoordinate2D(latitude: signedLat, longitude: signedLon)

    return CLLocation(
        coordinate: coordinate,
        altitude: altitude,
        horizontalAccuracy: hAccuracy,
        verticalAccuracy: vAccuracy,
        course: course,
        speed: speed,
        timestamp: timestamp
    )
}
```

---

## Decimal Degrees <--> DMS Conversion

For contexts where you need DMS values directly (e.g., display, or building
raw EXIF data outside ImageIO):

```swift
/// Convert decimal degrees to degrees, minutes, seconds.
func decimalToDMS(_ decimal: Double) -> (degrees: Int, minutes: Int, seconds: Double) {
    let absolute = abs(decimal)
    let degrees = Int(absolute)
    let minutesDecimal = (absolute - Double(degrees)) * 60
    let minutes = Int(minutesDecimal)
    let seconds = (minutesDecimal - Double(minutes)) * 60
    return (degrees, minutes, seconds)
}

/// Convert DMS to decimal degrees.
func dmsToDecimal(degrees: Int, minutes: Int, seconds: Double) -> Double {
    return Double(degrees) + Double(minutes) / 60.0 + seconds / 3600.0
}

// Example:
// 37.7749 --> (37, 46, 29.64)
// (37, 46, 29.64) --> 37.7749
```

### EXIF Three-RATIONAL to Decimal Degrees

When working with raw EXIF data (not through ImageIO), each coordinate is
three RATIONAL values. The conversion formula:

```
DD = (degNum/degDenom) + (minNum/minDenom)/60 + (secNum/secDenom)/3600
```

Example: GPSLatitude = `37/1, 46/1, 2964/100`

```
DD = 37/1 + 46/60 + (2964/100)/3600
   = 37 + 0.76667 + 0.00823
   = 37.7749
```

---

## Decimal Degrees <--> Degrees, Decimal Minutes

For XMP GPSCoordinate format and some GPS devices:

```swift
/// Convert decimal degrees to degrees and decimal minutes.
func decimalToDM(_ decimal: Double) -> (degrees: Int, decimalMinutes: Double) {
    let absolute = abs(decimal)
    let degrees = Int(absolute)
    let decimalMinutes = (absolute - Double(degrees)) * 60
    return (degrees, decimalMinutes)
}

/// Convert degrees and decimal minutes to decimal degrees.
func dmToDecimal(degrees: Int, decimalMinutes: Double) -> Double {
    return Double(degrees) + decimalMinutes / 60.0
}

// Example:
// 37.7749 --> (37, 46.494)
// (37, 46.494) --> 37.7749
```

---

## XMP GPS Coordinate Format

In XMP, GPS coordinates use the `GPSCoordinate` type defined in CIPA
DC-X010-2017 (section A.2.4.4) and the XMP Specification Part 2. The format
differs from both EXIF binary and ImageIO.

### Format

```
DDD,MM.mmk      (degrees and decimal minutes -- preferred)
DDD,MM,SSk      (degrees, minutes, integer seconds)
DDD,MM,SS.ssk   (degrees, minutes, decimal seconds)
```

Where:
- `DDD` = degrees (variable width, no leading zeros required)
- `MM` = minutes
- `SS` = seconds
- `k` = direction letter: `N`, `S`, `E`, or `W`

### Examples

```xml
<!-- Degrees and decimal minutes (preferred form) -->
<exif:GPSLatitude>37,46.494N</exif:GPSLatitude>
<exif:GPSLongitude>122,25.164W</exif:GPSLongitude>
```

Or with seconds:

```xml
<!-- Degrees, minutes, seconds -->
<exif:GPSLatitude>37,46,29.64N</exif:GPSLatitude>
<exif:GPSLongitude>122,25,9.84W</exif:GPSLongitude>
```

### Key Differences: EXIF Binary vs ImageIO vs XMP

| Aspect | EXIF Binary | ImageIO | XMP |
|--------|-------------|---------|-----|
| Coordinate format | Three RATIONALs (DMS) | Single Double (DD) | Comma-separated string (DM or DMS) |
| Direction | Separate tag (`GPSLatitudeRef`) | Separate key (`*Ref`) | Suffix letter on value (`N`/`S`/`E`/`W`) |
| Timestamp | Separate `GPSDateStamp` + `GPSTimeStamp` | Separate `DateStamp` + `TimeStamp` strings | Combined `exif:GPSTimeStamp` as ISO 8601 |
| Altitude | RATIONAL + BYTE ref | CFNumber + CFNumber ref | RATIONAL string + string ref |
| Signedness | Unsigned only | Unsigned only (positive) | Unsigned (direction suffix) |

### XMP GPS Tag Mapping

| EXIF Tag(s) | XMP Path | Format Notes |
|-------------|----------|--------------|
| GPSLatitude + GPSLatitudeRef | `exif:GPSLatitude` | Combined `GPSCoordinate`: `"37,46.494N"` |
| GPSLongitude + GPSLongitudeRef | `exif:GPSLongitude` | Combined `GPSCoordinate`: `"122,25.164W"` |
| GPSAltitude | `exif:GPSAltitude` | RATIONAL string: `"523/10"` |
| GPSAltitudeRef | `exif:GPSAltitudeRef` | `"0"` or `"1"` |
| GPSTimeStamp + GPSDateStamp | `exif:GPSTimeStamp` | ISO 8601: `"2024-06-15T14:30:45Z"` |
| GPSSpeed | `exif:GPSSpeed` | RATIONAL string |
| GPSSpeedRef | `exif:GPSSpeedRef` | `"K"`, `"M"`, or `"N"` |
| GPSTrack | `exif:GPSTrack` | RATIONAL string |
| GPSTrackRef | `exif:GPSTrackRef` | `"T"` or `"M"` |
| GPSImgDirection | `exif:GPSImgDirection` | RATIONAL string |
| GPSImgDirectionRef | `exif:GPSImgDirectionRef` | `"T"` or `"M"` |
| GPSMapDatum | `exif:GPSMapDatum` | String |
| GPSDestLatitude + Ref | `exif:GPSDestLatitude` | `GPSCoordinate` format |
| GPSDestLongitude + Ref | `exif:GPSDestLongitude` | `GPSCoordinate` format |
| GPSDestBearing | `exif:GPSDestBearing` | RATIONAL string |
| GPSDestBearingRef | `exif:GPSDestBearingRef` | String |
| GPSDestDistance | `exif:GPSDestDistance` | RATIONAL string |
| GPSDestDistanceRef | `exif:GPSDestDistanceRef` | String |
| GPSVersionID | `exif:GPSVersionID` | Dot-separated: `"2.3.0.0"` |
| GPSDOP | `exif:GPSDOP` | RATIONAL string |
| GPSMeasureMode | `exif:GPSMeasureMode` | `"2"` or `"3"` |
| GPSSatellites | `exif:GPSSatellites` | String |
| GPSStatus | `exif:GPSStatus` | `"A"` or `"V"` |
| GPSHPositioningError | `exif:GPSHPositioningError` | RATIONAL string |
| GPSDifferential | `exif:GPSDifferential` | `"0"` or `"1"` |
| GPSProcessingMethod | `exif:GPSProcessingMethod` | String (charset prefix stripped) |
| GPSAreaInformation | `exif:GPSAreaInformation` | String (charset prefix stripped) |

### XMP GPSCoordinate Conversion Code

```swift
/// Convert decimal degrees + reference to XMP GPSCoordinate format.
/// Returns a string like "37,46.494N" or "122,25.164W".
func xmpGPSCoordinate(decimalDegrees: Double, isLatitude: Bool) -> String {
    let ref: String
    if isLatitude {
        ref = decimalDegrees >= 0 ? "N" : "S"
    } else {
        ref = decimalDegrees >= 0 ? "E" : "W"
    }

    let absolute = abs(decimalDegrees)
    let degrees = Int(absolute)
    let decimalMinutes = (absolute - Double(degrees)) * 60

    // Use enough decimal places to preserve sub-meter precision
    return String(format: "%d,%.6f%@", degrees, decimalMinutes, ref)
}

/// Parse an XMP GPSCoordinate string to decimal degrees.
/// Handles both "DDD,MM.mmk" and "DDD,MM,SS.ssk" formats.
func parseXMPCoordinate(_ xmp: String) -> Double? {
    guard !xmp.isEmpty else { return nil }

    let direction = xmp.last  // N, S, E, or W
    let numberPart = String(xmp.dropLast())
    let components = numberPart.split(separator: ",")

    guard components.count >= 2 else { return nil }

    let degrees = Double(components[0]) ?? 0
    var result: Double

    if components.count == 2 {
        // DDD,MM.mmk format
        let minutes = Double(components[1]) ?? 0
        result = degrees + minutes / 60.0
    } else {
        // DDD,MM,SS.ssk format
        let minutes = Double(components[1]) ?? 0
        let seconds = Double(components[2]) ?? 0
        result = degrees + minutes / 60.0 + seconds / 3600.0
    }

    if direction == "S" || direction == "W" {
        result = -result
    }

    return result
}
```

---

## Common Conversion Bugs

### Bug 1: Passing Signed Values to ImageIO

```swift
// BUG: ImageIO ignores the sign. This stores longitude as 122.4194 E, not W.
dict[kCGImagePropertyGPSLongitude] = -122.4194

// FIX: Use absolute value + reference
dict[kCGImagePropertyGPSLongitude]    = 122.4194
dict[kCGImagePropertyGPSLongitudeRef] = "W"
```

This is the single most reported GPS metadata bug. A photo taken in
San Francisco ends up tagged in Jiangxi, China (same absolute longitude,
wrong hemisphere).

### Bug 2: Forgetting the Reference Tag

```swift
// BUG: No reference tag -- reader cannot determine hemisphere.
dict[kCGImagePropertyGPSLatitude] = 37.7749
// Missing: dict[kCGImagePropertyGPSLatitudeRef] = "N"
```

Many readers default to "N"/"E" when the reference is missing, which places
southern/western coordinates in the wrong hemisphere.

### Bug 3: Using abs() Without Checking Zero

```swift
// EDGE CASE: The prime meridian (0 deg) and equator (0 deg) are valid.
// abs(0.0) is 0.0, and the reference should be "N"/"E" by convention.
let latRef = latitude >= 0 ? "N" : "S"  // Correct: >= 0 gives "N"
let lonRef = longitude >= 0 ? "E" : "W" // Correct: >= 0 gives "E"
```

### Bug 4: Truncating XMP Coordinate Precision

When converting decimal degrees to XMP `GPSCoordinate` format, ensure enough
decimal places in the minutes value. Truncating to integer minutes loses
significant precision:

```
37,46N       --> 37 deg 46' 0"  N  (error: ~500 meters from actual)
37,46.5N     --> 37 deg 46.5' N    (error: ~9 meters)
37,46.494N   --> 37 deg 46.494' N  (error: ~0.2 meters)
37,46.494000N --> full precision    (error: < 0.02 meters)
```

### Bug 5: Confusing GPSTrack with GPSImgDirection

- `GPSTrack` = direction of **movement** (where device is traveling)
- `GPSImgDirection` = direction camera **faces** (where image points)

These are independent. A person walking north and photographing east has
`GPSTrack = 0` and `GPSImgDirection = 90`.

### Bug 6: Writing Local Time to GPSTimeStamp

`GPSTimeStamp` must be UTC. Using `Calendar.current` gives local time:

```swift
// BUG: Local time
let components = Calendar.current.dateComponents([.hour, .minute, .second], from: Date())

// FIX: Force UTC
let utc = TimeZone(identifier: "UTC")!
let components = Calendar(identifier: .gregorian).dateComponents(in: utc, from: timestamp)
```

### Bug 7: Using ISO 8601 Format for GPSDateStamp

```swift
// BUG: Hyphens (ISO 8601 format)
gps[kCGImagePropertyGPSDateStamp] = "2024-06-15"

// FIX: Colons (EXIF format)
gps[kCGImagePropertyGPSDateStamp] = "2024:06:15"
```

---

## Precision Reference

Relationship between decimal degree precision and ground distance at the
equator (maximum error; decreases toward poles):

| Decimal Places | Degrees | Approximate Distance |
|----------------|---------|---------------------|
| 0 | 1.0 | 111 km |
| 1 | 0.1 | 11.1 km |
| 2 | 0.01 | 1.11 km |
| 3 | 0.001 | 111 m |
| 4 | 0.0001 | 11.1 m |
| 5 | 0.00001 | 1.11 m |
| 6 | 0.000001 | 0.111 m |
| 7 | 0.0000001 | 11.1 mm |

Consumer GPS accuracy is typically 3--15 meters (4--5 decimal places).
iPhone GPS with good signal achieves ~5 meters. More precision in the
coordinate value does not improve actual positional accuracy.

A `Double` (IEEE 754 64-bit) has ~15--17 significant decimal digits, which
provides sub-millimeter resolution at any point on Earth -- far exceeding
GPS accuracy.
