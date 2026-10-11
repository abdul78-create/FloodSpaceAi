import os
import numpy as np
from osgeo import gdal

processed = r"C:\Users\Abdul\Desktop\FloodSpaceAI\data\processed"

pre_path = os.path.join(
    processed,
    "sentinel1_pre_20260816_vv_vh_filtered.tif"
)

post_path = os.path.join(
    processed,
    "sentinel1_post_20260828_vv_vh_filtered.tif"
)

pre = gdal.Open(pre_path)
post = gdal.Open(post_path)

if pre is None or post is None:
    raise RuntimeError("Could not open filtered Sentinel-1 files.")

pvv = pre.GetRasterBand(1).ReadAsArray().astype(np.float32)
ph = pre.GetRasterBand(2).ReadAsArray().astype(np.float32)

qvv = post.GetRasterBand(1).ReadAsArray().astype(np.float32)
qh = post.GetRasterBand(2).ReadAsArray().astype(np.float32)

valid = (
    np.isfinite(pvv)
    & np.isfinite(ph)
    & np.isfinite(qvv)
    & np.isfinite(qh)
    & (pvv > 0)
    & (ph > 0)
    & (qvv > 0)
    & (qh > 0)
)

vv_db = np.full(pvv.shape, np.nan, dtype=np.float32)
vh_db = np.full(pvv.shape, np.nan, dtype=np.float32)
ratio_db = np.full(pvv.shape, np.nan, dtype=np.float32)

vv_db[valid] = 10.0 * np.log10(qvv[valid] / pvv[valid])
vh_db[valid] = 10.0 * np.log10(qh[valid] / ph[valid])

ratio_db[valid] = 10.0 * np.log10(
    (qvv[valid] / qh[valid])
    / (pvv[valid] / ph[valid])
)

# ---------------------------------------------------------
# WRITE ACTUAL FLOAT32 dB RASTERS
# ---------------------------------------------------------

driver = gdal.GetDriverByName("GTiff")

geotransform = pre.GetGeoTransform()
projection = pre.GetProjection()
rows, cols = pvv.shape


def write_raster(path, array):
    out = driver.Create(
        path,
        cols,
        rows,
        1,
        gdal.GDT_Float32,
        options=["COMPRESS=DEFLATE", "PREDICTOR=3"]
    )

    if out is None:
        raise RuntimeError(f"Could not create output: {path}")

    out.SetGeoTransform(geotransform)
    out.SetProjection(projection)

    band = out.GetRasterBand(1)
    band.SetNoDataValue(-9999.0)

    output_array = np.where(
        np.isfinite(array),
        array,
        -9999.0
    ).astype(np.float32)

    band.WriteArray(output_array)
    band.FlushCache()

    out.FlushCache()
    out = None

    print("WROTE:", path)


write_raster(
    os.path.join(processed, "filtered_vv_change_db.tif"),
    vv_db
)

write_raster(
    os.path.join(processed, "filtered_vh_change_db.tif"),
    vh_db
)

write_raster(
    os.path.join(processed, "filtered_vvvh_ratio_change_db.tif"),
    ratio_db
)

# ---------------------------------------------------------
# STATISTICS
# ---------------------------------------------------------

percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]

print()
print("===== FILTERED SAR CHANGE ANALYSIS =====")

print(
    "VALID PIXELS:",
    int(valid.sum()),
    "/",
    valid.size,
    "=",
    round(100 * valid.mean(), 4),
    "%"
)

print()
print("VV CHANGE dB:")
print(np.nanpercentile(vv_db, percentiles))

print()
print("VH CHANGE dB:")
print(np.nanpercentile(vh_db, percentiles))

print()
print("VV/VH RATIO CHANGE dB:")
print(np.nanpercentile(ratio_db, percentiles))

print()
print("VV CHANGE MEAN:", np.nanmean(vv_db))
print("VV CHANGE MEDIAN:", np.nanmedian(vv_db))

print("VH CHANGE MEAN:", np.nanmean(vh_db))
print("VH CHANGE MEDIAN:", np.nanmedian(vh_db))

print("VV/VH RATIO CHANGE MEAN:", np.nanmean(ratio_db))
print("VV/VH RATIO CHANGE MEDIAN:", np.nanmedian(ratio_db))

print()
print("DONE")