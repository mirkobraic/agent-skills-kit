# EXIF ↔ XMP Standard Mapping

> Part of [EXIF Reference](README.md)

How EXIF tags map to XMP properties as defined by the XMP specification
(ISO 16684-1) and CIPA's ExifEX namespace. This documents the standard mapping
independent of any framework. For ImageIO-specific access (property keys, bridge
functions, auto-synthesis), see [`imageio-mapping.md`](imageio-mapping.md).

---

## XMP Namespaces for EXIF

| Namespace URI | Prefix | Scope |
|---------------|--------|-------|
| `http://ns.adobe.com/exif/1.0/` | `exif` | Core Exif IFD tags (pre-2.3) |
| `http://ns.adobe.com/exif/1.0/aux/` | `aux` | Auxiliary lens/camera data (Adobe origin) |
| `http://cipa.jp/exif/1.0/` | `exifEX` | EXIF 2.3+ extension tags (CIPA) |
| `http://ns.adobe.com/tiff/1.0/` | `tiff` | IFD0 tags (Make, Model, Orientation, etc.) |

---

## Exif IFD Tags → `exif:` Namespace

| EXIF Tag | ID | XMP Path | XMP Type |
|----------|----|----------|----------|
| ExposureTime | 0x829a | `exif:ExposureTime` | Rational |
| FNumber | 0x829d | `exif:FNumber` | Rational |
| ExposureProgram | 0x8822 | `exif:ExposureProgram` | Integer |
| SpectralSensitivity | 0x8824 | `exif:SpectralSensitivity` | Text |
| ISOSpeedRatings | 0x8827 | `exif:ISOSpeedRatings` | Seq Integer |
| OECF | 0x8828 | `exif:OECF` | Structure |
| SensitivityType | 0x8830 | `exifEX:SensitivityType` | Integer |
| StandardOutputSensitivity | 0x8831 | `exifEX:StandardOutputSensitivity` | Integer |
| RecommendedExposureIndex | 0x8832 | `exifEX:RecommendedExposureIndex` | Integer |
| ISOSpeed | 0x8833 | `exifEX:ISOSpeed` | Integer |
| ISOSpeedLatitudeyyy | 0x8834 | `exifEX:ISOSpeedLatitudeyyy` | Integer |
| ISOSpeedLatitudezzz | 0x8835 | `exifEX:ISOSpeedLatitudezzz` | Integer |
| ExifVersion | 0x9000 | `exif:ExifVersion` | Text |
| DateTimeOriginal | 0x9003 | `exif:DateTimeOriginal` | Date |
| DateTimeDigitized | 0x9004 | `exif:DateTimeDigitized` | Date |
| ComponentsConfiguration | 0x9101 | `exif:ComponentsConfiguration` | Seq Integer |
| CompressedBitsPerPixel | 0x9102 | `exif:CompressedBitsPerPixel` | Rational |
| ShutterSpeedValue | 0x9201 | `exif:ShutterSpeedValue` | Rational |
| ApertureValue | 0x9202 | `exif:ApertureValue` | Rational |
| BrightnessValue | 0x9203 | `exif:BrightnessValue` | Rational |
| ExposureBiasValue | 0x9204 | `exif:ExposureBiasValue` | Rational |
| MaxApertureValue | 0x9205 | `exif:MaxApertureValue` | Rational |
| SubjectDistance | 0x9206 | `exif:SubjectDistance` | Rational |
| MeteringMode | 0x9207 | `exif:MeteringMode` | Integer |
| LightSource | 0x9208 | `exif:LightSource` | Integer |
| Flash | 0x9209 | `exif:Flash` | Structure |
| FocalLength | 0x920a | `exif:FocalLength` | Rational |
| SubjectArea | 0x9214 | `exif:SubjectArea` | Seq Integer |
| MakerNote | 0x927c | — | Not mapped to XMP (proprietary binary) |
| UserComment | 0x9286 | `exif:UserComment` | Alt Text |
| SubSecTime | 0x9290 | `exif:SubSecTime` | Text |
| SubSecTimeOriginal | 0x9291 | `exif:SubSecTimeOriginal` | Text |
| SubSecTimeDigitized | 0x9292 | `exif:SubSecTimeDigitized` | Text |
| FlashpixVersion | 0xa000 | `exif:FlashpixVersion` | Text |
| ColorSpace | 0xa001 | `exif:ColorSpace` | Integer |
| PixelXDimension | 0xa002 | `exif:PixelXDimension` | Integer |
| PixelYDimension | 0xa003 | `exif:PixelYDimension` | Integer |
| RelatedSoundFile | 0xa004 | `exif:RelatedSoundFile` | Text |
| FlashEnergy | 0xa20b | `exif:FlashEnergy` | Rational |
| SpatialFrequencyResponse | 0xa20c | `exif:SpatialFrequencyResponse` | Structure |
| FocalPlaneXResolution | 0xa20e | `exif:FocalPlaneXResolution` | Rational |
| FocalPlaneYResolution | 0xa20f | `exif:FocalPlaneYResolution` | Rational |
| FocalPlaneResolutionUnit | 0xa210 | `exif:FocalPlaneResolutionUnit` | Integer |
| SubjectLocation | 0xa214 | `exif:SubjectLocation` | Seq Integer |
| ExposureIndex | 0xa215 | `exif:ExposureIndex` | Rational |
| SensingMethod | 0xa217 | `exif:SensingMethod` | Integer |
| FileSource | 0xa300 | `exif:FileSource` | Integer |
| SceneType | 0xa301 | `exif:SceneType` | Integer |
| CFAPattern | 0xa302 | `exif:CFAPattern` | Structure |
| CustomRendered | 0xa401 | `exif:CustomRendered` | Integer |
| ExposureMode | 0xa402 | `exif:ExposureMode` | Integer |
| WhiteBalance | 0xa403 | `exif:WhiteBalance` | Integer |
| DigitalZoomRatio | 0xa404 | `exif:DigitalZoomRatio` | Rational |
| FocalLengthIn35mmFilm | 0xa405 | `exif:FocalLengthIn35mmFilm` | Integer |
| SceneCaptureType | 0xa406 | `exif:SceneCaptureType` | Integer |
| GainControl | 0xa407 | `exif:GainControl` | Integer |
| Contrast | 0xa408 | `exif:Contrast` | Integer |
| Saturation | 0xa409 | `exif:Saturation` | Integer |
| Sharpness | 0xa40a | `exif:Sharpness` | Integer |
| DeviceSettingDescription | 0xa40b | `exif:DeviceSettingDescription` | Structure |
| SubjectDistanceRange | 0xa40c | `exif:SubjectDistanceRange` | Integer |
| ImageUniqueID | 0xa420 | `exif:ImageUniqueID` | Text |
| Gamma | 0xa500 | `exifEX:Gamma` | Rational |

---

## EXIF 2.3+ Tags → `exifEX:` Namespace

Tags added in EXIF 2.3 and later use the CIPA ExifEX namespace:

| EXIF Tag | ID | XMP Path | XMP Type |
|----------|----|----------|----------|
| CameraOwnerName | 0xa430 | `exifEX:CameraOwnerName` | Text |
| BodySerialNumber | 0xa431 | `exifEX:BodySerialNumber` | Text |
| LensSpecification | 0xa432 | `exifEX:LensSpecification` | Seq Rational |
| LensMake | 0xa433 | `exifEX:LensMake` | Text |
| LensModel | 0xa434 | `exifEX:LensModel` | Text |
| LensSerialNumber | 0xa435 | `exifEX:LensSerialNumber` | Text |
| CompositeImage | 0xa460 | `exifEX:CompositeImage` | Integer |
| SourceImageNumberOfCompositeImage | 0xa461 | `exifEX:SourceImageNumberOfCompositeImage` | Seq Integer |
| SourceExposureTimesOfCompositeImage | 0xa462 | `exifEX:SourceExposureTimesOfCompositeImage` | Text |

> **OffsetTime tags** (0x9010–0x9012) are EXIF 2.31+ additions, but in XMP
> they are folded into the datetime value itself rather than stored as separate
> properties. For example, `exif:DateTimeOriginal` becomes an ISO 8601 string
> with timezone: `"2024-06-15T14:30:00+05:30"`.

---

## Auxiliary Data → `aux:` Namespace

These originated as Adobe-defined XMP properties for lens/camera data before
EXIF 2.3 standardized equivalent tags:

| Description | XMP Path | EXIF 2.3+ Equivalent |
|-------------|----------|---------------------|
| Lens info [min FL, max FL, min FN at min FL, min FN at max FL] | `aux:LensInfo` | LensSpecification (0xa432) |
| Lens model name | `aux:Lens` | LensModel (0xa434) |
| Lens numeric identifier | `aux:LensID` | — (no standard equivalent) |
| Lens serial number | `aux:LensSerialNumber` | LensSerialNumber (0xa435) |
| Camera serial number | `aux:SerialNumber` | BodySerialNumber (0xa431) |
| Image sequence number | `aux:ImageNumber` | — |
| Flash compensation | `aux:FlashCompensation` | — |
| Camera owner name | `aux:OwnerName` | CameraOwnerName (0xa430) |
| Firmware version | `aux:Firmware` | — |

When both `aux:` and `exifEX:` versions exist, the `exifEX:` (standard) value
takes precedence.

---

## IFD0 Tags → `tiff:` Namespace

IFD0 tags that often appear alongside EXIF data map to the `tiff:` XMP
namespace:

| IFD0 Tag | ID | XMP Path | XMP Type |
|----------|----|----------|----------|
| Make | 0x010f | `tiff:Make` | Text |
| Model | 0x0110 | `tiff:Model` | Text |
| Orientation | 0x0112 | `tiff:Orientation` | Integer |
| Software | 0x0131 | `tiff:Software` | Text |
| DateTime | 0x0132 | `tiff:DateTime` | Date |
| Artist | 0x013b | `tiff:Artist` | Text |
| Copyright | 0x8298 | `tiff:Copyright` | Text |
| ImageDescription | 0x010e | `tiff:ImageDescription` | Alt Text |

---

## Key Differences: EXIF Binary vs XMP Representation

| Aspect | EXIF Binary | XMP |
|--------|------------|-----|
| **DateTime format** | `"YYYY:MM:DD HH:MM:SS"` (naive, no timezone) | ISO 8601 with timezone (e.g., `"2024-06-15T14:30:00+05:30"`) |
| **OffsetTime** | Separate tags (0x9010–0x9012) | Folded into datetime value |
| **Flash** | Single 16-bit bitfield | XMP Structure with named fields (`Fired`, `Return`, `Mode`, `Function`, `RedEyeMode`) |
| **GPS coordinates** | 3 RATIONALs (deg/min/sec) + Ref letter | Encoded string `"DDD,MM,SS.SSK"` or `"DDD,MM.MMK"` |
| **ISOSpeedRatings** | SHORT array | `rdf:Seq` of integers |
| **UserComment** | 8-byte charset ID + raw text bytes | `rdf:Alt` (language alternative text) |
| **MakerNote** | Vendor-specific binary blob | Not represented (proprietary) |
| **SubjectArea** | SHORT array (2–4 values) | `rdf:Seq` of integers |
| **LensSpecification** | 4 RATIONAL values in EXIF binary | `rdf:Seq` of rationals in `exifEX:` |
