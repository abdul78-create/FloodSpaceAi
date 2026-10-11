import os
import numpy as np
from osgeo import gdal

raw = r"C:\Users\Abdul\Desktop\FloodSpaceAI\data\raw"
out = r"C:\Users\Abdul\Desktop\FloodSpaceAI\data\processed"

os.makedirs(out, exist_ok=True)

pre_path = os.path.join(raw, "sentinel1_pre_20260816_vv_vh.tif")
post_path = os.path.join(raw, "sentinel1_post_20260828_vv_vh.tif")

pre = gdal.Open(pre_path)
post = gdal.Open(post_path)

if pre is None or post is None:
    raise RuntimeError("Could not open Sentinel-1 input files.")

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
    (qvv[valid] / qh[valid]) /
    (pvv[valid] / ph[valid])
)

gt = pre.GetGeoTransform()
proj = pre.GetProjection()

driver = gdal.GetDriverByName("GTiff")


def save_raster(filename, array, data_type):
    path = os.path.join(out, filename)

    ds = driver.Create(
        path,
        array.shape[1],
        array.shape[0],
        1,
        data_type,
        options=["COMPRESS=DEFLATE"]
    )

    ds.SetGeoTransform(gt)
    ds.SetProjection(proj)

    band = ds.GetRasterBand(1)
    band.WriteArray(array)

    if data_type == gdal.GDT_Float32:
        band.SetNoDataValue(np.nan)
    else:
        band.SetNoDataValue(0)

    ds.FlushCache()
    ds = None

    print("Created:", path)


save_raster("vv_change_db.tif", vv_db, gdal.GDT_Float32)
save_raster("vh_change_db.tif", vh_db, gdal.GDT_Float32)
save_raster(
    "vvvh_ratio_change_db.tif",
    ratio_db,
    gdal.GDT_Float32
)

valid_mask = valid.astype(np.uint8)

save_raster(
    "sar_valid_mask.tif",
    valid_mask,
    gdal.GDT_Byte
)

print()
print("===== SAR CHANGE ANALYSIS =====")
print(
    "VALID PIXELS:",
    int(valid.sum()),
    "/",
    valid.size,
    "=",
    round(100 * valid.mean(), 4),
    "%"
)

percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]

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
print("DONE")