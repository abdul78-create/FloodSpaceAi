import os
import numpy as np
from scipy.ndimage import median_filter
from osgeo import gdal

raw = r"C:\Users\Abdul\Desktop\FloodSpaceAI\data\raw"
out = r"C:\Users\Abdul\Desktop\FloodSpaceAI\data\processed"

os.makedirs(out, exist_ok=True)

files = [
    (
        "sentinel1_pre_20260816_vv_vh.tif",
        "sentinel1_pre_20260816_vv_vh_filtered.tif",
    ),
    (
        "sentinel1_post_20260828_vv_vh.tif",
        "sentinel1_post_20260828_vv_vh_filtered.tif",
    ),
]

driver = gdal.GetDriverByName("GTiff")

for source_name, output_name in files:
    source_path = os.path.join(raw, source_name)
    output_path = os.path.join(out, output_name)

    src = gdal.Open(source_path)

    if src is None:
        raise RuntimeError(f"Could not open: {source_path}")

    output = driver.Create(
        output_path,
        src.RasterXSize,
        src.RasterYSize,
        2,
        gdal.GDT_Float32,
        options=["COMPRESS=DEFLATE"]
    )

    output.SetGeoTransform(src.GetGeoTransform())
    output.SetProjection(src.GetProjection())

    for band_number in [1, 2]:
        array = src.GetRasterBand(band_number).ReadAsArray().astype(np.float32)

        valid = np.isfinite(array) & (array > 0)

        safe = np.where(valid, array, np.nan)

        # Fill invalid pixels temporarily using the median of valid values.
        fallback = np.nanmedian(safe)
        safe = np.where(np.isfinite(safe), safe, fallback)

        # Small 3x3 median filter.
        filtered = median_filter(safe, size=3, mode="nearest")

        # Restore invalid pixels.
        filtered[~valid] = np.nan

        output.GetRasterBand(band_number).WriteArray(filtered)

    output.FlushCache()
    output = None
    src = None

    print("Created:", output_path)

print()
print("DONE")
print("Applied 3x3 median filter to VV and VH.")