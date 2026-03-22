# TIFF

TIFF IFD structure. Image structure and basic descriptive tags.

## ImageIO dictionary

- `kCGImagePropertyTIFFDictionary` (iOS 4.0) — ~15 keys

## Planned content

- Key tags: Make, Model, Orientation, XResolution, YResolution, ResolutionUnit, DateTime, Software, Artist, Copyright, HostComputer
- Relationship to EXIF: TIFF is the container format; EXIF IFDs (ExifIFD, GPS IFD) are sub-IFDs within the TIFF structure
- How ImageIO exposes TIFF tags separately from EXIF tags
- Orientation tag behavior and interaction with `kCGImagePropertyOrientation`
