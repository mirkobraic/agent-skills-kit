# DNG and RAW Formats Reference

DNG (Digital Negative) is Adobe's open RAW image format specification, built
on the TIFF/EP (ISO 12234-2) structure. It is the only RAW format that ImageIO
can both read and write. All other camera-specific RAW formats (CR2, CR3, NEF,
ARW, RAF, etc.) are read-only in ImageIO.

DNG supports EXIF, XMP, ICC profiles, and GPS data. It is the foundation for
Apple ProRAW and is the preferred archival format for RAW photography.

---

## DNG Specification Overview

DNG is an extension of TIFF/EP, using the same IFD (Image File Directory)
structure with additional DNG-specific tags. The format is maintained by Adobe
and published as a freely available specification.

### Version History

| Version    | Date    | Key Additions                                          |
|------------|---------|--------------------------------------------------------|
| 1.0.0.0    | 2004-09 | Initial specification; basic TIFF/EP extension         |
| 1.1.0.0    | 2005-02 | Minor additions and clarifications                     |
| 1.2.0.0    | 2008-04 | **Camera profiles** (dual-illuminant calibration, profile embedding, `ProfileHueSatMapData`) |
| 1.3.0.0    | 2009-06 | **Opcodes** (13 opcodes for lens corrections, warp, gain map), multiple embedded profiles |
| 1.4.0.0    | 2012-06 | **Floating-point** image data (16/24/32-bit), transparent pixels, proxy DNG files |
| 1.5.0.0    | 2019-05 | **Depth maps**, enhanced (processed) images alongside raw data |
| 1.6.0.0    | 2021-12 | **BigTIFF** (64-bit offsets), semantic masks, **triple-illuminant** calibration (`CalibrationIlluminant3`, `ColorMatrix3`, `ForwardMatrix3`), `IlluminantData` tags |
| 1.7.0.0    | 2023-06 | **JPEG XL compression** (`NewSubFileType` with JXL), 14th opcode, additional compression options |
| 1.7.1.0    | 2023-09 | Minor clarifications and compression parameter refinements |

### File Structure

```
TIFF Header (8 bytes)
  Byte order: II (little-endian) or MM (big-endian)
  Magic number: 42 (standard TIFF) or 43 (BigTIFF, DNG 1.6+)
  IFD0 offset (4 bytes for TIFF, 8 bytes for BigTIFF)

IFD0 (Main Image Directory)
  TIFF tags (Make, Model, Orientation, DateTime, Software, etc.)
  EXIF sub-IFD pointer (tag 34665)
  GPS sub-IFD pointer (tag 34853)
  DNG-specific tags (DNGVersion, UniqueCameraModel, ColorMatrix, etc.)
  SubIFDs pointer (tag 330) -- raw data, reduced-resolution images
  XMP tag (tag 700) -- embedded XMP packet
  ICC profile tag (tag 34675) -- embedded ICC profile

ExifIFD
  Camera settings, exposure, timestamps, lens info, MakerNote

GPS IFD
  Location data (latitude, longitude, altitude, etc.)

SubIFD (RAW image data)
  CFA pattern, active area, image dimensions
  Strip/tile offsets and byte counts
  Compression tag (1=uncompressed, 7=JPEG, 8=deflate, 34892=lossy JPEG, 52546=JXL)

[Additional IFDs for thumbnails, previews, enhanced images]
```

---

## DNG-Specific Tags

These tags are unique to the DNG specification and are accessed via
`kCGImagePropertyDNGDictionary` in ImageIO.

### Version and Identification

| Tag Name                    | Tag ID  | Type    | Purpose                              |
|-----------------------------|---------|---------|--------------------------------------|
| DNGVersion                  | 50706   | BYTE[4] | DNG version (e.g. `[1,6,0,0]`)      |
| DNGBackwardVersion          | 50707   | BYTE[4] | Minimum reader version required      |
| UniqueCameraModel           | 50708   | ASCII   | Non-localized camera model ID        |
| LocalizedCameraModel        | 50709   | ASCII/UTF-8 | Localized camera model name      |
| CameraSerialNumber          | 50735   | ASCII   | Camera serial number                 |
| OriginalRawFileName         | 50827   | ASCII   | Original RAW filename before conversion |
| OriginalRawFileData         | 50828   | UNDEFINED | Original RAW file (embedded)       |
| OriginalRawFileDigest       | 50973   | BYTE[16] | MD5 of original RAW file            |

`UniqueCameraModel` is the canonical identifier for per-camera profile
lookups. It must include the manufacturer name (e.g. `"Canon EOS R5"`) to
avoid collisions across vendors.

### White Balance and Color Calibration

| Tag Name                    | Tag ID  | Type        | Purpose                           |
|-----------------------------|---------|-------------|-----------------------------------|
| AsShotNeutral               | 50728   | RATIONAL[]  | As-shot white balance (per-channel neutral) |
| AsShotWhiteXY               | 50729   | RATIONAL[2] | As-shot white point (CIE xy)     |
| AnalogBalance               | 50727   | RATIONAL[]  | Per-channel analog balance        |
| BaselineExposure            | 50730   | SRATIONAL   | Exposure compensation (EV)        |
| BaselineNoise               | 50731   | RATIONAL    | Relative noise level              |
| BaselineSharpness           | 50732   | RATIONAL    | Relative sharpness                |
| LinearResponseLimit         | 50734   | RATIONAL    | Max useful sensor value (fraction of saturated) |

### Color Matrices (Dual/Triple Illuminant)

DNG uses calibration illuminants to define the camera's color response. For
each illuminant, a set of matrices maps between camera-native color space
and CIE XYZ.

| Tag Name                    | Tag ID  | Type        | Version | Purpose                     |
|-----------------------------|---------|-------------|---------|-----------------------------|
| CalibrationIlluminant1      | 50778   | SHORT       | 1.0     | Light source for 1st calibration |
| CalibrationIlluminant2      | 50779   | SHORT       | 1.0     | Light source for 2nd calibration |
| CalibrationIlluminant3      | 51550   | SHORT       | 1.6     | Light source for 3rd calibration |
| ColorMatrix1                | 50721   | SRATIONAL[] | 1.0     | XYZ-to-camera, illuminant 1 |
| ColorMatrix2                | 50722   | SRATIONAL[] | 1.0     | XYZ-to-camera, illuminant 2 |
| ColorMatrix3                | 51551   | SRATIONAL[] | 1.6     | XYZ-to-camera, illuminant 3 |
| ForwardMatrix1              | 50964   | SRATIONAL[] | 1.2     | Camera-to-XYZ, illuminant 1 |
| ForwardMatrix2              | 50965   | SRATIONAL[] | 1.2     | Camera-to-XYZ, illuminant 2 |
| ForwardMatrix3              | 51554   | SRATIONAL[] | 1.6     | Camera-to-XYZ, illuminant 3 |
| CameraCalibration1          | 50723   | SRATIONAL[] | 1.0     | Per-camera adjustment 1     |
| CameraCalibration2          | 50724   | SRATIONAL[] | 1.0     | Per-camera adjustment 2     |
| ReductionMatrix1            | 50725   | SRATIONAL[] | 1.0     | Reduction, illuminant 1     |
| ReductionMatrix2            | 50726   | SRATIONAL[] | 1.0     | Reduction, illuminant 2     |
| IlluminantData1             | 52533   | UNDEFINED   | 1.6     | Custom illuminant spectrum 1 |
| IlluminantData2             | 52534   | UNDEFINED   | 1.6     | Custom illuminant spectrum 2 |
| IlluminantData3             | 52535   | UNDEFINED   | 1.6     | Custom illuminant spectrum 3 |

`ColorMatrix1` is required for all non-monochrome DNG files.
`CalibrationIlluminant1` values use EXIF LightSource codes (e.g., 17 =
Standard Light A, 21 = D65).

### Lens and Optics

| Tag Name                    | Tag ID  | Type        | Purpose                           |
|-----------------------------|---------|-------------|-----------------------------------|
| LensInfo                    | 50736   | RATIONAL[4] | [min FL, max FL, min FN, max FN] |
| LensMake                    | --      | ASCII       | Lens manufacturer                 |
| LensModel                   | --      | ASCII       | Lens model name                   |

### Opcodes

Introduced in DNG 1.3, opcodes define processing steps to be applied by the
DNG reader. This allows complex processing (lens corrections, noise reduction,
gain adjustment) to be deferred from the camera to more powerful hardware.

**Opcode list tags:**

| Tag Name    | Tag ID | Applied When                                      |
|-------------|--------|---------------------------------------------------|
| OpcodeList1 | 51008  | After reading raw data, before demosaicing         |
| OpcodeList2 | 51009  | After demosaicing (on linear reference values)     |
| OpcodeList3 | 51022  | After mapping to final output color space          |

Each opcode list contains a count followed by an array of opcode records.
Each record specifies the opcode ID, minimum DNG version, flags, and
opcode-specific parameters.

**Opcode types (14 as of DNG 1.7):**

| ID | Name                       | Version | Purpose                               |
|----|----------------------------|---------|---------------------------------------|
| 1  | WarpRectilinear            | 1.3     | Lens distortion correction (radial + tangential) |
| 2  | WarpFisheye                | 1.3     | Fisheye lens correction               |
| 3  | FixVignetteRadial          | 1.3     | Radial vignetting correction          |
| 4  | FixBadPixelsConstant       | 1.3     | Replace bad pixels with constant      |
| 5  | FixBadPixelsList           | 1.3     | Replace bad pixels from coordinate list |
| 6  | TrimBounds                 | 1.3     | Crop image to specified rectangle     |
| 7  | MapTable                   | 1.3     | Apply 16-bit lookup table             |
| 8  | MapPolynomial              | 1.3     | Apply polynomial curve transformation |
| 9  | GainMap                    | 1.3     | Spatially varying gain correction     |
| 10 | DeltaPerRow                | 1.3     | Per-row offset (dark current compensation) |
| 11 | DeltaPerColumn             | 1.3     | Per-column offset correction          |
| 12 | ScalePerRow                | 1.3     | Per-row scale correction              |
| 13 | ScalePerColumn             | 1.3     | Per-column scale correction           |
| 14 | --                         | 1.7     | Additional opcode (DNG 1.7)           |

### Camera Profiles (DNG 1.2+)

DNG supports embedded camera profiles for color rendering. Multiple profiles
can exist within a single file:

| Tag Name                      | Tag ID  | Purpose                              |
|-------------------------------|---------|--------------------------------------|
| ProfileName                   | 50936   | Profile display name                 |
| ProfileCalibrationSignature   | 50932   | Calibration signature string         |
| ProfileCopyright              | 50942   | Profile copyright notice             |
| ProfileEmbedPolicy            | 50941   | 0=allow copying, 1=embed only, 2=never embed, 3=no restrictions |
| ProfileHueSatMapDims          | 50937   | HSV map dimensions (hues, sats, vals)|
| ProfileHueSatMapData1         | 50938   | Hue/saturation map, illuminant 1     |
| ProfileHueSatMapData2         | 50939   | Hue/saturation map, illuminant 2     |
| ProfileHueSatMapData3         | --      | Hue/saturation map, illuminant 3 (1.6+) |
| ProfileToneCurve              | 50940   | Tone curve (input/output value pairs)|
| ExtraCameraProfiles           | 51043   | Pointer to additional profile IFDs   |

### Depth Maps (DNG 1.5+)

| Tag Name                    | Tag ID  | Purpose                              |
|-----------------------------|---------|--------------------------------------|
| DepthFormat                 | --      | Depth data format (uint/float)       |
| DepthNear                   | --      | Near depth plane distance            |
| DepthFar                    | --      | Far depth plane distance             |
| DepthUnits                  | --      | Depth measurement units              |
| DepthMeasureType            | --      | Optical axis vs optical ray          |

### Enhanced/Processed Data (DNG 1.5+)

| Tag Name                    | Tag ID  | Purpose                              |
|-----------------------------|---------|--------------------------------------|
| NewRawImageDigest           | 51111   | MD5 of processed raw data            |
| EnhanceParams               | --      | Enhancement processing parameters    |

### Semantic Masks (DNG 1.6+)

| Tag Name                    | Tag ID  | Purpose                              |
|-----------------------------|---------|--------------------------------------|
| SemanticName                | --      | Mask name (e.g. "Skin", "Sky", "Subject") |
| SemanticInstanceID          | --      | Instance identifier                  |
| MaskSubArea                 | --      | Sub-area coordinates within the mask |

---

## ImageIO Keys: `kCGImagePropertyDNGDictionary`

Available since iOS 4.0.

| Key                                            | Type     | Purpose                          |
|------------------------------------------------|----------|----------------------------------|
| `kCGImagePropertyDNGVersion`                   | CFArray  | DNG version [major, minor, ...]  |
| `kCGImagePropertyDNGBackwardVersion`           | CFArray  | Minimum reader version           |
| `kCGImagePropertyDNGUniqueCameraModel`         | CFString | Camera model identifier          |
| `kCGImagePropertyDNGLocalizedCameraModel`      | CFString | Localized camera model           |
| `kCGImagePropertyDNGCameraSerialNumber`        | CFString | Camera serial number             |
| `kCGImagePropertyDNGLensInfo`                  | CFArray  | Lens info (4 rationals)          |
| `kCGImagePropertyDNGLensMake`                  | CFString | Lens manufacturer                |
| `kCGImagePropertyDNGLensModel`                 | CFString | Lens model                       |
| `kCGImagePropertyDNGAsShotNeutral`             | CFArray  | As-shot white balance            |
| `kCGImagePropertyDNGAnalogBalance`             | CFArray  | Analog balance                   |
| `kCGImagePropertyDNGPrivateData`               | CFData   | Private manufacturer data        |
| `kCGImagePropertyDNGActiveArea`                | CFArray  | Active sensor area [top, left, bottom, right] |
| `kCGImagePropertyDNGBaselineExposure`          | CFNumber | Baseline exposure compensation   |
| `kCGImagePropertyDNGBaselineNoise`             | CFNumber | Baseline noise level             |
| `kCGImagePropertyDNGBaselineSharpness`         | CFNumber | Baseline sharpness               |
| `kCGImagePropertyDNGOriginalRawFileData`       | CFData   | Embedded original raw file data  |
| `kCGImagePropertyDNGOriginalRawFileDigest`     | CFData   | MD5 digest of original           |

---

## Generic RAW: `kCGImagePropertyRawDictionary`

For non-DNG RAW formats, ImageIO uses `kCGImagePropertyRawDictionary` to
expose a generic set of RAW properties. This dictionary contains a smaller,
less standardized set of keys compared to the DNG dictionary.

### Supported RAW Formats in ImageIO

All are **read-only** except DNG.

| Format         | Extension(s) | Vendor            | Dictionary                       |
|----------------|-------------|-------------------|----------------------------------|
| DNG            | .dng        | Adobe (universal) | `kCGImagePropertyDNGDictionary`  |
| Canon CR2      | .cr2        | Canon             | `kCGImagePropertyRawDictionary`  |
| Canon CR3      | .cr3        | Canon (ISOBMFF)   | `kCGImagePropertyRawDictionary`  |
| Canon CRW      | .crw        | Canon (legacy CIFF)| `kCGImagePropertyCIFFDictionary` |
| Nikon NEF      | .nef        | Nikon             | `kCGImagePropertyRawDictionary`  |
| Nikon NRW      | .nrw        | Nikon (Coolpix)   | `kCGImagePropertyRawDictionary`  |
| Sony ARW       | .arw        | Sony              | `kCGImagePropertyRawDictionary`  |
| Sony SRF       | .srf        | Sony (legacy)     | `kCGImagePropertyRawDictionary`  |
| Fujifilm RAF   | .raf        | Fujifilm          | `kCGImagePropertyRawDictionary`  |
| Olympus ORF    | .orf        | Olympus           | `kCGImagePropertyRawDictionary`  |
| Pentax PEF     | .pef        | Pentax            | `kCGImagePropertyRawDictionary`  |
| Panasonic RW2  | .rw2        | Panasonic         | `kCGImagePropertyRawDictionary`  |

Apple maintains a per-camera RAW support list (Apple Support HT211241)
updated with each OS release. Not all camera models from each vendor are
supported.

### Metadata from RAW Files

Even though RAW files use their own format-specific dictionary, the standard
metadata dictionaries work normally:

- **EXIF:** `kCGImagePropertyExifDictionary` -- camera settings, timestamps
- **TIFF:** `kCGImagePropertyTIFFDictionary` -- make, model, orientation
- **GPS:** `kCGImagePropertyGPSDictionary` -- location data
- **XMP:** `CGImageSourceCopyMetadataAtIndex` -- XMP tree (if embedded)
- **ICC:** `kCGImagePropertyProfileName` -- color profile name

The RAW-specific dictionary provides additional format-level properties not
covered by the standard metadata dictionaries.

---

## Apple ProRAW

Apple ProRAW (available on iPhone 12 Pro and later) produces DNG 1.6 files
with Apple's computational photography pipeline baked in.

### Technical Specifications

| Property                | Value                                          |
|-------------------------|------------------------------------------------|
| File format             | DNG 1.6 (TIFF-based container)                |
| Bit depth               | 12-bit per channel (losslessly compressed)     |
| Color depth             | Scene-referred linear RGB                      |
| Resolution options      | 12 MP or 48 MP (iPhone 14 Pro+)               |
| Typical file size       | 25-50 MB (12 MP), larger for 48 MP            |
| Dynamic range           | Up to 14 stops                                 |
| Computational pipeline  | Deep Fusion, Smart HDR baked in                |
| Semantic masks          | Scene segmentation (DNG 1.6 SemanticName tags) |
| Depth data              | Depth map embedded (DNG 1.5 DepthFormat tags)  |
| EXIF metadata           | Full EXIF, GPS, Apple MakerNote                |
| Compression             | Lossless (not JPEG XL -- that requires iPhone 16) |

### Device Support

| Device              | ProRAW | Resolution Options | Notes                    |
|---------------------|--------|--------------------|-----------------------------|
| iPhone 12 Pro/Max   | Yes    | 12 MP              | First ProRAW devices         |
| iPhone 13 Pro/Max   | Yes    | 12 MP              |                              |
| iPhone 14 Pro/Max   | Yes    | 12 MP, 48 MP       | 48 MP main camera option     |
| iPhone 15 Pro/Max   | Yes    | 12 MP, 48 MP       |                              |
| iPhone 16 Pro/Max   | Yes    | 12 MP, 48 MP       | JXL compression available    |

### Limitations

- Cannot be used with Live Photos, Portrait mode, or video
- Significantly larger than HEIC (25-50 MB vs 1-3 MB)
- Processing time is longer than standard capture
- Not all third-party apps support reading/editing ProRAW

---

## Metadata Capacity Summary

| Standard   | DNG     | Other RAW | Notes                               |
|------------|---------|-----------|-------------------------------------|
| **EXIF**   | Yes     | Yes       | Full EXIF IFD structure             |
| **XMP**    | Yes     | Sidecar   | Embedded in DNG (tag 700); sidecar .xmp for others |
| **IPTC IIM** | No   | No        | Use XMP `Iptc4xmpCore` for editorial metadata |
| **ICC**    | Yes     | Yes       | Via TIFF ICC profile tag (34675)    |
| **GPS**    | Yes     | Yes       | GPS IFD within EXIF                 |

**XMP sidecar files:** For read-only RAW formats, XMP metadata is typically
stored in a sidecar `.xmp` file alongside the RAW file, since the RAW file
itself cannot be modified. The sidecar file shares the same base name (e.g.,
`IMG_1234.cr2` + `IMG_1234.xmp`).

---

## Key Characteristics for iOS Development

| Property              | Value                                          |
|-----------------------|------------------------------------------------|
| UTI (DNG)             | `com.adobe.raw-image` / `public.camera-raw-image` |
| ImageIO Read (DNG)    | iOS 4.0+                                       |
| ImageIO Write (DNG)   | iOS 10.0+ (limited)                            |
| ImageIO Read (RAW)    | iOS 4.0+ (per-camera support list)             |
| ImageIO Write (RAW)   | Read-only (except DNG)                         |
| Metadata Standards    | EXIF, XMP (embedded/sidecar), ICC, GPS         |
| Lossless Meta Edit    | No                                             |
| Color Depth           | 12-16 bit per channel (raw sensor data)        |
| Compression           | Uncompressed, JPEG, deflate, or JXL (DNG 1.7) |

---

## Common Gotchas

1. **Read-only RAW** -- All RAW formats except DNG are read-only in ImageIO.
   You cannot write metadata back to CR2, NEF, ARW, etc. Use DNG conversion
   or XMP sidecar files.

2. **Per-camera support** -- Not all camera models are supported. Check
   Apple's HT211241 support article. Unsupported RAW files will fail to
   create a `CGImageSource`.

3. **DNG version compatibility** -- Older DNG readers may not support features
   from newer DNG versions (e.g., BigTIFF, triple-illuminant, JXL
   compression). `DNGBackwardVersion` declares the minimum reader version.

4. **Color matrix required** -- `ColorMatrix1` is mandatory for all
   non-monochrome DNG files. Missing it causes color rendering failures.

5. **Fujifilm RAF** -- Only uncompressed RAF files are supported by ImageIO.
   Compressed RAF files may fail to decode silently.

6. **ProRAW size** -- Apple ProRAW DNG files are 10-12x larger than HEIC
   equivalents due to 12-bit losslessly compressed data.

7. **BigTIFF (DNG 1.6+)** -- Files using 64-bit offsets (magic number 43
   instead of 42) require readers that understand BigTIFF. Older TIFF
   libraries may reject these files.

8. **Opcodes are optional** -- DNG readers are not required to implement all
   opcodes. If a reader skips lens correction opcodes, the output may have
   visible distortion. Check the opcode's minimum version and flags.

---

## Cross-References

- **EXIF tags:** `references/exif/tag-reference.md`
- **ImageIO RAW support:** `references/imageio/supported-formats.md` (RAW section)
- **Auxiliary data (depth):** `references/imageio/auxiliary-data.md`
- **XMP sidecar files:** `references/xmp/` (XMP standard reference)
- **CIFF (Canon legacy):** `references/formats/other-formats.md` (CIFF section)
- **ImageIO format support:** `references/imageio/supported-formats.md`
- **All DNG keys:** `references/imageio/property-keys.md` (DNG Dictionary)
