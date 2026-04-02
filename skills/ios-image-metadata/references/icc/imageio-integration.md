# ICC Profile Integration with Apple ImageIO

How to read, write, and manage ICC color profiles using Apple's ImageIO,
CoreGraphics, and related frameworks on iOS and macOS.

---

## Reading ICC Profile Information

### Top-Level Image Properties

When you call `CGImageSourceCopyPropertiesAtIndex`, three top-level keys relate
to color:

| Key | Type | iOS | Description |
|-----|------|-----|-------------|
| `kCGImagePropertyProfileName` | `CFString` | 4.0+ | Human-readable ICC profile name (e.g. `"sRGB IEC61966-2.1"`, `"Display P3"`) |
| `kCGImagePropertyColorModel` | `CFString` | 4.0+ | Color model: `"RGB"`, `"CMYK"`, `"Gray"`, `"Lab"` |
| `kCGImagePropertyNamedColorSpace` | `CFNumber` | 11.0+ | Numeric enum identifying well-known color spaces |

#### Reading the Profile Name

```swift
import ImageIO

func profileName(from url: URL) -> String? {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil)
              as? [CFString: Any] else {
        return nil
    }
    return properties[kCGImagePropertyProfileName] as? String
}

// Examples of returned values:
// "sRGB IEC61966-2.1"
// "Display P3"
// "Adobe RGB (1998)"
// "Generic RGB Profile"
// "Color LCD"  (device-specific display profile)
```

#### Color Model

```swift
let colorModel = properties[kCGImagePropertyColorModel] as? String
// "RGB", "CMYK", "Gray", or "Lab"
```

The color model constants are:

| Constant | String Value |
|----------|-------------|
| `kCGImagePropertyColorModelRGB` | `"RGB"` |
| `kCGImagePropertyColorModelGray` | `"Gray"` |
| `kCGImagePropertyColorModelCMYK` | `"CMYK"` |
| `kCGImagePropertyColorModelLab` | `"Lab"` |

#### Named Color Space (iOS 11+)

`kCGImagePropertyNamedColorSpace` returns a numeric value identifying well-known
Apple color spaces. This is more reliable than string-matching on
`kCGImagePropertyProfileName` because profile name strings can vary between
ICC profile vendors (e.g. `"sRGB IEC61966-2.1"` vs `"sRGB"` vs `"IEC 61966-2.1
Default RGB colour space - sRGB"`).

```swift
let namedSpace = properties[kCGImagePropertyNamedColorSpace] as? Int
```

The value corresponds to `CGColorSpace` name constants internally. When the
profile does not match a known Apple color space, this key may be absent from
the properties dictionary.

---

### Reading the CGColorSpace from a CGImage

For deeper color space inspection, work with `CGColorSpace` directly:

```swift
import CoreGraphics

func inspectColorSpace(from url: URL) {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil),
          let colorSpace = cgImage.colorSpace else {
        return
    }

    // Profile name (as CFString constant, e.g. kCGColorSpaceSRGB)
    let name = colorSpace.name  // CFString?

    // Color model
    let model = colorSpace.model
    // .rgb, .cmyk, .monochrome, .lab, .indexed, .unknown, .pattern, .deviceN

    // Number of components
    let components = colorSpace.numberOfComponents  // 3 for RGB, 4 for CMYK

    // Is wide gamut?
    if #available(iOS 12.0, *) {
        let isWide = colorSpace.isWideGamutRGB
        // true for Display P3, Adobe RGB, Rec. 2020, ProPhoto RGB, etc.
        // Defined as covering > 85% of NTSC gamut
    }

    // Is HDR? (iOS 17+)
    if #available(iOS 17.0, *) {
        let hdr = colorSpace.isHDR
        // true for PQ and HLG transfer function color spaces
    }

    // Raw ICC profile data
    let iccData = colorSpace.copyICCData()  // CFData? -- the raw ICC profile bytes

    // Get linearized variant (iOS 17+)
    if #available(iOS 17.0, *) {
        let linearSpace = colorSpace.linearized
        // e.g., displayP3 -> extendedLinearDisplayP3
    }

    // Check if it matches a named color space
    if let spaceName = colorSpace.name as String? {
        switch spaceName {
        case CGColorSpace.sRGB.rawValue:
            print("sRGB")
        case CGColorSpace.displayP3.rawValue:
            print("Display P3")
        case CGColorSpace.adobeRGB1998.rawValue:
            print("Adobe RGB (1998)")
        default:
            print("Other: \(spaceName)")
        }
    }
}
```

### Key CGColorSpace Properties

| Property / Method | iOS | Description |
|-------------------|-----|-------------|
| `.name` | 10.0+ | CFString name if this is a named color space; nil for custom profiles |
| `.model` | 2.0+ | `CGColorSpaceModel` enum (.rgb, .cmyk, .monochrome, .lab, etc.) |
| `.numberOfComponents` | 2.0+ | Number of color components (3 for RGB, 4 for CMYK, 1 for gray) |
| `.isWideGamutRGB` | 12.0+ | `true` if gamut exceeds ~85% of NTSC gamut (covers sRGB entirely) |
| `.copyICCData()` | 10.0+ | Raw ICC profile binary data as `CFData` |
| `.supportsOutput` | 13.0+ | Whether the color space can be used for rendering output |
| `.isHDR` | 17.0+ | `true` if the color space uses an HDR transfer function (PQ, HLG) |
| `.linearized` | 17.0+ | Returns the linearized variant of this color space |
| `.iccData` | 10.0+ | Property alias for `copyICCData()` (Obj-C: `CGColorSpaceCopyICCData`) |

#### CGColorSpaceModel Values

```swift
enum CGColorSpaceModel: Int32 {
    case unknown     = -1
    case monochrome  = 0   // 1 component (grayscale)
    case rgb         = 1   // 3 components
    case cmyk        = 2   // 4 components
    case lab         = 3   // 3 components (L*a*b*)
    case deviceN     = 4   // N components
    case indexed     = 5   // Palette-based
    case pattern     = 6   // Pattern color space
    case xyz         = 7   // CIE XYZ (iOS 17+)
}
```

---

## Named CGColorSpace Constants

Complete reference of Apple's named color spaces, grouped by category:

### Standard RGB

| Constant | Profile Name | iOS | Notes |
|----------|-------------|-----|-------|
| `.sRGB` | sRGB IEC61966-2.1 | 9.0+ | The universal default |
| `.linearSRGB` | sRGB IEC61966-2.1 (linear) | 10.0+ | sRGB primaries, gamma 1.0 |
| `.extendedSRGB` | Extended sRGB | 10.0+ | Values beyond 0-1 represent colors outside sRGB gamut |
| `.extendedLinearSRGB` | Extended Linear sRGB | 10.0+ | Linear + extended range |

### Display P3

| Constant | iOS | Notes |
|----------|-----|-------|
| `.displayP3` | 9.3+ | Apple's wide-gamut standard; sRGB TRC |
| `.displayP3_HLG` | 11.0+ | Display P3 + HLG transfer for HDR |
| `.displayP3_PQ` | 15.0+ | Display P3 + PQ/ST 2084 transfer for HDR |
| `.displayP3_PQ_EOTF` | 12.6+ | Display P3 + PQ EOTF (display-referred HDR) |
| `.extendedDisplayP3` | 12.0+ | Extended range (values beyond 0-1) |
| `.extendedLinearDisplayP3` | 10.0+ | Linear + extended range |

#### displayP3_PQ vs displayP3_PQ_EOTF

Both use Display P3 primaries with the PQ (Perceptual Quantizer, SMPTE ST 2084)
transfer function, but they differ in reference level:

- **`.displayP3_PQ`** (iOS 15+): Scene-referred. PQ values are used directly.
- **`.displayP3_PQ_EOTF`** (iOS 12.6+): Display-referred. The PQ EOTF is
  applied, mapping code values to absolute luminance. Reference white at 100
  nits maps to 1.0 in EDR.

For most HDR rendering on iOS, `.displayP3_HLG` is preferred because the
iPhone camera captures in P3, avoiding an extra color space transform.

### Adobe / Professional

| Constant | iOS | Notes |
|----------|-----|-------|
| `.adobeRGB1998` | 9.0+ | Adobe RGB (1998) for photography/print |
| `.genericRGBLinear` | 9.0+ | Generic linear RGB (not device-specific) |

### Broadcast / Cinema

| Constant | iOS | Notes |
|----------|-----|-------|
| `.itur_709` | 11.0+ | Rec. 709 (HDTV) |
| `.itur_709_HLG` | 14.0+ | Rec. 709 + HLG |
| `.itur_709_PQ` | 15.0+ | Rec. 709 + PQ |
| `.itur_2020` | 11.0+ | Rec. 2020 (UHDTV) |
| `.itur_2020_HLG` | 14.0+ | Rec. 2020 + HLG |
| `.itur_2020_PQ` | 14.0+ | Rec. 2020 + PQ |
| `.itur_2020_PQ_EOTF` | 12.6+ | Rec. 2020 + PQ EOTF (display-referred) |
| `.extendedLinearITUR_2020` | 14.0+ | Rec. 2020 linear + extended |
| `.dcip3` | 11.0+ | DCI-P3 (cinema, 2.6 gamma, ~6300K white) |

### VFX / Scene-Referred

| Constant | iOS | Notes |
|----------|-----|-------|
| `.acescgLinear` | 12.0+ | ACEScg (Academy Color Encoding, AP1 primaries, linear) |

### Grayscale

| Constant | iOS | Notes |
|----------|-----|-------|
| `.genericGrayGamma2_2` | 9.0+ | Gamma 2.2 grayscale |
| `.extendedGray` | 10.0+ | Extended range grayscale |
| `.linearGray` | 10.0+ | Linear grayscale |
| `.extendedLinearGray` | 10.0+ | Linear + extended gray |

### Device-Independent

| Constant | iOS | Notes |
|----------|-----|-------|
| `.genericXYZ` | 9.0+ | CIE XYZ (D50) |
| `.genericLab` | 9.0+ | CIE L*a*b* (D50) |
| `.genericCMYK` | 9.0+ | System default CMYK profile |

---

## Writing ICC Profiles

### Method 1: Preserve the Source Color Space

The simplest way to ensure the correct ICC profile is embedded. When you add
a `CGImage` to a `CGImageDestination`, the image's `CGColorSpace` determines
the embedded profile:

```swift
import ImageIO
import CoreGraphics
import UniformTypeIdentifiers

func saveImagePreservingProfile(cgImage: CGImage, to url: URL) {
    guard let destination = CGImageDestinationCreateWithURL(
        url as CFURL,
        UTType.jpeg.identifier as CFString,
        1, nil
    ) else { return }

    // The image's CGColorSpace determines the embedded ICC profile.
    // If cgImage is Display P3, the output JPEG embeds a Display P3 profile.
    CGImageDestinationAddImage(destination, cgImage, nil)
    CGImageDestinationFinalize(destination)
}
```

### Method 2: Converting Color Space Before Writing

To explicitly convert an image to a specific color space:

```swift
func convertToSRGB(_ cgImage: CGImage) -> CGImage? {
    guard let srgb = CGColorSpace(name: CGColorSpace.sRGB) else { return nil }

    // Create a bitmap context in the target color space
    let width = cgImage.width
    let height = cgImage.height
    guard let context = CGContext(
        data: nil,
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: 0,
        space: srgb,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    ) else { return nil }

    // Drawing performs the color conversion via ColorSync
    context.draw(cgImage, in: CGRect(x: 0, y: 0, width: width, height: height))
    return context.makeImage()
    // The returned CGImage has .colorSpace == sRGB
}
```

### Method 3: `kCGImageDestinationOptimizeColorForSharing`

Apple's one-step solution for producing universally compatible images. When
set to `true`, ImageIO converts the image to sRGB (or the closest compatible
color space) and embeds the appropriate profile:

```swift
func saveForSharing(cgImage: CGImage, to url: URL) {
    guard let destination = CGImageDestinationCreateWithURL(
        url as CFURL,
        UTType.jpeg.identifier as CFString,
        1, nil
    ) else { return }

    let options: [CFString: Any] = [
        kCGImageDestinationOptimizeColorForSharing: true
    ]

    CGImageDestinationAddImage(destination, cgImage, options as CFDictionary)
    CGImageDestinationFinalize(destination)
}
```

**What this option does:**

1. Checks the source image's color space.
2. If it is NOT sRGB, converts the pixel data to sRGB using relative
   colorimetric rendering.
3. Embeds the sRGB ICC profile in the output.
4. If the image IS already sRGB, it is written unchanged.

**Available since:** iOS 9.3 / macOS 10.12

**Additional behavior:** This option also handles images with unusual or
unknown color spaces (such as uRGB, eciRGB v2, or device-specific profiles)
that might cause issues with Core Image or other processing pipelines.

> **Warning:** This conversion is lossy for wide-gamut images. A Display P3
> image with vivid reds and greens will lose those out-of-sRGB colors
> permanently. Use this option for sharing, not for archival.

### Method 4: Creating CGColorSpace from ICC Data

To embed a custom ICC profile not available as a named constant:

```swift
func createColorSpace(fromProfileAt url: URL) -> CGColorSpace? {
    guard let data = try? Data(contentsOf: url) else { return nil }
    return CGColorSpace(iccData: data as CFData)
}

// Use the custom color space when creating images or contexts
let customSpace = createColorSpace(fromProfileAt: profileURL)

// Create an image with the custom color space
if let provider = CGDataProvider(data: pixelData as CFData) {
    let image = CGImage(
        width: width, height: height,
        bitsPerComponent: 8, bitsPerPixel: 24,
        bytesPerRow: width * 3,
        space: customSpace!,
        bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.none.rawValue),
        provider: provider,
        decode: nil, shouldInterpolate: true,
        intent: .defaultIntent
    )
}
```

### Method 5: CGColorConversionInfo for Explicit Control

For fine-grained control over color conversion, including rendering intent:

```swift
import CoreGraphics

func convertWithIntent(
    _ cgImage: CGImage,
    to destSpace: CGColorSpace,
    intent: CGColorRenderingIntent = .defaultIntent
) -> CGImage? {
    let width = cgImage.width
    let height = cgImage.height

    guard let context = CGContext(
        data: nil,
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: 0,
        space: destSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    ) else { return nil }

    context.setRenderingIntent(intent)
    context.draw(cgImage, in: CGRect(x: 0, y: 0, width: width, height: height))
    return context.makeImage()
}

// Example: convert with perceptual intent for photos
let p3Space = CGColorSpace(name: CGColorSpace.displayP3)!
let srgbSpace = CGColorSpace(name: CGColorSpace.sRGB)!
let result = convertWithIntent(p3Image, to: srgbSpace, intent: .perceptual)
```

---

## Preserving ICC Profile Through Read/Write

The recommended pattern for lossless metadata preservation (including ICC
profile) through a read/write cycle:

### Best: CGImageDestinationCopyImageSource (Lossless)

For JPEG, PNG, TIFF, and PSD, this copies the image data and all metadata
without re-encoding:

```swift
func updateMetadataOnly(sourceURL: URL, destURL: URL, newMetadata: CFDictionary) -> Bool {
    guard let source = CGImageSourceCreateWithURL(sourceURL as CFURL, nil),
          let uti = CGImageSourceGetType(source),
          let destination = CGImageDestinationCreateWithURL(
              destURL as CFURL, uti, 0, nil
          ) else {
        return false
    }

    var error: Unmanaged<CFError>?
    let success = CGImageDestinationCopyImageSource(
        destination, source, newMetadata, &error
    )
    return success
}
```

This preserves the ICC profile byte-for-byte because the image data is not
re-decoded or re-encoded.

> **Format limitation:** `CGImageDestinationCopyImageSource` only supports
> JPEG, PNG, TIFF, and PSD. HEIF/HEIC requires re-encoding, which means the
> ICC profile is re-resolved from the CGColorSpace rather than byte-preserved.

### Good: Copy Properties Explicitly

When re-encoding is necessary (format conversion, resizing):

```swift
func reencodeWithProfile(source: CGImageSource, to url: URL, asType: CFString) {
    guard let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil),
          let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil),
          let destination = CGImageDestinationCreateWithURL(
              url as CFURL, asType, 1, nil
          ) else { return }

    // Pass the original properties (includes profile info) as image properties
    CGImageDestinationAddImage(destination, cgImage, properties)
    CGImageDestinationFinalize(destination)
}
```

The `cgImage` carries its `CGColorSpace`, and `properties` carries the
`kCGImagePropertyProfileName`. Together they ensure the profile is embedded
in the output.

### Avoid: UIImage Round-Trips

```swift
// DON'T do this if you need to preserve the ICC profile:
let uiImage = UIImage(contentsOfFile: path)
let jpegData = uiImage?.jpegData(compressionQuality: 0.9)
// jpegData will have an sRGB profile, even if the original was Display P3!
```

`UIImage.jpegData(compressionQuality:)` and `UIImage.pngData()` do NOT
preserve the original ICC profile. They use the UIImage's internal
representation, which is often converted to sRGB during UIImage creation.
Always use `CGImageDestination` for profile-preserving workflows.

---

## EXIF ColorSpace vs ICC Profile

The EXIF tag `ColorSpace` (`kCGImagePropertyExifColorSpace`) and the ICC
profile are two independent mechanisms for signaling color space:

| Mechanism | What It Says | Granularity |
|-----------|-------------|-------------|
| EXIF `ColorSpace` | 1 = sRGB, 65535 = Uncalibrated | Two meaningful values only |
| ICC profile | Full color space characterization | Arbitrary profiles |

**How they interact:**

- If both are present and agree (EXIF says sRGB, ICC profile is sRGB), no
  conflict.
- If the ICC profile is Display P3 but EXIF says sRGB (1), the ICC profile
  takes precedence in color-managed renderers. However, non-color-managed
  software may read the EXIF tag and assume sRGB.
- If EXIF says Uncalibrated (65535), the renderer should rely entirely on the
  ICC profile.
- **iPhone behavior:** iPhones write EXIF ColorSpace = 65535 (Uncalibrated)
  when capturing in Display P3 and embed the Display P3 ICC profile (or use
  nclx CICP in HEIC). This is correct behavior.

**Ensuring consistency when writing:**

```swift
var exifDict = (properties[kCGImagePropertyExifDictionary] as? [CFString: Any]) ?? [:]

if let colorSpace = cgImage.colorSpace, colorSpace.name == CGColorSpace.sRGB {
    exifDict[kCGImagePropertyExifColorSpace] = 1  // sRGB
} else {
    exifDict[kCGImagePropertyExifColorSpace] = 65535  // Uncalibrated
}
```

---

## DNG-Specific ICC Properties

| ImageIO Key | Tag | Description |
|-------------|-----|-------------|
| `kCGImagePropertyDNGAsShotICCProfile` | 50831 | ICC profile for as-shot rendering |
| `kCGImagePropertyDNGCurrentICCProfile` | 50833 | ICC profile for current DNG processing parameters |
| `kCGImagePropertyDNGCurrentPreProfileMatrix` | 50834 | 3x3 matrix to apply before the current ICC profile |

These are specific to DNG files and represent ICC profiles that correspond
to specific DNG rendering states (as-shot vs current processing parameters),
as opposed to the base ICC profile embedded in TIFF tag 34675.

---

## Detecting Wide Color and HDR

### Comprehensive Color Space Detection

```swift
func describeColorSpace(of url: URL) -> String {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let cgImage = CGImageSourceCreateImageAtIndex(source, 0, nil),
          let colorSpace = cgImage.colorSpace else {
        return "Unknown"
    }

    var description = ""

    // Profile name
    if let name = colorSpace.name as String? {
        description += "Profile: \(name)\n"
    }

    // Color model
    switch colorSpace.model {
    case .rgb: description += "Model: RGB (\(colorSpace.numberOfComponents) components)\n"
    case .cmyk: description += "Model: CMYK (\(colorSpace.numberOfComponents) components)\n"
    case .monochrome: description += "Model: Grayscale\n"
    case .lab: description += "Model: L*a*b*\n"
    default: description += "Model: \(colorSpace.model)\n"
    }

    // Wide gamut
    if #available(iOS 12.0, *) {
        description += "Wide gamut: \(colorSpace.isWideGamutRGB)\n"
    }

    // HDR
    if #available(iOS 17.0, *) {
        description += "HDR: \(colorSpace.isHDR)\n"
    }

    // Output support
    if #available(iOS 13.0, *) {
        description += "Supports output: \(colorSpace.supportsOutput)\n"
    }

    return description
}
```

---

## Color Management Pipeline

How iOS processes color through the ImageIO pipeline:

```
Image File (JPEG/HEIF/PNG/...)
    |
    +-- ICC Profile embedded (or CICP/nclx signaling)
    |
    v
CGImageSource reads file
    |
    +-- Resolves ICC profile / CICP -> CGColorSpace
    +-- kCGImagePropertyProfileName = "Display P3"
    +-- kCGImagePropertyColorModel = "RGB"
    +-- kCGImagePropertyNamedColorSpace = <numeric enum>
    |
    v
CGImage has .colorSpace property
    |
    +-- CGColorSpace.displayP3
    +-- .isWideGamutRGB = true
    +-- .isHDR = false (SDR profile)
    +-- .copyICCData() -> raw ICC bytes
    |
    v
Drawing into CGContext or UIView
    |
    +-- If context color space != image color space:
    |     ColorSync automatically converts
    |     (e.g., Display P3 -> sRGB for non-wide-color display)
    |     Default intent: Relative Colorimetric
    |
    v
CGImageDestination writes file
    |
    +-- Embeds ICC profile from CGImage's CGColorSpace
    +-- OR converts to sRGB if kCGImageDestinationOptimizeColorForSharing = true
    +-- HEIF: may write nclx CICP instead of full ICC profile
    |
    v
Output File (with embedded ICC profile or CICP signaling)
```

### Automatic Color Conversion in CoreGraphics

CoreGraphics (Quartz) automatically performs color space conversion when the
source and destination color spaces differ. This happens transparently:

```swift
// sRGB context
let srgbSpace = CGColorSpace(name: CGColorSpace.sRGB)!
let ctx = CGContext(data: nil, width: 100, height: 100,
    bitsPerComponent: 8, bytesPerRow: 0,
    space: srgbSpace,
    bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!

// Draw a Display P3 image into the sRGB context
// -> ColorSync automatically converts P3 -> sRGB
ctx.draw(p3Image, in: CGRect(x: 0, y: 0, width: 100, height: 100))

// Draw a CMYK image into the sRGB context
// -> ColorSync converts CMYK -> sRGB using the CMYK image's ICC profile
ctx.draw(cmykImage, in: CGRect(x: 0, y: 0, width: 100, height: 100))
```

No explicit conversion code is needed -- CoreGraphics reads each image's
`CGColorSpace` and invokes ColorSync for the transform.

---

## Cross-References

- [Profile Basics](profile-basics.md) -- ICC binary structure, header, tags
- [Common Profiles](common-profiles.md) -- sRGB, Display P3, Adobe RGB characteristics
- [Embedding](embedding.md) -- Per-format ICC embedding mechanisms
- [Pitfalls](pitfalls.md) -- Color space mismatch, UIImage loss, CMYK issues
- [`imageio/property-keys.md`](../imageio/property-keys.md) -- All `kCGImageProperty*` constants
- [`imageio/cgimagesource.md`](../imageio/cgimagesource.md) -- CGImageSource reading functions
- [`imageio/cgimagedestination.md`](../imageio/cgimagedestination.md) -- CGImageDestination writing functions
- [`imageio/pitfalls.md`](../imageio/pitfalls.md) -- UIImage metadata loss, orientation issues
