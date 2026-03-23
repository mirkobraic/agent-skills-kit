# Common ICC Profiles

This reference covers the ICC profiles most frequently encountered in iOS image
workflows, from the universal sRGB to wide-gamut Display P3 and beyond.

---

## Quick Comparison

| Profile | Gamut (% CIE 1931) | White Point | Gamma / TRC | Bit Depth | Primary Use |
|---------|--------------------|-------------|-------------|-----------|-------------|
| **sRGB** | ~35.9% | D65 | ~2.2 (piece-wise) | 8-bit OK | Web, screens, default |
| **Display P3** | ~45.5% | D65 | ~2.2 (sRGB curve) | 8/10-bit | Apple devices, wide color |
| **Adobe RGB (1998)** | ~52.1% | D65 | 2.2 (pure gamma) | 8/16-bit | Photography, prepress |
| **ProPhoto RGB** | ~90%+ | D50 | 1.8 | 16-bit required | Photo editing, archival |
| **Rec. 709** | ~35.9% | D65 | BT.1886 (2.4 EOTF) | 8/10-bit | HDTV video |
| **Rec. 2020** | ~75.8% | D65 | BT.1886 / PQ / HLG | 10/12-bit | UHDTV, HDR video |
| **DCI-P3** | ~45.5% | ~6300K (green) | 2.6 | 12-bit | Digital cinema projection |

---

## sRGB IEC 61966-2.1

The most widely used color space in the world. Created by HP and Microsoft in
1996, standardized as IEC 61966-2.1 in 1999, and adopted by the W3C as the
default color space for the web.

### Characteristics

| Property | Value |
|----------|-------|
| **Standard** | IEC 61966-2.1:1999 |
| **White point** | D65 (x=0.3127, y=0.3290) |
| **Red primary** | x=0.6400, y=0.3300 |
| **Green primary** | x=0.3000, y=0.6000 |
| **Blue primary** | x=0.1500, y=0.0600 |
| **Transfer function** | Piece-wise: linear below 0.0031308, then `1.055 * L^(1/2.4) - 0.055` |
| **Effective gamma** | ~2.2 (not a pure power function) |
| **CIE 1931 coverage** | ~35.9% |
| **Primaries source** | Same as ITU-R BT.709 (HDTV) |

### sRGB Transfer Function (Exact)

**Encoding (OETF, linear to non-linear):**

```
if L <= 0.0031308:
    V = 12.92 * L
else:
    V = 1.055 * L^(1/2.4) - 0.055
```

**Decoding (EOTF, non-linear to linear):**

```
if V <= 0.04045:
    L = V / 12.92
else:
    L = ((V + 0.055) / 1.055)^2.4
```

The piece-wise function avoids an infinite slope at zero (which a pure gamma
would have) while approximating a gamma of 2.2 across most of the range. Due
to rounding of the parameters, the encode and decode functions have a tiny
discontinuity at the transition (~10^-8), and are not exact inverses.

### When to Use

- **Default for web and screen display.** All browsers assume sRGB when no
  profile is embedded.
- **Default for iOS rendering.** UIKit and SwiftUI render in sRGB unless
  wide color is explicitly used.
- **Sharing images.** `kCGImageDestinationOptimizeColorForSharing` converts
  to sRGB for maximum compatibility.
- **8-bit workflows.** sRGB's relatively small gamut means 8-bit precision
  is sufficient for most content.

### CGColorSpace Constants

```swift
CGColorSpace.sRGB                    // Standard sRGB
CGColorSpace.linearSRGB              // sRGB primaries, linear gamma (1.0)
CGColorSpace.extendedSRGB            // sRGB primaries, values beyond 0-1 allowed
CGColorSpace.extendedLinearSRGB      // Extended + linear
```

### Profile Variants

| Variant | Version | Size | Purpose |
|---------|---------|------|---------|
| `sRGB IEC61966-2.1` | v2 | ~3 KB | Standard profile shipped with most OSes |
| `sRGB2014.icc` | v4 | ~2 KB | ICC v4 reference profile from color.org |
| `sRGBz` | v2 | 491 bytes | Minimal profile for embedding (saucecontrol) |
| `sRGB-elle-V2-srgbtrc.icc` | v2 | ~3 KB | Well-behaved v2 profile (Elle Stone) |

---

## Display P3

Apple's wide-gamut color space for modern displays. Used as the default capture
and display color space on iPhone 7 and later, iPad Pro (2017+), and all Apple
silicon Macs. Display P3 is a variant of DCI-P3 adapted for consumer displays.

### Characteristics

| Property | Value |
|----------|-------|
| **Standard** | Based on SMPTE EG 432-1 (DCI-P3), adapted by Apple |
| **White point** | D65 (x=0.3127, y=0.3290) -- differs from DCI-P3's ~6300K |
| **Red primary** | x=0.6800, y=0.3200 |
| **Green primary** | x=0.2650, y=0.6900 |
| **Blue primary** | x=0.1500, y=0.0600 |
| **Transfer function** | sRGB piece-wise curve (~2.2) |
| **Red dominant wavelength** | 614.9 nm (deeper red than sRGB's ~612 nm) |
| **CIE 1931 coverage** | ~45.5% |
| **Gamut vs sRGB** | ~25% larger by area; significantly wider reds, oranges, greens |

### Display P3 vs DCI-P3

| Aspect | Display P3 | DCI-P3 (theatrical) |
|--------|-----------|---------------------|
| White point | D65 (6500K, neutral) | ~6300K (slightly green) |
| Transfer function | sRGB curve (~2.2) | Pure gamma 2.6 |
| Luminance | Not constrained (160+ cd/m2 SDR) | 48 cd/m2 |
| Use case | Consumer displays | Cinema projection |
| Blue primary | Same as sRGB (0.1500, 0.0600) | Same |

> Display P3 shares its blue primary with sRGB. The gamut extension is
> entirely in the red and green primaries.

### Display P3 vs sRGB

| Aspect | Display P3 | sRGB |
|--------|-----------|------|
| Red primary | x=0.6800, y=0.3200 | x=0.6400, y=0.3300 |
| Green primary | x=0.2650, y=0.6900 | x=0.3000, y=0.6000 |
| Blue primary | x=0.1500, y=0.0600 | x=0.1500, y=0.0600 (same) |
| Transfer function | sRGB curve (same) | sRGB curve |
| CIE area | ~45.5% | ~35.9% |
| Colors sRGB cannot reach | Vivid reds, deep oranges, saturated greens | -- |

### When to Use

- **iPhone/iPad photography.** The camera captures in Display P3 on devices
  with P3 displays (iPhone 7+).
- **Wide color UI.** SwiftUI `Color` and `UIColor(displayP3Red:...)` define
  colors outside sRGB.
- **Asset catalogs.** Xcode marks image assets as sRGB or Display P3.
- **HDR-aware workflows.** Display P3 is the base gamut for Apple's SDR
  rendering on wide-color displays.

### CGColorSpace Constants

```swift
CGColorSpace.displayP3              // Standard Display P3
CGColorSpace.displayP3_HLG          // Display P3 with HLG transfer (HDR)
CGColorSpace.displayP3_PQ           // Display P3 with PQ/ST 2084 transfer (HDR)
CGColorSpace.displayP3_PQ_EOTF      // Display P3 with PQ EOTF (display-referred)
CGColorSpace.extendedDisplayP3      // Extended range (values beyond 0-1)
CGColorSpace.extendedLinearDisplayP3 // Extended + linear
```

> **Important:** When an iPhone captures a photo, the embedded ICC profile name
> is typically `"Display P3"`. If your code assumes sRGB and ignores the embedded
> profile, reds and greens will appear desaturated.

---

## Adobe RGB (1998)

A wider-gamut RGB space designed by Adobe for professional photography and
prepress. It extends significantly beyond sRGB in the cyan-green region, making
it popular for images destined for high-quality print.

### Characteristics

| Property | Value |
|----------|-------|
| **Standard** | Adobe RGB (1998) Color Image Encoding (Adobe, 2005) |
| **White point** | D65 (x=0.3127, y=0.3290) |
| **Red primary** | x=0.6400, y=0.3300 (same as sRGB) |
| **Green primary** | x=0.2100, y=0.7100 |
| **Blue primary** | x=0.1500, y=0.0600 (same as sRGB) |
| **Transfer function** | Pure gamma 2.19921875 (2+51/256, the closest to 2.2 in u8Fixed8 format) |
| **v4 gamma** | 2.19999695 (2+13107/65536, via parametric curve) |
| **CIE 1931 coverage** | ~52.1% |
| **Gamut vs sRGB** | ~45% larger; much wider greens and cyans |

### Adobe RGB Gamma: Why 2.19921875?

The ICC v2 profile format encodes a single-value gamma as an unsigned 8.8
fixed-point number (u8Fixed8Number). The closest representable value to 2.2 is
2 + 51/256 = 2.19921875. This is stored as `0x0233` in the `curv` tag. In v4
profiles using `para` type-0 curves, s15Fixed16Number encoding allows
2 + 13107/65536 = 2.19999695 -- effectively 2.2 to five decimal places.

### When to Use

- **Professional photography** destined for print (CMYK conversion).
- **Archival images** where a wider gamut than sRGB is needed but ProPhoto
  RGB's imaginary colors are undesirable.
- **Interoperability** with Adobe Lightroom/Photoshop workflows.

### CGColorSpace Constant

```swift
CGColorSpace.adobeRGB1998
```

> **iOS note:** While `CGColorSpace.adobeRGB1998` is available on iOS, Apple's
> own capture pipeline never produces Adobe RGB images. You will encounter this
> profile when processing images from DSLR cameras or Adobe software.

---

## ProPhoto RGB (ROMM RGB)

The widest standard RGB gamut, designed by Kodak for photographic workflows.
Encompasses over 90% of surface colors and 100% of Pointer's gamut (all colors
found on real-world reflective surfaces).

### Characteristics

| Property | Value |
|----------|-------|
| **Standard** | ROMM RGB (ISO 22028-2:2013) |
| **White point** | D50 (x=0.3457, y=0.3585) -- note: different from sRGB/P3/Adobe RGB |
| **Red primary** | x=0.7347, y=0.2653 |
| **Green primary** | x=0.1596, y=0.8404 |
| **Blue primary** | x=0.0366, y=0.0001 |
| **Transfer function** | Gamma 1.8 with linear segment: `L' = 16*L` for `L < 1/512`, else `L' = L^(1/1.8)` |
| **CIE 1931 coverage** | ~90%+ |
| **Imaginary colors** | ~13% of encodable values are outside human vision |

### Key Design Decisions

- **D50 white point** aligns with the ICC PCS, meaning no chromatic adaptation
  is needed when connecting ProPhoto RGB to the PCS. This is unique among
  common RGB working spaces (sRGB, Display P3, Adobe RGB all use D65).
- **Imaginary primaries.** The green and blue primaries fall outside the
  spectral locus, meaning some encodable color values represent "colors"
  invisible to humans. This was done intentionally to minimize hue rotations
  during non-linear tone scale operations.
- **Gamma 1.8** provides a more perceptually uniform encoding than 2.2,
  allocating more code values to shadows where the eye is most sensitive.

### When to Use

- **RAW processing and photo editing** where maximum color fidelity is needed.
- **Archival master files** before output-specific conversion.
- **16-bit workflows only.** At 8-bit, the gamut is so large that posterization
  (banding) is visible in gradients. Always use 16-bit per channel or
  floating-point.

### CGColorSpace Constant

There is no dedicated `CGColorSpace` constant for ProPhoto RGB. To use it:

```swift
// Create from ICC data
if let url = Bundle.main.url(forResource: "ProPhotoRGB", withExtension: "icc"),
   let data = try? Data(contentsOf: url) {
    let colorSpace = CGColorSpace(iccData: data as CFData)
}
```

> **Caution:** ProPhoto RGB uses D50 white, while most display profiles use D65.
> Converting between them requires chromatic adaptation, which Apple's ColorSync
> handles automatically when you specify the color spaces.

---

## Rec. 709 (BT.709)

The color space standard for HDTV. Shares the same primaries as sRGB but uses
a different transfer function optimized for broadcast video.

### Characteristics

| Property | Value |
|----------|-------|
| **Standard** | ITU-R BT.709-6 |
| **White point** | D65 |
| **Primaries** | Same as sRGB (R: 0.64/0.33, G: 0.30/0.60, B: 0.15/0.06) |
| **OETF** | BT.709: `V = 4.5 * L` for `L < 0.018`, else `V = 1.099 * L^0.45 - 0.099` |
| **Reference EOTF** | BT.1886 (pure gamma 2.4, with ambient-dependent black level) |
| **CIE 1931 coverage** | ~35.9% (same gamut as sRGB) |

### Rec. 709 vs sRGB

Same primaries, different transfer functions:

| | sRGB | Rec. 709 |
|--|------|----------|
| OETF | Piece-wise (~1/2.2) | BT.709 piece-wise (~1/2.2) |
| Reference EOTF | Piece-wise (~2.2) | BT.1886 (2.4 pure gamma) |
| Linear threshold | 0.0031308 | 0.018 |
| Viewing conditions | Office/desktop (bright surround) | Dim surround (TV viewing) |
| Black level | 0.0 (absolute) | Ambient-dependent (BT.1886) |
| Effective appearance | Slightly brighter shadows | Slightly deeper shadows |

Despite sharing primaries, treating sRGB content as Rec. 709 (or vice versa)
produces visible differences in shadow regions due to the different transfer
functions.

### CGColorSpace Constants

```swift
CGColorSpace.itur_709              // Rec. 709
CGColorSpace.itur_709_HLG          // Rec. 709 with HLG transfer (iOS 14.0+)
CGColorSpace.itur_709_PQ           // Rec. 709 with PQ transfer (iOS 15.0+)
```

---

## Rec. 2020 (BT.2020)

The wide color gamut standard for Ultra High Definition Television (UHDTV).
Covers 75.8% of the CIE 1931 diagram -- more than any other standard RGB
color space in common use.

### Characteristics

| Property | Value |
|----------|-------|
| **Standard** | ITU-R BT.2020-2 |
| **White point** | D65 |
| **Red primary** | x=0.708, y=0.292 (630 nm monochromatic) |
| **Green primary** | x=0.170, y=0.797 (532 nm monochromatic) |
| **Blue primary** | x=0.131, y=0.046 (467 nm monochromatic) |
| **Transfer function** | BT.2020 (10/12-bit), or PQ/HLG for HDR (Rec. 2100) |
| **CIE 1931 coverage** | ~75.8% |
| **Bit depth** | 10-bit or 12-bit required |

### Monochromatic Primaries

Unlike other RGB spaces whose primaries are defined by chromaticity
coordinates alone, Rec. 2020's primaries correspond to specific wavelengths
of monochromatic (single-wavelength) light on the spectral locus. This is why
the gamut is so large -- but it also means no current display technology can
reproduce the full Rec. 2020 gamut.

### HDR Transfer Functions

Rec. 2020 defines the container gamut; for HDR content, Rec. 2100 specifies
two transfer functions used with the same primaries:

| Transfer Function | Standard | Peak Luminance | Key Feature |
|-------------------|----------|----------------|-------------|
| **PQ** (Perceptual Quantizer) | SMPTE ST 2084 | Up to 10,000 cd/m2 | Absolute luminance encoding |
| **HLG** (Hybrid Log-Gamma) | ARIB STD-B67 | Relative (scene-referred) | Backward-compatible with SDR |

PQ maps specific code values to specific luminance levels (absolute). HLG
uses a relative encoding that adapts to the display's peak luminance, making
it backward-compatible with SDR displays.

### When to Use

- **HDR video content** (Dolby Vision, HDR10, HLG).
- **Future-proofing** wide-gamut captures.
- **Note:** No current consumer display covers the full Rec. 2020 gamut.
  Display P3 covers roughly 60% of Rec. 2020 by area (45.5% / 75.8% of CIE 1931 xy).

### CGColorSpace Constants

```swift
CGColorSpace.itur_2020                  // Standard Rec. 2020
CGColorSpace.itur_2020_HLG             // Rec. 2020 + HLG (iOS 14.0+)
CGColorSpace.itur_2020_PQ              // Rec. 2020 + PQ (iOS 14.0+)
CGColorSpace.itur_2020_PQ_EOTF         // Rec. 2020 PQ EOTF (iOS 12.6+)
CGColorSpace.extendedLinearITUR_2020    // Rec. 2020 linear extended (iOS 14.0+)
```

---

## DCI-P3

The digital cinema projection color space defined by the Digital Cinema
Initiatives. Display P3 is derived from DCI-P3 but adapted for consumer
displays.

### Characteristics

| Property | Value |
|----------|-------|
| **Standard** | SMPTE EG 432-1:2010 |
| **White point** | ~6300K (x=0.314, y=0.351) -- greenish, not D65 |
| **Primaries** | Same as Display P3 |
| **Transfer function** | Pure gamma 2.6 |
| **Luminance** | 48 cd/m2 reference |
| **CIE 1931 coverage** | ~45.5% (same area as Display P3, same primaries) |

### CGColorSpace Constant

```swift
CGColorSpace.dcip3   // DCI-P3 (cinema, 2.6 gamma, ~6300K white) — iOS 11.0+
```

> **When to use DCI-P3 on iOS:** Rarely. DCI-P3 is for theatrical projection.
> For consumer content on Apple devices, always use Display P3 (D65 white,
> sRGB curve). The `CGColorSpace.dcip3` constant exists for cinema workflows.

---

## Generic System Profiles

Apple provides several generic profiles for device-independent workflows:

| Profile | CGColorSpace Constant | Components | iOS | Notes |
|---------|-----------------------|------------|-----|-------|
| Generic RGB Linear | `.genericRGBLinear` | 3 (RGB) | 9.0+ | Linear gamma, generic primaries |
| Generic Gray 2.2 | `.genericGrayGamma2_2` | 1 | 9.0+ | Gamma 2.2 grayscale |
| Extended Gray | `.extendedGray` | 1 | 10.0+ | Extended range gray |
| Linear Gray | `.linearGray` | 1 | 10.0+ | Linear grayscale |
| Extended Linear Gray | `.extendedLinearGray` | 1 | 10.0+ | Linear + extended gray |
| Generic CMYK | `.genericCMYK` | 4 | 9.0+ | System default CMYK |
| Generic XYZ | `.genericXYZ` | 3 | 9.0+ | CIE XYZ D50 |
| Generic Lab | `.genericLab` | 3 | 9.0+ | CIE L*a*b* D50 |
| ACEScg | `.acescgLinear` | 3 | 12.0+ | Academy Color Encoding (VFX, linear) |

### ACEScg

The Academy Color Encoding System (ACES) defines `ACEScg` as a linear,
wide-gamut color space for visual effects compositing. It uses AP1 primaries
(wider than Display P3, narrower than ProPhoto RGB) and a linear transfer
function, making it ideal for physically-based rendering and compositing.

---

## Gamut Comparison

Relative gamut sizes (CIE 1931 xy chromaticity area):

```
ProPhoto RGB  ████████████████████████████████████████████████  ~90%+
Rec. 2020     ██████████████████████████████████████            ~75.8%
Adobe RGB     ██████████████████████████                        ~52.1%
Display P3    ██████████████████████████                        ~45.5% (*)
DCI-P3        ██████████████████████████                        ~45.5%
sRGB          ██████████████████                                ~35.9%
Rec. 709      ██████████████████                                ~35.9%
```

(*) Display P3 and Adobe RGB overlap significantly but in different regions.
Display P3 extends further into reds/oranges; Adobe RGB extends further into
greens/cyans.

### Gamut Coverage Relationships

| Source Space | Containing Space | Relationship |
|--------------|-----------------|--------------|
| sRGB | Display P3 | sRGB is a proper subset; ~25% of P3 volume is beyond sRGB |
| sRGB | Adobe RGB | sRGB covers ~69% of Adobe RGB area |
| Display P3 | Rec. 2020 | P3 covers ~60% of Rec. 2020 area; 100% of P3 is contained within Rec. 2020 |
| Display P3 | Adobe RGB | Significant overlap in different regions; neither is a subset |
| Adobe RGB | ProPhoto RGB | Adobe RGB covers ~58% of ProPhoto area |
| Rec. 709 | sRGB | Same gamut (identical primaries); different TRC only |
| DCI-P3 | Display P3 | Same gamut (identical primaries); different white point and TRC |

### Overlap Regions

Understanding where gamuts differ is important for avoiding color clipping:

| Gamut Pair | Extended Region | Colors at Risk in Conversion |
|-----------|-----------------|------------------------------|
| P3 vs sRGB | P3 extends in reds, oranges, greens | Vivid sunsets, autumn foliage, neon signs |
| Adobe RGB vs sRGB | Adobe extends in cyans, greens | Tropical ocean, emerald foliage, turquoise |
| P3 vs Adobe RGB | P3 wider in reds; Adobe wider in cyans | Red-heavy photos favor P3; cyan-heavy favor Adobe |
| Rec. 2020 vs P3 | 2020 extends in all directions, esp. greens | Pure spectral greens and deep blues |

---

## Choosing the Right Profile

| Scenario | Recommended Profile | Why |
|----------|-------------------|-----|
| Web/social media sharing | sRGB | Universal browser/app support |
| iOS app UI assets | sRGB or Display P3 | P3 on capable devices; sRGB fallback |
| iPhone camera capture | Display P3 (automatic) | Native gamut of iPhone displays |
| Professional photo editing | ProPhoto RGB (16-bit) | Maximum gamut preservation |
| Print production | Adobe RGB or profile-specific | Wide gamut, good CMYK overlap |
| HDTV video | Rec. 709 | Broadcast standard |
| HDR/UHD video | Rec. 2020 + PQ or HLG | Standards-compliant HDR |
| VFX/compositing | ACEScg (linear) | Scene-referred, wide gamut |
| Archival master | ProPhoto RGB (16-bit) | Future-proof, maximum fidelity |
| Digital cinema mastering | DCI-P3 | Industry standard for theatrical projection |

---

## Cross-References

- [Profile Basics](profile-basics.md) -- ICC profile structure, header, tags, rendering intents
- [Embedding](embedding.md) -- How these profiles are stored in image files
- [ImageIO Integration](imageio-integration.md) -- Reading profile names, CGColorSpace APIs
- [Pitfalls](pitfalls.md) -- Gamut mismatch, silent conversion, CMYK limitations
