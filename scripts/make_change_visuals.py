import os
import numpy as np
from osgeo import gdal

processed = r"C:\Users\Abdul\Desktop\FloodSpaceAI\data\processed"

layers = [
    ("vv_change_db.tif", "vv_change_db_visual.tif"),
    ("vh_change_db.tif", "vh_change_db_visual.tif"),
    ("vvvh_ratio_change_db.tif", "vvvh_ratio_change_db_visual.tif"),
]

LOW = -6.0
HIGH = 6.0

for source_name, output_name in layers:
    source_path = os.path.join(processed, source_name)
    output_path = os.path.join(processed, output_name)

    src = gdal.Open(source_path)
    array = src.GetRasterBand(1).ReadAsArray().astype(np.float32)

    valid = np.isfinite(array)

    visual = np.zeros(array.shape, dtype=np.uint8)

    clipped = np.clip(array[valid], LOW, HIGH)

    # Map -6 dB -> 0 and +6 dB -> 255.
    visual[valid] = (
        ((clipped - LOW) / (HIGH - LOW)) * 255
    ).astype(np.uint8)

    driver = gdal.GetDriverByName("GTiff")

    dst = driver.Create(
        output_path,
        src.RasterXSize,
        src.RasterYSize,
        1,
        gdal.GDT_Byte,
        options=["COMPRESS=DEFLATE"]
    )

    dst.SetGeoTransform(src.GetGeoTransform())
    dst.SetProjection(src.GetProjection())

    band = dst.GetRasterBand(1)
    band.WriteArray(visual)
    band.SetNoDataValue(0)

    dst.FlushCache()
    dst = None
    src = None

    print("Created:", output_path)

print()
print("DONE")
print("Display range: -6 dB to +6 dB")