import numpy as np
from pathlib import Path
from osgeo import gdal
from scipy import ndimage


BASE = Path(".")

VV_CHANGE = BASE / "data/processed/filtered_vv_change_db.tif"
VH_CHANGE = BASE / "data/processed/filtered_vh_change_db.tif"

PRE_NDWI = (
    BASE
    / "data/processed/sentinel2_pre_ndwi_20260812_cloudmasked.tif"
)

POST_NDWI = (
    BASE
    / "data/processed/sentinel2_ndwi_20260827_cloudmasked.tif"
)

NDWI_CHANGE = (
    BASE
    / "data/processed/ndwi_change_20260827_vs_20260812.tif"
)

OUTPUT = (
    BASE
    / "data/processed/final_flood_candidate_v3.tif"
)

MIN_PATCH_PIXELS = 25


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def read_raster(path):

    ds = gdal.Open(str(path), gdal.GA_ReadOnly)

    if ds is None:
        raise RuntimeError(
            f"Could not open: {path}"
        )

    array = ds.GetRasterBand(1).ReadAsArray()

    nodata = ds.GetRasterBand(1).GetNoDataValue()

    return ds, array, nodata


def valid(array, nodata):

    mask = np.isfinite(array)

    if nodata is not None:
        mask &= array != nodata

    return mask


# ------------------------------------------------------------
# Start
# ------------------------------------------------------------

print("=" * 70)
print("FloodSpaceAI — Flood Candidate V3")
print("=" * 70)

print("\nLoading existing rasters...")

vv_ds, vv, vv_nodata = read_raster(VV_CHANGE)
vh_ds, vh, vh_nodata = read_raster(VH_CHANGE)
pre_ds, pre_ndwi, pre_nodata = read_raster(PRE_NDWI)
post_ds, post_ndwi, post_nodata = read_raster(POST_NDWI)
change_ds, ndwi_change, change_nodata = read_raster(NDWI_CHANGE)


# ------------------------------------------------------------
# Verify dimensions
# ------------------------------------------------------------

shapes = {
    "VV": vv.shape,
    "VH": vh.shape,
    "pre NDWI": pre_ndwi.shape,
    "post NDWI": post_ndwi.shape,
    "NDWI change": ndwi_change.shape,
}

print("\nRaster dimensions:")

for name, shape in shapes.items():
    print(
        f"  {name:15s}: {shape}"
    )

if len(set(shapes.values())) != 1:
    raise RuntimeError(
        "Raster dimensions do not match."
    )


# ------------------------------------------------------------
# Valid data mask
# ------------------------------------------------------------

valid_mask = (
    valid(vv, vv_nodata)
    & valid(vh, vh_nodata)
    & valid(pre_ndwi, pre_nodata)
    & valid(post_ndwi, post_nodata)
    & valid(ndwi_change, change_nodata)
)


print(
    "\nValid common pixels:",
    int(valid_mask.sum())
)


# ------------------------------------------------------------
# Strict flood conditions
# ------------------------------------------------------------

sar_condition = (
    (vv < -1.5)
    &
    (vh < -1.5)
)

ndwi_change_condition = (
    ndwi_change > 0.15
)

post_water_condition = (
    post_ndwi > 0.05
)

pre_nonwater_condition = (
    pre_ndwi < 0.20
)


candidate = (
    valid_mask
    &
    sar_condition
    &
    ndwi_change_condition
    &
    post_water_condition
    &
    pre_nonwater_condition
)


print("\nCondition statistics:")

print(
    "SAR condition:",
    int(
        (
            valid_mask
            & sar_condition
        ).sum()
    )
)

print(
    "NDWI change condition:",
    int(
        (
            valid_mask
            & ndwi_change_condition
        ).sum()
    )
)

print(
    "Post-event water condition:",
    int(
        (
            valid_mask
            & post_water_condition
        ).sum()
    )
)

print(
    "Pre-event non-water condition:",
    int(
        (
            valid_mask
            & pre_nonwater_condition
        ).sum()
    )
)

print(
    "\nV3 raw candidate pixels:",
    int(candidate.sum())
)


# ------------------------------------------------------------
# Connected component filtering
# ------------------------------------------------------------

print(
    "\nRemoving isolated patches..."
)

structure = np.ones(
    (3, 3),
    dtype=np.uint8
)

labels, num_features = ndimage.label(
    candidate,
    structure=structure
)

print(
    "Initial candidate patches:",
    num_features
)


sizes = np.bincount(
    labels.ravel()
)

keep = sizes >= MIN_PATCH_PIXELS

keep[0] = False

filtered = keep[labels].astype(
    np.uint8
)


# ------------------------------------------------------------
# Final statistics
# ------------------------------------------------------------

raw_pixels = int(
    candidate.sum()
)

final_pixels = int(
    filtered.sum()
)

removed = (
    raw_pixels - final_pixels
)

if raw_pixels:
    reduction = (
        removed / raw_pixels
    ) * 100
else:
    reduction = 0.0


remaining_labels = np.unique(
    labels[filtered == 1]
)

remaining_labels = (
    remaining_labels[
        remaining_labels != 0
    ]
)

print()
print(
    "Minimum patch size:",
    MIN_PATCH_PIXELS
)

print(
    "Raw V3 candidate pixels:",
    raw_pixels
)

print(
    "Final V3 pixels:",
    final_pixels
)

print(
    "Removed by patch filtering:",
    removed
)

print(
    "Patch-filter reduction:",
    round(
        reduction,
        2
    ),
    "%"
)

print(
    "Remaining patches:",
    len(remaining_labels)
)


# ------------------------------------------------------------
# Write output
# ------------------------------------------------------------

driver = gdal.GetDriverByName(
    "GTiff"
)

out = driver.Create(
    str(OUTPUT),
    vv_ds.RasterXSize,
    vv_ds.RasterYSize,
    1,
    gdal.GDT_Byte,
    options=[
        "COMPRESS=LZW",
        "TILED=YES"
    ]
)

out.SetGeoTransform(
    vv_ds.GetGeoTransform()
)

out.SetProjection(
    vv_ds.GetProjection()
)

band = out.GetRasterBand(1)

band.WriteArray(
    filtered
)

band.SetNoDataValue(
    255
)

band.SetDescription(
    "Flood candidate V3 - strict SAR + NDWI + spatial filtering"
)

band.FlushCache()

out.FlushCache()

out = None


# ------------------------------------------------------------
# Complete
# ------------------------------------------------------------

print()
print("=" * 70)
print("V3 COMPLETE")
print("=" * 70)

print(
    "Saved:",
    OUTPUT
)

print()
print(
    "V3 is still a modelled flood candidate,"
)

print(
    "not confirmed floodwater."
)

print("=" * 70)