---
name: gps
description: Use when tasks involve GPS/geolocation metadata in images — coordinate encoding, sign/ref conventions, altitude, heading, or kCGImagePropertyGPS* keys on iOS/macOS.
---

# GPS Metadata

## Use For

- Reading or writing GPS coordinates in image metadata.
- Understanding GPS IFD tag conventions (absolute values + N/S/E/W refs).
- Mapping GPS tags to `kCGImagePropertyGPS*` ImageIO keys.
- Altitude, heading, speed, and timestamp tags.
- Debugging wrong/inverted coordinates.

## Do Not Use For

- Non-GPS EXIF tags — use the `exif` skill.
- CoreLocation APIs (this skill covers metadata, not device location).

## Workflow

1. For writes: use absolute values + `Ref` letters (`N`/`S`, `E`/`W`), not signed decimals.
2. Map coordinates using `references/coordinate-conventions.md`.
3. Check ImageIO key names in `references/imageio-mapping.md`.
4. Review pitfalls for sign/ref mismatches.

## Guardrails

- GPS EXIF latitude/longitude are always positive; direction is in the `Ref` tag.
- `GPSTimeStamp` is UTC; `GPSDateStamp` is UTC date — do not mix with local time.
- Some apps write signed decimals directly, causing southern/western coordinates to appear in the wrong hemisphere.

## References

- `references/`
  - `README.md` — GPS IFD overview
  - `tag-reference.md` — all 31 GPS tags
  - `coordinate-conventions.md` — encoding rules and examples
  - `imageio-mapping.md` — GPS tags to ImageIO keys
  - `pitfalls.md` — common GPS metadata pitfalls
