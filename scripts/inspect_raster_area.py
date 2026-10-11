import os
import sys

if hasattr(os, "add_dll_directory"):
    dll_dir = r"C:\Program Files\QGIS 3.44.14\bin"
    if os.path.exists(dll_dir):
        os.add_dll_directory(dll_dir)

from osgeo import gdal, osr
import numpy as np
import math

tif_path = r'data\processed\final_flood_candidate_v3.tif'
ds = gdal.Open(tif_path)
if ds is None:
    print(f"Could not open {tif_path}")
    sys.exit(1)

gt = ds.GetGeoTransform()
srs = ds.GetSpatialRef()
width = ds.RasterXSize
height = ds.RasterYSize
band = ds.GetRasterBand(1)
arr = band.ReadAsArray()
px_count = int(np.sum(arr == 1))

print("=== RASTER INSPECTION ===")
print(f"File: {tif_path}")
print(f"Dimensions: {width} x {height}")
print(f"GeoTransform: {gt}")
print(f"Pixel width (deg or m): {gt[1]}, Pixel height: {gt[5]}")
if srs:
    print(f"Is Geographic (degrees)? {srs.IsGeographic()}")
    print(f"Is Projected (meters)? {srs.IsProjected()}")
    print(f"SRS Name: {srs.GetName()}")
    print(f"Authority code: {srs.GetAuthorityCode(None)}")

print(f"Active flood pixels (value == 1): {px_count}")

# Check exact bounding box
min_x = gt[0]
max_x = gt[0] + width * gt[1]
max_y = gt[3]
min_y = gt[3] + height * gt[5]
print(f"Bounding box: [{min_x}, {min_y}, {max_x}, {max_y}]")

mid_lat = (min_y + max_y) / 2.0
print(f"Center latitude: {mid_lat:.6f} degrees")

# If geographic EPSG:4326:
# Earth radius WGS84:
a = 6378137.0  # semi-major axis
b = 6356752.314245 # semi-minor axis
e2 = 1 - (b**2 / a**2)
lat_rad = math.radians(mid_lat)

# Exact WGS84 meters per degree:
# Length of a degree of latitude:
m_per_deg_lat = (math.pi / 180.0) * a * (1 - e2) / math.pow(1 - e2 * math.sin(lat_rad)**2, 1.5)
# Length of a degree of longitude:
m_per_deg_lon = (math.pi / 180.0) * a * math.cos(lat_rad) / math.sqrt(1 - e2 * math.sin(lat_rad)**2)

dx_m = abs(gt[1]) * m_per_deg_lon
dy_m = abs(gt[5]) * m_per_deg_lat
cell_area_m2 = dx_m * dy_m
total_ha = (px_count * cell_area_m2) / 10000.0

print(f"WGS84 meters per degree at lat {mid_lat:.4f}: lon={m_per_deg_lon:.2f}m, lat={m_per_deg_lat:.2f}m")
print(f"Pixel dimension in meters: {dx_m:.4f} m (width) x {dy_m:.4f} m (height)")
print(f"Pixel area: {cell_area_m2:.4f} m^2")
print(f"Total flood candidate area for {px_count} pixels: {total_ha:.4f} ha ({px_count * cell_area_m2:.2f} m^2)")

# Now check what 10m x 10m gives:
ha_10m = (px_count * 100.0) / 10000.0
print(f"If assumed nominal native 10m x 10m: {ha_10m:.2f} ha")

# Now check what 18.8m x 16.2m was:
print(f"Notice: if dx_m=18.8, dy_m=16.2 -> cell_area = 18.8 * 16.2 = {18.8*16.2:.2f} m^2 -> {px_count * 18.8 * 16.2 / 10000:.2f} ha")
