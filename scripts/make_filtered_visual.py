import os
import numpy as np
from osgeo import gdal

processed = r"C:\Users\Abdul\Desktop\FloodSpaceAI\data\processed"

source_path = os.path.join(processed, "sentinel1_pre_20260816_vv_vh_filtered.tif")
post_path = os.path.join(processed, "sentinel1_post_20260828_vv_vh_filtered.tif")
output_path = os.path.join(processed, "filtered_vv_change_visual.tif")

pre = gdal.Open(source_path)
post = gdal.Open(post_path)

pvv = pre.GetRasterBand(1).ReadAsArray().astype(np.float32)
qvv = post.GetRasterBand(1).ReadAsArray().astype(np.float32)

valid = (
    np.isfinite(pvv)
    & np.isfinite(qvv)
    & (pvv > 0)
    & (qvv > 0)
)

change = np.full(pvv.shape, np.nan, dtype=np.float32)
change[valid] = 10.0 * np.log10(qvv[valid] / pvv[valid])

LOW = -4.0
HIGH = 4.0

visual = np.zeros(change.shape, dtype=np.uint8)

clipped = np.clip(change[valid], LOW, HIGH)

visual[valid] = (
    ((clipped - LOW) / (HIGH - LOW)) * 255
).astype(np.uint8)

driver = gdal.GetDriverByName("GTiff")

dst = driver.Create(
    output_path,
    pre.RasterXSize,
    pre.RasterYSize,
    1,
    gdal.GDT_Byte,
    options=["COMPRESS=DEFLATE"]
)

dst.SetGeoTransform(pre.GetGeoTransform())
dst.SetProjection(pre.GetProjection())

band = dst.GetRasterBand(1)
band.WriteArray(visual)
band.SetNoDataValue(0)

dst.FlushCache()
dst = None

print("Created:", output_path)
print("Display range: -4 dB to +4 dB")
print("DONE")