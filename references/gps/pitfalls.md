# GPS Metadata Pitfalls

> Part of [GPS Reference](README.md)

Known bugs, misconceptions, and edge cases when working with GPS metadata in
iOS/macOS. Each entry describes the problem, shows the bug, and provides the
fix.

---

## 1. Signed vs Unsigned Coordinate Bug

**The single most common GPS metadata bug.**

EXIF and ImageIO store GPS coordinates as **absolute (positive) values** with
a separate reference tag indicating the hemisphere. Passing a signed
(negative) value does not work -- ImageIO takes the absolute value silently.

### The Bug

```swift
// BUG: Negative longitude is treated as positive by ImageIO.
// This stores 122.4194 E instead of 122.4194 W.
let gps: [String: Any] = [
    kCGImagePropertyGPSLatitude:  37.7749,
    kCGImagePropertyGPSLongitude: -122.4194  // Sign is ignored!
]
```

A photo taken in San Francisco (western hemisphere) ends up tagged at
122.4194 E in Jiangxi, China (eastern hemisphere, same absolute longitude).
The error is approximately 19,600 km.

### The Fix

```swift
let gps: [String: Any] = [
    kCGImagePropertyGPSLatitude:     abs(location.coordinate.latitude),
    kCGImagePropertyGPSLatitudeRef:  location.coordinate.latitude >= 0 ? "N" : "S",
    kCGImagePropertyGPSLongitude:    abs(location.coordinate.longitude),
    kCGImagePropertyGPSLongitudeRef: location.coordinate.longitude >= 0 ? "E" : "W",
]
```

**Always** use `abs()` on the coordinate and set the `*Ref` tag based on the
sign. See [coordinate-conventions.md](coordinate-conventions.md) for a
complete `CLLocation` --> GPS dictionary conversion function.

### Why This Happens

`CLLocation.coordinate` uses signed decimal degrees (the DD format), where
negative latitude means south and negative longitude means west. EXIF uses
unsigned RATIONAL values because the data type does not support negative
numbers -- the direction is encoded separately. Developers accustomed to
the DD convention naturally pass signed values, not realizing ImageIO
silently discards the sign.

---

## 2. Altitude Reference (Above vs Below Sea Level)

`GPSAltitudeRef` is a single BYTE: `0` = above sea level, `1` = below sea
level. The `GPSAltitude` value itself is always positive (unsigned RATIONAL).

### The Bug

```swift
// BUG: Negative altitude passed directly.
// ImageIO may store this as 0 meters or take the absolute value
// without setting AltitudeRef to 1.
gps[kCGImagePropertyGPSAltitude] = location.altitude  // Could be -30.5
```

### The Fix

```swift
gps[kCGImagePropertyGPSAltitude]    = abs(location.altitude)
gps[kCGImagePropertyGPSAltitudeRef] = location.altitude >= 0 ? 0 : 1
```

### Altitude Datum Ambiguity

`CLLocation.altitude` reports altitude relative to the **WGS-84 reference
ellipsoid** (geometric/ellipsoidal altitude). EXIF `GPSAltitude` does not
specify the altitude reference system, though WGS-84 is the de facto
standard for GPS data.

The difference between ellipsoidal altitude and mean sea level (geoid)
altitude can be significant -- up to ~100 meters in some regions (e.g., the
Indian Ocean has a geoid low of about -105 m). In practice, most GPS
receivers and iOS both report ellipsoidal altitude.

For precision applications, `CLLocation.ellipsoidalAltitude` (iOS 15+) is
guaranteed WGS-84 ellipsoidal.

---

## 3. GPSTimeStamp is UTC, Not Local Time

`GPSTimeStamp` is always in **UTC** (Coordinated Universal Time), regardless
of the device's timezone setting. This is different from EXIF
`DateTimeOriginal`, which records local time.

### The Bug

```swift
// BUG: Using local time components for GPS timestamp.
let components = Calendar.current.dateComponents(
    [.hour, .minute, .second], from: Date()
)
gps[kCGImagePropertyGPSTimeStamp] = String(
    format: "%02d:%02d:%02d",
    components.hour!, components.minute!, components.second!
)
// If local time is 2:30 PM EDT (UTC-4), this writes "14:30:00"
// but the correct GPS time should be "18:30:00" (UTC).
```

### The Fix

```swift
let utc = TimeZone(identifier: "UTC")!
let components = Calendar(identifier: .gregorian)
    .dateComponents(in: utc, from: location.timestamp)

gps[kCGImagePropertyGPSTimeStamp] = String(
    format: "%02d:%02d:%02d",
    components.hour ?? 0, components.minute ?? 0, components.second ?? 0
)
gps[kCGImagePropertyGPSDateStamp] = String(
    format: "%04d:%02d:%02d",
    components.year ?? 0, components.month ?? 0, components.day ?? 0
)
```

### Consequences

- A photo taken at 2:30 PM EDT gets tagged as taken at 2:30 PM UTC -- a
  4-hour error.
- Tools that cross-reference GPS time with EXIF `DateTimeOriginal` (e.g.,
  for geotagging from a GPS track log) will produce incorrect locations.
- The date can also be wrong: if local time is 11:00 PM EDT on June 15,
  UTC is 3:00 AM on June **16**. Using `Calendar.current` for the date
  component would record June 15 instead of June 16.

### Background: GPS Time vs Camera Time

GPS timestamps derive from satellite atomic clocks and are inherently UTC.
Camera time (`DateTimeOriginal`) is whatever the user set the camera clock
to. On iPhone, both are accurate because iOS synchronizes the device clock
via NTP servers, but on third-party cameras the device clock may drift by
seconds or minutes.

---

## 4. GPSDateStamp Format: Colons, Not Hyphens

`GPSDateStamp` uses the EXIF date format `"YYYY:MM:DD"` -- **colons** as
separators. This is different from ISO 8601 (`"YYYY-MM-DD"`).

### The Bug

```swift
// BUG: ISO 8601 format with hyphens.
gps[kCGImagePropertyGPSDateStamp] = "2024-06-15"  // Wrong separator

// Also wrong: slash separators
gps[kCGImagePropertyGPSDateStamp] = "2024/06/15"
```

### The Fix

```swift
gps[kCGImagePropertyGPSDateStamp] = "2024:06:15"
```

ImageIO is generally tolerant of the hyphen format when reading, but writing
the correct colon format ensures maximum compatibility with other tools
(ExifTool, Adobe products, Google Photos).

---

## 5. Speed Reference Units

`GPSSpeedRef` defines the unit for `GPSSpeed`. The three options are often
confused, and `CLLocation.speed` is in m/s -- a unit not directly supported
by EXIF.

| Ref | Unit | From m/s (CLLocation) |
|-----|------|----------------------|
| `"K"` | Kilometers per hour | `speed * 3.6` |
| `"M"` | Miles per hour | `speed * 2.23694` |
| `"N"` | Knots (nautical miles per hour) | `speed * 1.94384` |

### The Bug

```swift
// BUG: CLLocation.speed is in m/s, but writing without conversion.
gps[kCGImagePropertyGPSSpeed] = location.speed     // m/s, not km/h!
gps[kCGImagePropertyGPSSpeedRef] = "K"             // Claims km/h
```

A speed of 10 m/s (36 km/h) gets written as 10 km/h -- a 3.6x error.

### The Fix

```swift
if location.speed >= 0 {
    gps[kCGImagePropertyGPSSpeed]    = location.speed * 3.6  // m/s --> km/h
    gps[kCGImagePropertyGPSSpeedRef] = "K"
}
```

**Important:** Check `speed >= 0` before writing. `CLLocation.speed` returns
`-1` when the speed is invalid or unknown (device stationary, GPS signal
insufficient). Writing `-1` as a GPS speed produces nonsensical data.

**iPhone default:** The Camera app writes speed in km/h (`SpeedRef = "K"`).

---

## 6. Missing GPSMapDatum

`GPSMapDatum` should be `"WGS-84"` for GPS-derived coordinates. If absent,
readers typically assume WGS-84, but some tools may flag the data as
ambiguous.

### The Bug

Omitting `GPSMapDatum` entirely. While most software handles this gracefully,
professional geospatial tools (GIS applications, surveying software) may
reject coordinates without an explicit datum.

### The Fix

```swift
gps[kCGImagePropertyGPSMapDatum] = "WGS-84"
```

The only common alternative is `"TOKYO"` for the Japanese geodetic datum
(JGD2000 or older Tokyo Datum). All modern GPS receivers use WGS-84.

### Datum Confusion

The string `"WGS-84"` is the EXIF convention. Some tools write `"WGS84"`,
`"WGS 84"`, or `"World Geodetic System 1984"`. The EXIF specification does
not mandate a specific string format beyond recording the datum used. For
maximum compatibility, use `"WGS-84"` (the form iPhone writes).

---

## 7. GPS Metadata Not Stripped by Default in iOS Sharing

When sharing photos from the iOS Photos app, GPS metadata is **included by
default**. The user must manually toggle "Location" off in the share sheet
options each time they share.

### Key Facts

- The "Location" toggle in Share Options resets to **ON** every time the
  share sheet opens. There is no persistent setting.
- AirDrop with "All Photos Data" includes full metadata with no way to
  selectively exclude GPS.
- Third-party social media apps (Facebook, Instagram, WhatsApp, Signal)
  strip EXIF metadata on their side during upload -- but the original file
  sent to the app still contains it.
- iMessage preserves full EXIF metadata in attachments.

### For App Developers

If your app shares user photos, consider:

1. **Strip GPS by default** when sharing to external services.
2. **Provide a clear toggle** if users should choose.
3. Use `kCGImageMetadataShouldExcludeGPS` for lossless stripping.
4. Remember that `kCGImageMetadataShouldExcludeGPS` does **not** strip
   MakerNote location data. See pitfall #9.
5. Consider stripping IPTC location fields (City, State, Country) as well.

---

## 8. PHAsset.location Altitude vs GPS Altitude

`PHAsset.location.altitude` and EXIF `GPSAltitude` can report different
values for the same photo.

### Why They Differ

- `CLLocation.altitude` is the altitude relative to the **WGS-84 reference
  ellipsoid** (geometric/ellipsoidal altitude).
- `GPSAltitude` in EXIF does not mandate a specific reference, though GPS
  receivers typically write ellipsoidal altitude.
- Photos may adjust `PHAsset.location` during import or reverse-geocoding.
- Some third-party cameras write altitude relative to mean sea level (MSL),
  which differs from the WGS-84 ellipsoid by the local geoid height (can
  be -100 to +85 meters depending on location).

### Practical Impact

For most consumer use cases, the difference is negligible (< 1 meter when
the source is an iPhone). But for precision applications:

- Check `GPSMapDatum` to confirm the datum.
- Be aware that mixing ellipsoidal and MSL altitudes can produce large
  errors in mountainous or extreme-latitude regions.
- `CLLocation.ellipsoidalAltitude` (iOS 15+) is guaranteed to be WGS-84
  ellipsoidal.

---

## 9. GPS Stripping Does NOT Remove MakerNote Location Data

`kCGImageMetadataShouldExcludeGPS` strips the GPS IFD and corresponding XMP
tags, but does **not** filter:

- **Apple MakerNote:** May contain location-related processing metadata
  (computational photography parameters that could be correlated with
  location, scene classification data).
- **Other vendor MakerNotes:** Some camera manufacturers (certain Samsung
  and Huawei models) embed GPS coordinates directly in their proprietary
  MakerNote fields.
- **Custom XMP properties:** Third-party tools may write location to
  non-standard XMP namespaces.
- **IPTC location fields:** City, State/Province, Country, Sub-location
  are semantic location data (not GPS coordinates) and are not stripped.

### Complete Location Removal

For truly comprehensive location removal:

1. Use `kCGImageMetadataShouldExcludeGPS` to strip GPS IFD and XMP GPS.
2. Remove the MakerNote. `kCGImagePropertyExifMakerNote` is read-only
   in ImageIO -- removing it requires either binary-level EXIF editing or
   writing pixels only (no metadata copy).
3. Remove IPTC location fields if present (City, State, Country, Sub-location).
4. Or: create a new image from pixels only (no metadata copy). This is the
   safest approach but loses all other metadata too (camera settings,
   timestamps, ICC profile, etc.).

See [imageio-mapping.md](imageio-mapping.md#gps-stripping-removing-location-data)
for code examples of all stripping methods.

---

## 10. kCGImagePropertyGPSDifferental Typo

The ImageIO constant for the GPS differential correction tag is misspelled:

```swift
kCGImagePropertyGPSDifferental  // Missing 'i' -- "Diferental" not "Differential"
```

This is a known Apple SDK bug preserved for backward compatibility. Using
the correct English spelling will not compile:

```swift
// DOES NOT EXIST:
// kCGImagePropertyGPSDifferential  <-- Not a valid constant
```

The workaround is straightforward -- just use the misspelled constant. But
be aware of it when:
- Searching documentation or code for "Differential"
- Writing wrapper code that uses the correct English spelling in method/property names
- Reading code from developers who worked around this with a custom alias

---

## 11. GPSTimeStamp Format Varies Between Reading and Writing

When **reading**, ImageIO returns `kCGImagePropertyGPSTimeStamp` as a
CFString in `"HH:MM:SS.SS"` format (e.g., `"14:30:45.00"`).

When **writing**, ImageIO accepts either:
- A CFString in `"HH:MM:SS"` or `"HH:MM:SS.SS"` format
- The same format it returns when reading

However, the raw EXIF format is three RATIONAL values (H, M, S). ImageIO
handles this conversion transparently, but if you write EXIF data with a
non-ImageIO tool (ExifTool, libexif, raw binary manipulation), you must
use three RATIONALs, not a string.

### Parsing GPSTimeStamp

When reading the timestamp for conversion, handle both with and without
fractional seconds:

```swift
let timeStr = gpsDict[kCGImagePropertyGPSTimeStamp as String] as? String
// Could be "14:30:45" or "14:30:45.00" or "14:30:45.123"
let cleanTime = timeStr?.components(separatedBy: ".").first ?? timeStr
```

---

## 12. Coordinate Precision and RATIONAL Denominator Choice

When writing GPS data with tools that construct raw EXIF (not ImageIO),
the choice of RATIONAL denominator affects coordinate precision:

| Seconds Denominator | Precision | Use Case |
|--------------------|-----------|----------|
| 1 | ~30 meters | Very rough (city-level) |
| 10 | ~3 meters | Adequate for most consumer use |
| 100 | ~0.3 meters | Good (ImageIO default when converting DD to DMS) |
| 1000 | ~0.03 meters | High precision |
| 10000 | ~0.003 meters | Overkill for consumer GPS |

ImageIO handles this automatically when you provide a Double for
`kCGImagePropertyGPSLatitude` -- it chooses an appropriate denominator.
This is only a concern when building raw EXIF binary data directly with
tools like ExifTool, libexif, or custom binary writers.

### Alternative: DD-in-RATIONAL

Some tools encode coordinates as a single RATIONAL in the degrees position
with minutes and seconds set to 0/1:

```
GPSLatitude: 377749/10000, 0/1, 0/1
```

This is valid EXIF but may confuse tools that expect the traditional DMS
layout. ImageIO handles both encodings correctly when reading.

---

## 13. GPS Version ID Requirement

The EXIF specification states that `GPSVersionID` (tag 0x0000) is
**mandatory** when a GPS IFD is present. Some tools do not write it.

### Impact

Most readers handle a missing version ID gracefully, but strict validators
may reject the GPS data. Always write it:

```swift
gps[kCGImagePropertyGPSVersion] = [2, 3, 0, 0] as [Int]
```

The current version is `[2, 3, 0, 0]` (GPS IFD version 2.3, corresponding
to EXIF 2.3/2.31/2.32/3.0). The GPS IFD version was not bumped in EXIF 3.0.
Older files may contain `[2, 2, 0, 0]` (EXIF 2.2).

---

## Quick Reference: Pitfall Summary

| # | Pitfall | Severity | Likelihood | Section |
|---|---------|----------|------------|---------|
| 1 | Signed coordinate values | **Critical** | Very common | [Coordinates](#1-signed-vs-unsigned-coordinate-bug) |
| 2 | Negative altitude without AltitudeRef | High | Common | [Altitude](#2-altitude-reference-above-vs-below-sea-level) |
| 3 | Local time instead of UTC | High | Common | [Timestamps](#3-gpstimestamp-is-utc-not-local-time) |
| 4 | Hyphens instead of colons in DateStamp | Low | Occasional | [DateStamp](#4-gpsdatestamp-format-colons-not-hyphens) |
| 5 | Speed unit mismatch (m/s vs km/h) | Medium | Common | [Speed](#5-speed-reference-units) |
| 6 | Missing GPSMapDatum | Low | Common | [Datum](#6-missing-gpsmapdatum) |
| 7 | GPS not stripped by default in sharing | **Critical** (privacy) | Always | [Sharing](#7-gps-metadata-not-stripped-by-default-in-ios-sharing) |
| 8 | PHAsset altitude vs GPS altitude | Low | Rare | [PHAsset altitude](#8-phassetlocation-altitude-vs-gps-altitude) |
| 9 | MakerNote location not stripped | High (privacy) | Always | [MakerNote](#9-gps-stripping-does-not-remove-makernote-location-data) |
| 10 | kCGImagePropertyGPSDifferental typo | Low (compile) | Once | [Typo](#10-kcgimagepropertygpsdifferental-typo) |
| 11 | TimeStamp format string vs RATIONAL | Low | Rare | [TimeStamp](#11-gpstimestamp-format-varies-between-reading-and-writing) |
| 12 | RATIONAL denominator precision | Low | Rare | [Precision](#12-coordinate-precision-and-rational-denominator-choice) |
| 13 | Missing GPSVersionID | Low | Occasional | [VersionID](#13-gps-version-id-requirement) |

### Priority for New Code

If you are writing GPS metadata for the first time, address these in order:

1. **Use `abs()` + Ref tags** for all coordinates and altitude (pitfalls 1, 2)
2. **Convert timestamps to UTC** (pitfall 3)
3. **Convert speed from m/s** to km/h (pitfall 5)
4. **Use colon separators** in DateStamp (pitfall 4)
5. **Include GPSVersionID and GPSMapDatum** (pitfalls 6, 13)
6. **Strip GPS before sharing** if your app handles user photos (pitfall 7)

The `gpsDictionary(from:)` function in
[coordinate-conventions.md](coordinate-conventions.md) handles all of these
correctly.
