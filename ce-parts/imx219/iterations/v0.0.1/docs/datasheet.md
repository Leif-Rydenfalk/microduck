# IMX219PQH5-C — the datasheet behind the record

| | |
|---|---|
| document | Sony, "Diagonal 4.60 mm (Type 1/4.0) 8 Mega-Pixel CMOS Image Sensor with Square Pixel for Color Cameras — IMX219PQH5-C", 96 pages, **no document number or revision printed**; PDF metadata title `sony`, created 2014-04-24 |
| URL | https://www.opensourceinstruments.com/Electronics/Data/IMX219PQ.pdf (mirror — Sony does not publish it) |
| cross-check | https://storage.googleapis.com/publiclab-production/public/system/images/photos/000/023/294/original/RASPBERRY_PI_CAMERA_V2_DATASHEET_IMX219PQH5_7.0.0_Datasheet_XXX.PDF — identical bytes |
| fetched | 2026-09-02, HTTP 200, 2237503 bytes |
| file | `../datasheet.pdf`, sha256 `49250b153d55fe91a5a184651ef0eeab4316a195f7f6c2d42c068b336f237219` |
| why this part | probe log `imx219 2-0010: Model ID 0x0219` (`research/raw/microduck_main_docs_project_media-bringup.md:312`); overlay `radxa-zero3-rpi-camera-v2` |
| identity | family confirmed by Model ID; the `-PQH5-C` suffix is what a Pi Camera v2 carries — inferred for Pollen's M12 board, not read |

## Figures, verbatim

| figure | quote | cite |
|---|---|---|
| pixels | `Number of active pixels : 3280 (H) × 2464 (V) approx. 8.08 M pixels` | p.2 |
| chip | `Chip size : 5.095 mm (H) × 4.930 mm (V) (w/ Scribe)` · `Unit cell size : 1.12 µm` | p.2 |
| VANA | `Supply voltage (analogue) \| VANA \| 2.6 \| 2.8 \| 3.0 \| V` | Table 42 p.84 |
| VDDL | `Supply voltage (Core) \| VDDL \| 1.08 \| 1.2 \| 1.3 \| V` | Table 42 p.84 |
| VDIG | `Supply voltage (IF) \| VDIG \| 1.62 \| 1.8 \| 1.98 \| V` | Table 42 p.84 |
| abs max | `VANA \| -0.3 \| 3.3` · `VDDL \| -0.3 \| 2.0` · `VDIG \| -0.3 \| 3.3` V; `Topr \| -20 \| 60 ˚C \| Junction temperature` | Table 41 p.84 |
| current | `IVAVA_strm \| 33 \| 38 \| mA` (VANA) · `IVDDL_strm \| 100 \| 160 \| mA` (VDDL), Full 30 fps, CSI2 4 lanes | Table 45 p.86 |
| INCK | `Frequency \| fSCK \| 6 \| 18 \| 27 \| MHz` | Table 44 p.86 |
| I2C address | `[7:1] \| 0 0 1 0 0 0 0 \| R/W` (= 0x10) | Fig. 10 p.18 |
| CSI-2 | `IMX219PQH5-C has CSI-2 interface and the options are 4 lanes or 2lanes.` | p.16 |
| frame rate | `Max. 30 frame/s in all-pixel scan mode` · `60 frame/s @1080p with V-crop` | p.1 |

## Still CANNOT DETERMINE

the carrier board (regulators, clock source, lanes wired, ribbon), the lens (focal length / FOV / aperture — no part number exists to fetch), the sensor suffix on Pollen's board.
