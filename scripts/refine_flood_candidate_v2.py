import numpy as np
from pathlib import Path
from osgeo import gdal
from scipy import ndimage


BASE = Path(".")

INPUT = (
    BASE
    / "data/processed/final_flood_candidate_v1.tif"
)

OUTPUT = (
    BASE
    / "data/processed/final_flood_candidate_v2.tif"
)

MIN_PATCH_PIXELS = 25


print("=" * 65)
print("FloodSpaceAI — Flood Candidate V2")
print("=" * 65)

ds = gdal.Open(str(INPUT), gdal.GA_ReadOnly)

if ds is None:
    raise RuntimeError(
        f"Could not open {INPUT}"
    )

band = ds.GetRasterBand(1)

array = band.ReadAsArray()

nodata = band.GetNoDataValue()

print("Input:", INPUT)
print(
    "Raster:",
    ds.RasterXSize,
    "x",
    ds.RasterYSize
)

print("NoData:", nodata)

# ------------------------------------------------------------
# Create binary candidate mask
# ------------------------------------------------------------

mask = (
    np.isfinite(array)
    & (array == 1)
)

print(
    "V1 candidate pixels:",
    int(mask.sum())
)


# ------------------------------------------------------------
# Connected-component analysis
# ------------------------------------------------------------

print(
    "\nFinding connected flood patches..."
)

structure = np.ones(
    (3, 3),
    dtype=np.uint8
)

labels, num_features = ndimage.label(
    mask,
    structure=structure
)

print(
    "Initial connected patches:",
    num_features
)


# ------------------------------------------------------------
# Remove tiny isolated patches
# ------------------------------------------------------------

sizes = np.bincount(
    labels.ravel()
)

keep = sizes >= MIN_PATCH_PIXELS

keep[0] = False

filtered = keep[
    labels
]

filtered = filtered.astype(
    np.uint8
)


# ------------------------------------------------------------
# Statistics
# ------------------------------------------------------------

v1_pixels = int(
    mask.sum()
)

v2_pixels = int(
    filtered.sum()
)

removed = (
    v1_pixels - v2_pixels
)

if v1_pixels:
    reduction = (
        removed / v1_pixels
    ) * 100
else:
    reduction = 0


remaining_patches = 0

if v2_pixels:

    remaining_labels = np.unique(
        labels[filtered == 1]
    )

    remaining_patches = len(
        remaining_labels
    )


print()
print(
    "Minimum patch size:",
    MIN_PATCH_PIXELS,
    "pixels"
)

print(
    "V1 candidate pixels:",
    v1_pixels
)

print(
    "V2 candidate pixels:",
    v2_pixels
)

print(
    "Removed pixels:",
    removed
)

print(
    "Reduction:",
    round(reduction, 2),
    "%"
)

print(
    "Remaining patches:",
    remaining_patches
)


# ------------------------------------------------------------
# Write GeoTIFF
# ------------------------------------------------------------

driver = gdal.GetDriverByName(
    "GTiff"
)

out = driver.Create(
    str(OUTPUT),
    ds.RasterXSize,
    ds.RasterYSize,
    1,
    gdal.GDT_Byte,
    options=[
        "COMPRESS=LZW",
        "TILED=YES"
    ]
)

out.SetGeoTransform(
    ds.GetGeoTransform()
)

out.SetProjection(
    ds.GetProjection()
)

out_band = out.GetRasterBand(1)

out_band.WriteArray(
    filtered
)

out_band.SetNoDataValue(
    255
)

out_band.SetDescription(
    "Flood candidate V2 - connected patch filtered"
)

out_band.FlushCache()

out.FlushCache()

out = None
ds = None


print()
print("=" * 65)
print("V2 COMPLETE")
print("=" * 65)

print(
    "Saved:",
    OUTPUT
)

print()
print(
    "IMPORTANT:"
)

print(
    "V2 only removes small isolated candidate patches."
)

print(
    "It does NOT prove that remaining pixels are floodwater."
)

print("=" * 65)