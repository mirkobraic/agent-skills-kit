# GPS IFD -- Complete Tag Reference

> Part of [GPS Reference](README.md)

All 31 tags defined in the GPS IFD by the EXIF specification (CIPA DC-008).
The GPS IFD is a sub-IFD pointed to by IFD0 tag `0x8825`
(`GPSInfoIFDPointer`). Each tag entry follows the standard 12-byte IFD entry
format (tag ID, data type, count, value/offset).

For the underlying IFD binary format, data type definitions (BYTE, ASCII,
RATIONAL, etc.), and byte order conventions, see
[`../exif/technical-structure.md`](../exif/technical-structure.md).

---

## Version

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x0000 | GPSVersionID | BYTE | 4 | `kCGImagePropertyGPSVersion` | GPS IFD version. Current: `[2, 3, 0, 0]` (EXIF 2.3+). Mandatory when GPS IFD is present. Earlier version `[2, 2, 0, 0]` exists in older files. EXIF 3.0 retains `[2, 3, 0, 0]` (the GPS IFD version was not bumped). ImageIO returns this as a CFArray of four CFNumber values. |

---

## Coordinates

### Latitude

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x0001 | GPSLatitudeRef | ASCII | 2 | `kCGImagePropertyGPSLatitudeRef` | `"N"` = north latitude, `"S"` = south latitude. Count includes null terminator. |
| 0x0002 | GPSLatitude | RATIONAL | 3 | `kCGImagePropertyGPSLatitude` | Latitude as three RATIONALs: degrees, minutes, seconds. Each RATIONAL is a pair of unsigned 32-bit integers (numerator/denominator). See [coordinate-conventions.md](coordinate-conventions.md). |

**EXIF binary format:** Three RATIONAL values = 24 bytes. Example for 37 deg 46' 29.64":

```
Degrees:  37/1     (0x00000025 / 0x00000001)
Minutes:  46/1     (0x0000002E / 0x00000001)
Seconds:  2964/100 (0x00000B94 / 0x00000064)
```

**ImageIO format:** Single CFNumber (Double) in decimal degrees. ImageIO
converts the three RATIONALs to a single floating-point value automatically.
Example: `37.7749` (always positive; direction from `LatitudeRef`).

### Longitude

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x0003 | GPSLongitudeRef | ASCII | 2 | `kCGImagePropertyGPSLongitudeRef` | `"E"` = east longitude, `"W"` = west longitude. |
| 0x0004 | GPSLongitude | RATIONAL | 3 | `kCGImagePropertyGPSLongitude` | Longitude as three RATIONALs: degrees, minutes, seconds. Range: 0 to 180 degrees. |

Same binary format as latitude. ImageIO returns a single CFNumber in decimal
degrees (always positive).

### Altitude

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x0005 | GPSAltitudeRef | BYTE | 1 | `kCGImagePropertyGPSAltitudeRef` | `0` = above sea level, `1` = below sea level. Note: this is a BYTE, not ASCII like the other Ref tags. |
| 0x0006 | GPSAltitude | RATIONAL | 1 | `kCGImagePropertyGPSAltitude` | Altitude in meters as a single RATIONAL. Always a positive value; the sign is determined by AltitudeRef. |

**Example:** An altitude of 52.3 meters above sea level:

```
GPSAltitudeRef: 0
GPSAltitude:    5230/100
```

**ImageIO:** `kCGImagePropertyGPSAltitude` is a CFNumber (the absolute value),
`kCGImagePropertyGPSAltitudeRef` is a CFNumber (0 or 1).

**Altitude datum:** EXIF does not mandate a specific altitude reference system.
GPS receivers (including iPhone) typically report altitude relative to the
WGS-84 ellipsoid. Some third-party cameras report mean sea level (MSL)
altitude. The difference (geoid height) can be up to ~100 meters depending on
geographic location. See [`pitfalls.md`](pitfalls.md#8-phassetlocation-altitude-vs-gps-altitude).

---

## Timestamps

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x0007 | GPSTimeStamp | RATIONAL | 3 | `kCGImagePropertyGPSTimeStamp` | UTC time as three RATIONALs: hours (0--23), minutes (0--59), seconds (0.00--59.99). The seconds value may include fractional parts for sub-second precision. |
| 0x001D | GPSDateStamp | ASCII | 11 | `kCGImagePropertyGPSDateStamp` | UTC date as ASCII string: `"YYYY:MM:DD\0"`. Note the colon separators, not hyphens. 11 bytes including null terminator. |

**Critical:** GPSTimeStamp is always UTC, regardless of the camera's local
timezone. This differs from EXIF `DateTimeOriginal` which is local time
(unless `OffsetTimeOriginal` is present).

**EXIF binary format for GPSTimeStamp:**

```
Hour:    14/1     (0x0000000E / 0x00000001)
Minute:  30/1     (0x0000001E / 0x00000001)
Second:  4500/100 (0x00001194 / 0x00000064)  --> 45.00 seconds
```

**ImageIO format:** `kCGImagePropertyGPSTimeStamp` is returned as a CFString
in the format `"HH:MM:SS.SS"` (e.g., `"14:30:45.00"`). This differs from
the raw EXIF format (three RATIONALs). ImageIO handles the conversion
transparently in both directions. `kCGImagePropertyGPSDateStamp` is a CFString
`"YYYY:MM:DD"`.

**XMP equivalent:** In XMP, GPSDateStamp and GPSTimeStamp are combined into a
single `exif:GPSTimeStamp` tag as an ISO 8601 datetime string (e.g.,
`"2024-06-15T14:30:45Z"`). ImageIO synthesizes this when bridging to XMP.

**Relationship to DateTimeOriginal:** GPS time comes from the satellite
signal (atomic clock accuracy). EXIF DateTimeOriginal comes from the
camera's internal clock. The two should be consistent, but camera clocks
drift. GPS time is the authoritative UTC reference.

---

## Measurement Quality

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x0008 | GPSSatellites | ASCII | Any | `kCGImagePropertyGPSSatellites` | Satellites used for measurement. Format is not standardized -- may contain satellite count, IDs, or detailed NMEA-style info. Example: `"09"` (9 satellites). The EXIF spec allows NMEA-0183 format (e.g., `"03,05,12,..."` for satellite PRN numbers). |
| 0x0009 | GPSStatus | ASCII | 2 | `kCGImagePropertyGPSStatus` | Receiver status. `"A"` = measurement active (in progress), `"V"` = measurement void (interoperability mode). Based on NMEA GGA/RMC sentence status field. |
| 0x000A | GPSMeasureMode | ASCII | 2 | `kCGImagePropertyGPSMeasureMode` | Measurement dimensionality. `"2"` = 2-dimensional (latitude/longitude only, no altitude), `"3"` = 3-dimensional (latitude/longitude/altitude). Based on NMEA GSA sentence fix type. |
| 0x000B | GPSDOP | RATIONAL | 1 | `kCGImagePropertyGPSDOP` | Dilution of Precision. Lower values = better precision. When MeasureMode is `"2"`, this is HDOP (horizontal). When `"3"`, this is PDOP (positional). Typical range: 1.0 (ideal) to 20.0+ (poor). Values above 6.0 indicate degraded accuracy. |
| 0x001F | GPSHPositioningError | RATIONAL | 1 | `kCGImagePropertyGPSHPositioningError` | Horizontal positioning error in meters. Added in EXIF 2.31. iPhone writes this from `CLLocation.horizontalAccuracy`. Typical iPhone values: 3--65 meters. ImageIO constant available iOS 8.0+. |

### GPSHPositioningError (EXIF 2.31+)

This tag was added specifically to record the GPS accuracy reported by mobile
devices. On iOS, it maps directly to `CLLocation.horizontalAccuracy`:

```swift
// CLLocation.horizontalAccuracy --> GPSHPositioningError
let gpsDict: [CFString: Any] = [
    kCGImagePropertyGPSHPositioningError: location.horizontalAccuracy
]
```

The value represents the radius of uncertainty in meters. A value of 5.0
means the true location is within 5 meters of the recorded coordinates with
68% confidence (one standard deviation).

Typical values on iPhone:
- 3--5 meters: Excellent GPS signal (clear sky, many satellites)
- 10--15 meters: Good signal (typical outdoor)
- 30--65 meters: Degraded (indoor, urban canyon)
- 100+ meters: Wi-Fi or cell-tower positioning only

---

## Speed and Direction of Movement

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x000C | GPSSpeedRef | ASCII | 2 | `kCGImagePropertyGPSSpeedRef` | Speed unit. `"K"` = km/h, `"M"` = mph, `"N"` = knots. Default: `"K"`. |
| 0x000D | GPSSpeed | RATIONAL | 1 | `kCGImagePropertyGPSSpeed` | Speed of the GPS receiver at capture time. Unit defined by SpeedRef. Always a positive value (speed has no direction; that is GPSTrack). |
| 0x000E | GPSTrackRef | ASCII | 2 | `kCGImagePropertyGPSTrackRef` | Track reference. `"T"` = true north, `"M"` = magnetic north. |
| 0x000F | GPSTrack | RATIONAL | 1 | `kCGImagePropertyGPSTrack` | Direction of movement in degrees (0.00--359.99). 0 = north, 90 = east, 180 = south, 270 = west. This is a compass bearing, measured clockwise from north. |

**iOS mapping:** `CLLocation.speed` is in m/s. Conversion to km/h:
`speed * 3.6`. `CLLocation.course` (degrees from true north) maps directly
to `GPSTrack`. Both return `-1` when invalid -- check before writing.

**iPhone default:** Speed is written with `GPSSpeedRef = "K"` (km/h).

---

## Image Direction

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x0010 | GPSImgDirectionRef | ASCII | 2 | `kCGImagePropertyGPSImgDirectionRef` | Direction reference. `"T"` = true north, `"M"` = magnetic north. |
| 0x0011 | GPSImgDirection | RATIONAL | 1 | `kCGImagePropertyGPSImgDirection` | Direction the camera was facing when the image was captured, in degrees (0.00--359.99). Measured clockwise from the reference direction. |

**Distinction from GPSTrack:** `GPSTrack` is the direction of *movement*
(where the device is going). `GPSImgDirection` is the direction the camera
*faces* (where it is pointing). A person walking north while photographing
to the east would have `GPSTrack = 0` (north) and `GPSImgDirection = 90`
(east).

**iOS mapping:** `CLHeading.trueHeading` maps to `GPSImgDirection` with
`GPSImgDirectionRef = "T"`. If only magnetic heading is available, use
`CLHeading.magneticHeading` with `GPSImgDirectionRef = "M"`. The iPhone
Camera app writes `GPSImgDirectionRef = "T"` with the true heading from the
magnetometer/gyroscope fusion.

---

## Map Datum

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x0012 | GPSMapDatum | ASCII | Any | `kCGImagePropertyGPSMapDatum` | Geodetic survey datum. Almost always `"WGS-84"` for GPS data. In Japan, may be `"TOKYO"` for the older Tokyo Datum (now superseded by JGD2000/JGD2011). |

All modern GPS receivers use WGS-84. This tag is informational -- it tells
consumers which datum the coordinates reference. If absent, WGS-84 is
assumed. iPhone always writes `"WGS-84"`.

---

## Destination

Destination tags describe a point of interest the camera is directed toward.
These are rarely used by consumer cameras but supported by the EXIF
specification for navigation and surveying applications.

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x0013 | GPSDestLatitudeRef | ASCII | 2 | `kCGImagePropertyGPSDestLatitudeRef` | `"N"` or `"S"` |
| 0x0014 | GPSDestLatitude | RATIONAL | 3 | `kCGImagePropertyGPSDestLatitude` | Destination latitude: degrees, minutes, seconds. Same format as GPSLatitude. |
| 0x0015 | GPSDestLongitudeRef | ASCII | 2 | `kCGImagePropertyGPSDestLongitudeRef` | `"E"` or `"W"` |
| 0x0016 | GPSDestLongitude | RATIONAL | 3 | `kCGImagePropertyGPSDestLongitude` | Destination longitude: degrees, minutes, seconds. Same format as GPSLongitude. |
| 0x0017 | GPSDestBearingRef | ASCII | 2 | `kCGImagePropertyGPSDestBearingRef` | `"T"` = true north, `"M"` = magnetic north. |
| 0x0018 | GPSDestBearing | RATIONAL | 1 | `kCGImagePropertyGPSDestBearing` | Bearing to destination point (0.00--359.99 degrees). |
| 0x0019 | GPSDestDistanceRef | ASCII | 2 | `kCGImagePropertyGPSDestDistanceRef` | `"K"` = kilometers, `"M"` = miles, `"N"` = nautical miles. |
| 0x001A | GPSDestDistance | RATIONAL | 1 | `kCGImagePropertyGPSDestDistance` | Distance to the destination point. Unit defined by DestDistanceRef. |

**ImageIO keys:** All destination keys follow the same pattern as the primary
coordinate keys. Values are CFNumber (absolute) with separate Ref strings.

**Use cases:** Navigation photography, surveying, military applications,
augmented reality apps that tag what the camera was pointed at.

---

## Processing Method and Area Information

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x001B | GPSProcessingMethod | UNDEFINED | Any | `kCGImagePropertyGPSProcessingMethod` | Name of the method used for location finding. Encoded with an 8-byte character set prefix (same format as EXIF UserComment). |
| 0x001C | GPSAreaInformation | UNDEFINED | Any | `kCGImagePropertyGPSAreaInformation` | Name of the GPS area. Same 8-byte charset prefix encoding as GPSProcessingMethod. |

### Character Set Prefix

Both tags use the same encoding scheme as the EXIF `UserComment` tag. The
first 8 bytes identify the character encoding:

| Prefix (8 bytes) | Encoding |
|-------------------|----------|
| `ASCII\0\0\0` | 7-bit ASCII |
| `JIS\0\0\0\0\0` | JIS X0208-1990 |
| `UNICODE\0` | Unicode (UCS-2) |
| `\0\0\0\0\0\0\0\0` | Undefined (implementation-specific) |

The remainder of the data after the 8-byte prefix is the actual text content.

**Common GPSProcessingMethod values:**
- `"GPS"` -- standard GPS satellite positioning
- `"CELLID"` -- cell tower triangulation
- `"WLAN"` -- Wi-Fi positioning (e.g., Apple's Wi-Fi location service)
- `"A-GPS"` -- assisted GPS (uses network data to speed up satellite lock)
- `"MANUAL"` -- manually entered coordinates

**ImageIO:** Returns these as CFString values with the charset prefix stripped.

---

## Differential Correction

| Tag ID | Name | Type | Count | ImageIO Key | Description |
|--------|------|------|-------|-------------|-------------|
| 0x001E | GPSDifferential | SHORT | 1 | `kCGImagePropertyGPSDifferental` | `0` = no differential correction, `1` = differential correction applied (DGPS). |

**Note the ImageIO spelling:** The constant is `kCGImagePropertyGPSDifferental`
(missing an 'i' -- "Diferental" instead of "Differential"). This is a known
Apple typo that has persisted since iOS 4.0 and cannot be corrected without
breaking backward compatibility.

DGPS (Differential GPS) uses ground-based reference stations to improve
accuracy from ~5-10 meters to ~1-3 meters. Consumer smartphones do not
typically use DGPS, so this tag is rarely seen in iPhone photos.

---

## Complete Tag Summary Table

Quick-reference table of all 31 GPS IFD tags sorted by tag ID:

| Tag ID | Dec | Name | Type | Count | Value Range / Meaning |
|--------|-----|------|------|-------|-----------------------|
| 0x0000 | 0 | GPSVersionID | BYTE | 4 | `[2,3,0,0]` |
| 0x0001 | 1 | GPSLatitudeRef | ASCII | 2 | `"N"` / `"S"` |
| 0x0002 | 2 | GPSLatitude | RATIONAL | 3 | DMS: 0--90 deg |
| 0x0003 | 3 | GPSLongitudeRef | ASCII | 2 | `"E"` / `"W"` |
| 0x0004 | 4 | GPSLongitude | RATIONAL | 3 | DMS: 0--180 deg |
| 0x0005 | 5 | GPSAltitudeRef | BYTE | 1 | 0=above, 1=below sea level |
| 0x0006 | 6 | GPSAltitude | RATIONAL | 1 | Meters (positive) |
| 0x0007 | 7 | GPSTimeStamp | RATIONAL | 3 | H (0--23), M (0--59), S (0--59.99) UTC |
| 0x0008 | 8 | GPSSatellites | ASCII | Any | Free-form satellite info |
| 0x0009 | 9 | GPSStatus | ASCII | 2 | `"A"` active / `"V"` void |
| 0x000A | 10 | GPSMeasureMode | ASCII | 2 | `"2"` 2D / `"3"` 3D |
| 0x000B | 11 | GPSDOP | RATIONAL | 1 | Dilution of precision (lower=better) |
| 0x000C | 12 | GPSSpeedRef | ASCII | 2 | `"K"` km/h / `"M"` mph / `"N"` knots |
| 0x000D | 13 | GPSSpeed | RATIONAL | 1 | Speed (positive) |
| 0x000E | 14 | GPSTrackRef | ASCII | 2 | `"T"` true / `"M"` magnetic |
| 0x000F | 15 | GPSTrack | RATIONAL | 1 | 0.00--359.99 degrees |
| 0x0010 | 16 | GPSImgDirectionRef | ASCII | 2 | `"T"` true / `"M"` magnetic |
| 0x0011 | 17 | GPSImgDirection | RATIONAL | 1 | 0.00--359.99 degrees |
| 0x0012 | 18 | GPSMapDatum | ASCII | Any | e.g., `"WGS-84"` |
| 0x0013 | 19 | GPSDestLatitudeRef | ASCII | 2 | `"N"` / `"S"` |
| 0x0014 | 20 | GPSDestLatitude | RATIONAL | 3 | DMS: 0--90 deg |
| 0x0015 | 21 | GPSDestLongitudeRef | ASCII | 2 | `"E"` / `"W"` |
| 0x0016 | 22 | GPSDestLongitude | RATIONAL | 3 | DMS: 0--180 deg |
| 0x0017 | 23 | GPSDestBearingRef | ASCII | 2 | `"T"` true / `"M"` magnetic |
| 0x0018 | 24 | GPSDestBearing | RATIONAL | 1 | 0.00--359.99 degrees |
| 0x0019 | 25 | GPSDestDistanceRef | ASCII | 2 | `"K"` km / `"M"` miles / `"N"` naut. mi |
| 0x001A | 26 | GPSDestDistance | RATIONAL | 1 | Distance (positive) |
| 0x001B | 27 | GPSProcessingMethod | UNDEFINED | Any | 8-byte charset prefix + method name |
| 0x001C | 28 | GPSAreaInformation | UNDEFINED | Any | 8-byte charset prefix + area name |
| 0x001D | 29 | GPSDateStamp | ASCII | 11 | `"YYYY:MM:DD\0"` UTC |
| 0x001E | 30 | GPSDifferential | SHORT | 1 | 0=none / 1=DGPS correction |
| 0x001F | 31 | GPSHPositioningError | RATIONAL | 1 | Meters (EXIF 2.31+) |

---

## Tags Commonly Written by iPhone

When an iPhone captures a photo with location services enabled, it typically
writes these GPS tags:

| Tag | Source | Notes |
|-----|--------|-------|
| GPSLatitude + Ref | `CLLocation.coordinate.latitude` | Split into absolute value + N/S |
| GPSLongitude + Ref | `CLLocation.coordinate.longitude` | Split into absolute value + E/W |
| GPSAltitude + Ref | `CLLocation.altitude` | Ref=0 when positive, Ref=1 when negative |
| GPSTimeStamp | `CLLocation.timestamp` | Converted to UTC, three RATIONALs |
| GPSDateStamp | `CLLocation.timestamp` | UTC date portion, `"YYYY:MM:DD"` |
| GPSSpeed + Ref | `CLLocation.speed` | Converted from m/s to km/h (Ref="K") |
| GPSImgDirection + Ref | `CLHeading.trueHeading` | Ref="T" for true north |
| GPSHPositioningError | `CLLocation.horizontalAccuracy` | Meters, radius of uncertainty |
| GPSMapDatum | Hardcoded | Always `"WGS-84"` |
| GPSVersionID | Hardcoded | `[2, 3, 0, 0]` |

Tags the iPhone does **not** typically write: GPSSatellites, GPSStatus,
GPSMeasureMode, GPSDOP, GPSTrack (course of travel), GPSDestination tags,
GPSProcessingMethod, GPSAreaInformation, GPSDifferential.

---

## EXIF Data Types Used in GPS IFD

Quick reference for the data types appearing in GPS tags:

| Type | ID | Size | Description | GPS Usage |
|------|----|------|-------------|-----------|
| BYTE | 1 | 1 byte | Unsigned 8-bit integer | GPSVersionID (x4), GPSAltitudeRef |
| ASCII | 2 | 1 byte | 7-bit ASCII, null-terminated | All Ref tags, GPSSatellites, GPSMapDatum, GPSDateStamp |
| SHORT | 3 | 2 bytes | Unsigned 16-bit integer | GPSDifferential |
| RATIONAL | 5 | 8 bytes | Two unsigned LONGs (num/denom) | Coordinates, altitude, time, speed, direction, distance, DOP, error |
| UNDEFINED | 7 | 1 byte | Arbitrary bytes | GPSProcessingMethod, GPSAreaInformation |

The GPS IFD does not use LONG, SLONG, SRATIONAL, FLOAT, or DOUBLE types.
All numeric measurements use unsigned RATIONAL, which is why coordinates
require separate reference tags for sign information.
