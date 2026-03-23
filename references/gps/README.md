# GPS IFD Reference

> Part of [iOS Image Metadata Skill](../../SKILL.md) · [References Index](../README.md)

The GPS IFD (Image File Directory) stores geolocation and positioning metadata
within the EXIF structure. It is pointed to by IFD0 tag `0x8825`
(`GPSInfoIFDPointer`). Apple exposes it as a separate dictionary via
`kCGImagePropertyGPSDictionary` (iOS 4.0+).

---

## Overview

GPS metadata records **where** a photo was taken (and optionally where the
camera was pointing or heading). The GPS IFD contains up to 31 tags covering:

- **Position** -- latitude, longitude, altitude
- **Timing** -- UTC timestamp and date
- **Movement** -- speed, track (direction of travel)
- **Image direction** -- compass bearing the camera faced
- **Destination** -- target location, bearing, and distance
- **Quality** -- satellites, DOP, measurement mode, positioning error
- **System** -- version, map datum, processing method, differential correction

### The #1 Pitfall

GPS coordinates in EXIF use **absolute values + reference letters**, NOT signed
decimals. A point at 37.7749 N, 122.4194 W is stored as:

```
GPSLatitude:     37.7749    GPSLatitudeRef:  "N"
GPSLongitude:    122.4194   GPSLongitudeRef: "W"
```

ImageIO ignores the sign of coordinate values. Passing `-122.4194` as
`kCGImagePropertyGPSLongitude` produces wrong results -- the photo ends up
tagged in the eastern hemisphere (China) instead of the western hemisphere
(San Francisco). See [coordinate-conventions.md](coordinate-conventions.md)
for full details and conversion code.

---

## File Index

| File | Contents |
|------|----------|
| [`tag-reference.md`](tag-reference.md) | All 31 GPS IFD tags -- tag IDs (hex), EXIF data types, component counts, value ranges, ImageIO key names, iPhone behavior |
| [`coordinate-conventions.md`](coordinate-conventions.md) | Coordinate formats (DMS, DD, DM, RATIONAL), signed-to-unsigned conversion, CLLocation/CLHeading conversion code, XMP GPSCoordinate format, common conversion bugs |
| [`imageio-mapping.md`](imageio-mapping.md) | All `kCGImagePropertyGPS*` constants with CFType mapping, reading/writing GPS in Swift, lossless updates, PHAsset.location vs EXIF GPS, GPS stripping (3 methods), CLLocation property mapping, iOS sharing behavior |
| [`pitfalls.md`](pitfalls.md) | 13 pitfalls: signed coordinates, altitude reference, UTC timestamps, date format, speed units, missing datum, privacy/sharing defaults, PHAsset altitude, MakerNote location leak, SDK typo, TimeStamp format, RATIONAL precision, version ID |

---

## Format Support

GPS metadata is part of the EXIF standard. It is supported in formats that
carry EXIF data:

| Format | GPS Support | Notes |
|--------|-------------|-------|
| **JPEG** | Full | APP1 segment, 64 KB limit for all EXIF |
| **HEIF/HEIC** | Full | EXIF item in ISOBMFF container, no 64 KB limit |
| **TIFF** | Full | Native IFD structure |
| **DNG** | Full | TIFF-based, EXIF IFD location preferred |
| **PNG** | Via eXIf chunk | PNG 1.5+; adoption growing |
| **WebP** | Via EXIF chunk | Read-only in ImageIO |
| **AVIF** | Via EXIF item | ISOBMFF container like HEIF |
| **GIF** | Not supported | No EXIF capability |

---

## WGS-84 Datum

All modern GPS receivers -- including every iPhone -- use the WGS-84 (World
Geodetic System 1984, EPSG:4326) geodetic datum. EXIF records this in the
`GPSMapDatum` tag. When absent, WGS-84 is assumed.

WGS-84 defines:
- An Earth-centered ellipsoid (semi-major axis 6,378,137 m, flattening 1/298.257223563)
- Latitude: -90 to +90 degrees (south to north)
- Longitude: -180 to +180 degrees (west to east)
- Altitude: meters above the WGS-84 reference ellipsoid (not mean sea level)

The difference between WGS-84 ellipsoidal altitude and mean sea level (MSL)
varies by region (the "geoid height"), ranging from roughly -100 m to +85 m
globally. For most consumer use cases this is irrelevant, but it matters for
precision surveying.

---

## GPS Data Flow on iPhone

```
CLLocationManager ─── CLLocation ───┬──── Camera app ──── EXIF GPS IFD
                                    │                        (in image file)
                                    │
                                    └──── Photos library ── PHAsset.location
                                                              (in database)
```

Both paths originate from the same `CLLocation`, but they store data in
different formats and locations. See
[imageio-mapping.md](imageio-mapping.md#phassetlocation-vs-exif-gps) for the
detailed comparison.

---

## Cross-References

- **ImageIO GPS keys:** [`../imageio/property-keys.md`](../imageio/property-keys.md) -- GPS Dictionary section
- **ImageIO GPS pitfalls:** [`../imageio/pitfalls.md`](../imageio/pitfalls.md) -- GPS coordinate convention, GPS stripping, MakerNote caveat
- **EXIF IFD structure:** [`../exif/technical-structure.md`](../exif/technical-structure.md) -- GPS IFD tag table, IFD0 pointer tag 0x8825, data types, byte order
- **EXIF pitfalls:** [`../exif/pitfalls.md`](../exif/pitfalls.md) -- MakerNote location data not stripped by GPS exclusion
- **EXIF MakerNote:** [`../exif/makernote.md`](../exif/makernote.md) -- Apple MakerNote may contain location-related processing data

---

## Key Specifications

| Specification | Relevance |
|---------------|-----------|
| CIPA DC-008 (EXIF 2.31 / 2.32 / 3.0) | Defines GPS IFD tags; added GPSHPositioningError in 2.31 |
| CIPA DC-X010-2017 | XMP GPS coordinate format (`GPSCoordinate` type: `DDD,MM.mmk`) |
| WGS-84 (EPSG:4326) | Standard geodetic datum for GPS coordinates |
| ISO 6709 | Geographic point location representation |
| NMEA 0183 | GPS sentence format; basis for GPSSatellites and GPSStatus values |
