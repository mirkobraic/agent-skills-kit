# GPS

GPS IFD. Location and positioning metadata.

## ImageIO dictionary

- `kCGImagePropertyGPSDictionary` (iOS 4.0) — ~30 keys

## Planned content

- Coordinates: latitude, longitude, altitude (with reference indicators N/S, E/W, above/below sea level)
- Destination: dest latitude, dest longitude, dest bearing, dest distance
- Image direction and reference
- Measurement details: status, satellites, measure mode, DOP, speed, track
- Timestamps: GPSTimeStamp (UTC), GPSDateStamp
- Map datum and processing method
- Positioning error (`kCGImagePropertyGPSHPositioningError`)
- Relationship to EXIF: GPS IFD is a sub-IFD within the EXIF structure, but ImageIO exposes it as a separate dictionary
