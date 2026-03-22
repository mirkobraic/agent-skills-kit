# ICC

ICC color profiles. Color space metadata and management.

## ImageIO surface

Not a dictionary — accessed via top-level keys and CoreGraphics:

- `kCGImagePropertyProfileName` — top-level image property
- `kCGImagePropertyColorModel` — RGB, CMYK, Gray, Lab
- `CGColorSpace.iccData` — raw ICC profile data
- `CGColorSpace(iccData:)` — create color space from ICC data

## Planned content

- ICC profile basics and what they encode
- Common profiles: sRGB, Display P3, Adobe RGB, ProPhoto RGB
- Reading ICC profile from an image via ImageIO
- Embedding / preserving ICC profile during image write
- `kCGImagePropertyDNGCurrentICCProfile` for DNG
- iOS version considerations (color management available from iOS 9+)
