# EXIF Tag Reference — Semantic Details

> Part of [EXIF Reference](README.md)

Detailed semantics, enum values, and usage notes for EXIF tags organized by
category. For raw tag tables with IDs, types, and byte counts, see
[`technical-structure.md`](technical-structure.md). For ImageIO property keys,
see [`imageio-mapping.md`](imageio-mapping.md).

---

## Camera & Exposure

| Tag | ID | Values / Notes |
|-----|----|----------------|
| ExposureTime | 0x829a | Exposure in seconds as a rational (e.g., 1/250 stored as 1/250) |
| FNumber | 0x829d | F-stop as rational (e.g., f/2.8 stored as 28/10) |
| ExposureProgram | 0x8822 | 0=Not defined, 1=Manual, 2=Normal program, 3=Aperture priority, 4=Shutter priority, 5=Creative (biased toward depth of field), 6=Action (biased toward fast shutter), 7=Portrait, 8=Landscape |
| ISOSpeedRatings | 0x8827 | Array of ISO sensitivity values (e.g., [100]) |
| SensitivityType | 0x8830 | Which ISO 12232 parameter is stored: 0=Unknown, 1=SOS, 2=REI, 3=SOS+REI, 4=ISO Speed, 5=SOS+ISO, 6=REI+ISO, 7=SOS+REI+ISO *(v2.3+)* |
| StandardOutputSensitivity | 0x8831 | SOS value per ISO 12232 *(v2.3+)* |
| RecommendedExposureIndex | 0x8832 | REI value per ISO 12232 *(v2.3+)* |
| ISOSpeed | 0x8833 | ISO speed per ISO 12232 *(v2.3+)* |
| ISOSpeedLatitudeyyy | 0x8834 | ISO speed latitude yyy *(v2.3+)* |
| ISOSpeedLatitudezzz | 0x8835 | ISO speed latitude zzz *(v2.3+)* |
| ExposureIndex | 0xa215 | Camera exposure index at capture time |
| ExposureMode | 0xa402 | 0=Auto, 1=Manual, 2=Auto bracket *(v2.2+)* |
| ExposureBiasValue | 0x9204 | Exposure compensation in EV (e.g., -1.0, +0.7) |
| SpectralSensitivity | 0x8824 | Spectral sensitivity per ASTM E-1417 |
| OECF | 0x8828 | Opto-Electronic Conversion Function per ISO 14524 |

---

## APEX Values, Metering & Flash

| Tag | ID | Values / Notes |
|-----|----|----------------|
| ShutterSpeedValue | 0x9201 | APEX value. Convert: exposure time = 2^(-value). E.g., value 8 → 1/256s |
| ApertureValue | 0x9202 | APEX value. Convert: F-number = 2^(value/2). E.g., value 5 → f/5.6 |
| BrightnessValue | 0x9203 | APEX brightness. Value -1 means unknown |
| MaxApertureValue | 0x9205 | Smallest F-number of the lens (APEX) |
| MeteringMode | 0x9207 | 0=Unknown, 1=Average, 2=Center-weighted average, 3=Spot, 4=Multi-spot, 5=Pattern (evaluative/matrix), 6=Partial, 255=Other |
| LightSource | 0x9208 | 0=Unknown, 1=Daylight, 2=Fluorescent, 3=Tungsten (incandescent), 4=Flash, 9=Fine weather, 10=Cloudy, 11=Shade, 12=Daylight fluorescent (D 5700–7100K), 13=Day white fluorescent (N 4600–5500K), 14=Cool white fluorescent (W 3800–4500K), 15=White fluorescent (WW 3200–3700K), 17=Standard light A, 18=Standard light B, 19=Standard light C, 20=D55, 21=D65, 22=D75, 23=D50, 24=ISO studio tungsten, 255=Other |
| Flash | 0x9209 | Bitfield — see decode table below |
| FlashEnergy | 0xa20b | Flash energy in BCPS (beam candle power seconds) |
| GainControl | 0xa407 | 0=None, 1=Low gain up, 2=High gain up, 3=Low gain down, 4=High gain down *(v2.2+)* |

### Flash Bitfield Decode

The Flash tag is a 16-bit bitfield:

```
Bit 0:     Fired           0 = No, 1 = Yes
Bits 1-2:  Return          00 = No strobe return detection function
                            01 = Reserved
                            10 = Strobe return light not detected
                            11 = Strobe return light detected
Bits 3-4:  Mode            00 = Unknown
                            01 = Compulsory flash firing
                            10 = Compulsory flash suppression
                            11 = Auto mode
Bit 5:     Function        0 = Flash function present
                            1 = No flash function
Bit 6:     Red-eye         0 = No red-eye reduction
                            1 = Red-eye reduction supported
```

Common combined values:

| Value | Hex | Meaning |
|-------|-----|---------|
| 0 | 0x00 | No flash |
| 1 | 0x01 | Flash fired |
| 5 | 0x05 | Flash fired, return not detected |
| 7 | 0x07 | Flash fired, return detected |
| 16 | 0x10 | Flash did not fire, compulsory suppression |
| 24 | 0x18 | Flash did not fire, auto mode |
| 25 | 0x19 | Flash fired, auto mode |
| 65 | 0x41 | Flash fired, red-eye reduction |
| 73 | 0x49 | Flash fired, compulsory flash, red-eye reduction |
| 89 | 0x59 | Flash fired, auto, red-eye reduction |

---

## Subject & Sensing

| Tag | ID | Values / Notes |
|-----|----|----------------|
| SubjectDistance | 0x9206 | Distance to subject in meters. 0 = unknown, 0xFFFFFFFF = infinity |
| SubjectArea | 0x9214 | 2 values = center point (x,y); 3 = circle (x,y,diameter); 4 = rectangle (x,y,width,height) *(v2.2+)* |
| SubjectLocation | 0xa214 | (x, y) coordinates of main subject in pixels |
| SubjectDistanceRange | 0xa40c | 0=Unknown, 1=Macro, 2=Close view, 3=Distant view *(v2.2+)* |
| SensingMethod | 0xa217 | 1=Not defined, 2=One-chip color area sensor, 3=Two-chip, 4=Three-chip, 5=Color sequential area, 7=Trilinear, 8=Color sequential linear |
| SpatialFrequencyResponse | 0xa20c | Camera spatial frequency response per ISO 12233 |
| DeviceSettingDescription | 0xa40b | Device-specific settings data *(v2.2+)* |
| CFAPattern | 0xa302 | Color filter array pattern |

---

## Focal Length & Lens

| Tag | ID | Values / Notes |
|-----|----|----------------|
| FocalLength | 0x920a | Actual focal length of the lens in millimeters |
| FocalLengthIn35mmFilm | 0xa405 | 35mm equivalent focal length in mm. 0=unknown *(v2.2+)* |
| LensSpecification | 0xa432 | 4 rationals: [MinFocalLength, MaxFocalLength, MinFNumber@MinFL, MinFNumber@MaxFL]. For a fixed 50mm f/1.8 lens: [50, 50, 1.8, 1.8] *(v2.3+)* |
| LensMake | 0xa433 | Lens manufacturer name *(v2.3+)* |
| LensModel | 0xa434 | Lens model name/number *(v2.3+)* |
| LensSerialNumber | 0xa435 | Lens serial number string *(v2.3+)* |
| FocalPlaneXResolution | 0xa20e | Number of pixels per FocalPlaneResolutionUnit on the sensor (horizontal). Used with sensor dimensions to calculate actual focal length equivalents |
| FocalPlaneYResolution | 0xa20f | Same, vertical |
| FocalPlaneResolutionUnit | 0xa210 | 1=No unit, 2=Inch, 3=Centimeter. Applies to FocalPlaneXResolution and FocalPlaneYResolution |

---

## Image Dimensions & Color

| Tag | ID | Values / Notes |
|-----|----|----------------|
| PixelXDimension | 0xa002 | Valid width of the meaningful image data (for compressed data where padding may exist) |
| PixelYDimension | 0xa003 | Valid height of the meaningful image data |
| ColorSpace | 0xa001 | 1=sRGB, 65535=Uncalibrated. Value 2 appears in some files/tools as non-standard Adobe RGB signaling. When 65535, check the ICC profile for actual color space |
| ComponentsConfiguration | 0x9101 | 4-byte channel order: 0=does not exist, 1=Y, 2=Cb, 3=Cr, 4=R, 5=G, 6=B. Typical YCbCr: `[1,2,3,0]`. RGB: `[4,5,6,0]` |
| CompressedBitsPerPixel | 0x9102 | Average compression ratio for the image |
| Gamma | 0xa500 | Gamma coefficient of the image *(v2.3+)* |

---

## Date & Time

EXIF defines three parallel timestamp triplets. Each has a base tag, a
subsecond precision tag, and a timezone offset tag:

| Timestamp | Base Tag | SubSec Tag | Offset Tag | Meaning |
|-----------|----------|------------|------------|---------|
| **DateTime** | DateTime (0x0132, IFD0) | SubSecTime (0x9290) | OffsetTime (0x9010) | File last modified |
| **DateTimeOriginal** | DateTimeOriginal (0x9003) | SubSecTimeOriginal (0x9291) | OffsetTimeOriginal (0x9011) | Shutter actuation (capture time) |
| **DateTimeDigitized** | DateTimeDigitized (0x9004) | SubSecTimeDigitized (0x9292) | OffsetTimeDigitized (0x9012) | Analog-to-digital conversion |

**Format details:**

- **Base tags:** 20 ASCII characters: `"YYYY:MM:DD HH:MM:SS\0"` (note: colons
  separate date components, not hyphens)
- **SubSec tags:** Variable-length ASCII decimal digits. `"2"` = 0.2s,
  `"23"` = 0.23s, `"234"` = 0.234s — precision is manufacturer-chosen
- **OffsetTime tags** *(v2.31+)*: 7 ASCII characters: `"+HH:MM\0"` or
  `"-HH:MM\0"`. iPhone always writes these. Many third-party cameras omit them,
  leaving timestamps timezone-ambiguous

> **DateTime lives in IFD0**, not the Exif SubIFD. DateTimeOriginal and
> DateTimeDigitized are in the Exif SubIFD.

---

## Scene & Processing

| Tag | ID | Values / Notes |
|-----|----|----------------|
| WhiteBalance | 0xa403 | 0=Auto, 1=Manual *(v2.2+)* |
| DigitalZoomRatio | 0xa404 | Ratio of digital zoom. 0=not used *(v2.2+)* |
| SceneCaptureType | 0xa406 | 0=Standard, 1=Landscape, 2=Portrait, 3=Night scene *(v2.2+)* |
| SceneType | 0xa301 | 1=A directly photographed image |
| Contrast | 0xa408 | 0=Normal, 1=Soft, 2=Hard *(v2.2+)* |
| Saturation | 0xa409 | 0=Normal, 1=Low saturation, 2=High saturation *(v2.2+)* |
| Sharpness | 0xa40a | 0=Normal, 1=Soft, 2=Hard *(v2.2+)* |
| CustomRendered | 0xa401 | 0=Normal process, 1=Custom process *(v2.2+)* |
| FileSource | 0xa300 | 1=Film scanner, 2=Reflection print scanner, 3=Digital still camera |

---

## Composite Images (v2.32+)

Used for computational photography — Night Mode, HDR stacking, multi-exposure
composites.

| Tag | ID | Description |
|-----|----|-------------|
| CompositeImage | 0xa460 | 0=Unknown, 1=Not a composite, 2=General composite image, 3=Composite image captured while shooting |
| SourceImageNumberOfCompositeImage | 0xa461 | Two SHORT values: [total source images, number actually used] |
| SourceExposureTimesOfCompositeImage | 0xa462 | Total exposure time followed by individual exposure times of each source image |

Value 3 ("captured while shooting") indicates computational photography where
multiple frames are captured and merged in a single shutter actuation — e.g.,
iPhone Night Mode, Smart HDR.

---

## Environmental Conditions (v2.31+)

Tags for recording ambient conditions at capture time. Primarily used in
specialized, scientific, or underwater imaging.

| Tag | ID | Type | Unit | Description |
|-----|----|------|------|-------------|
| Temperature | 0x9400 | SRational | °C | Ambient temperature |
| Humidity | 0x9401 | Rational | % | Relative humidity |
| Pressure | 0x9402 | Rational | hPa | Atmospheric pressure |
| WaterDepth | 0x9403 | SRational | meters | Depth underwater (negative = above surface) |
| Acceleration | 0x9404 | Rational | mGal (10⁻⁵ m/s²) | Gravitational acceleration |
| CameraElevationAngle | 0x9405 | SRational | degrees | Camera tilt from horizontal |

---

## Version & Identity

| Tag | ID | Description |
|-----|----|-------------|
| ExifVersion | 0x9000 | 4 ASCII bytes: `"0210"` = v2.1, `"0220"` = v2.2, `"0230"` = v2.3, `"0231"` = v2.31, `"0232"` = v2.32, `"0300"` = v3.0 |
| FlashpixVersion | 0xa000 | FlashPix format version, typically `"0100"` |
| ImageUniqueID | 0xa420 | 128-bit unique identifier as 32 hex characters |
| CameraOwnerName | 0xa430 | Name of the camera owner *(v2.3+)* |
| BodySerialNumber | 0xa431 | Camera body serial number *(v2.3+)* |
| RelatedSoundFile | 0xa004 | Name of related audio file in 8.3 format |

### MakerNote (0x927c)

Vendor-specific binary data in a proprietary format. Not standardized beyond
the tag definition. See [`makernote.md`](makernote.md) for details.

### UserComment (0x9286)

The first 8 bytes identify the character encoding, followed by the comment text:

| Charset ID (8 bytes) | Encoding |
|-----------------------|----------|
| `ASCII\0\0\0` | US-ASCII |
| `JIS\0\0\0\0\0` | JIS X 0208-1990 |
| `UNICODE\0` | Unicode (typically UCS-2) |
| `\0\0\0\0\0\0\0\0` | Undefined (treat as system default) |

---

## EXIF 3.0 Tags

New identity tags added in EXIF 3.0 (May 2023). These support the new UTF-8
data type (type ID 129) for non-ASCII text.

| Tag | ID | Description |
|-----|----|-------------|
| ImageTitle | 0xa436 | Title of the image |
| Photographer | 0xa437 | Name of the photographer |
| ImageEditor | 0xa438 | Name of the main image editor |
| CameraFirmware | 0xa439 | Camera firmware name and version |
| RAWDevelopingSoftware | 0xa43a | RAW development software name and version |
| ImageEditingSoftware | 0xa43b | Image editing software name and version |
| MetadataEditingSoftware | 0xa43c | Metadata editing software name and version |
