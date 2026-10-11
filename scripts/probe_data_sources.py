import json
import os
import sys
import requests

for dll_dir in [r"C:\Program Files\QGIS 3.44.14\bin", r"C:\OSGeo4W\bin"]:
    if os.path.exists(dll_dir):
        try:
            os.add_dll_directory(dll_dir)
        except Exception:
            pass

from osgeo import gdal

gdal.SetConfigOption("AWS_NO_SIGN_REQUEST", "YES")
gdal.SetConfigOption("AWS_REGION", "us-west-2")
gdal.SetConfigOption("GDAL_HTTP_TIMEOUT", "30")

print("=== Testing S1 Access via S3 / HTTPS ===")
s3_path = "/vsis3/sentinel-s1-l1c/GRD/2024/8/31/IW/DV/S1A_IW_GRDH_1SDV_20240831T122235_20240831T122300_055457_06C3C9_AE31/measurement/iw-vv.tiff"
ds_s1 = gdal.Open(s3_path, gdal.GA_ReadOnly)
print("S1 /vsis3/ open result:", ds_s1 is not None)
if ds_s1:
    print("S1 dimensions:", ds_s1.RasterXSize, ds_s1.RasterYSize)
else:
    print("S1 GDAL error:", gdal.GetLastErrorMsg())

# Also test Planetary Computer Sentinel-1 STAC
print("\n=== Testing Microsoft Planetary Computer for S1 ===")
pc_payload = {
    "collections": ["sentinel-1-grd"],
    "bbox": [84.95, 27.80, 85.05, 27.90],
    "datetime": "2024-08-01T00:00:00Z/2024-08-31T23:59:59Z",
    "limit": 2
}
try:
    rpc = requests.post("https://planetarycomputer.microsoft.com/api/stac/v1/search", json=pc_payload, timeout=15)
    print("PC HTTP Status:", rpc.status_code)
    pc_features = rpc.json().get("features", [])
    print(f"PC S1 Found: {len(pc_features)} scenes")
    if pc_features:
        feat = pc_features[0]
        print("PC Scene ID:", feat["id"])
        print("PC Assets:", list(feat.get("assets", {}).keys()))
        vv_href = feat.get("assets", {}).get("vv", {}).get("href")
        print("PC VV href:", vv_href)
        # Sign asset with planetary computer token endpoint
        token_url = f"https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-1-grd"
        rt = requests.get(token_url, timeout=10)
        print("PC Token Status:", rt.status_code)
        if rt.status_code == 200:
            token = rt.json().get("token")
            signed_url = f"{vv_href}?{token}"
            print("Signed URL starts with:", signed_url[:60])
            ds_pc = gdal.Open(f"/vsicurl/{signed_url}", gdal.GA_ReadOnly)
            print("PC GDAL Open result:", ds_pc is not None)
            if ds_pc:
                print("PC S1 dimensions:", ds_pc.RasterXSize, ds_pc.RasterYSize)
except Exception as e:
    print("PC Error:", e)

print("\n=== Testing Historical Overpass with User-Agent ===")
overpass_query = """[out:json][timeout:25][date:"2024-08-01T00:00:00Z"];
(
  way["highway"~"primary|secondary|tertiary|trunk"](27.80,84.95,27.85,85.00);
  way["building"](27.80,84.95,27.82,84.97);
);
out body;
>;
out skel qt;"""

headers = {
    "User-Agent": "FloodSpaceAI-Research/1.0 (floodspace-evaluation; contact: test@floodspace.ai)"
}

eps = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]
for ep in eps:
    print(f"Querying {ep} with custom User-Agent...")
    try:
        r = requests.post(ep, data={"data": overpass_query}, headers=headers, timeout=25)
        print(f"  Status: {r.status_code}, Length: {len(r.content)}")
        if r.status_code == 200:
            d = r.json()
            print(f"  SUCCESS! Elements: {len(d.get('elements', []))}")
            break
    except Exception as e:
        print("  Error:", e)

print("\n=== Testing Ohsome API (Heidelberg University) ===")
# Ohsome API endpoint for historical elements
ohsome_url = "https://api.ohsome.org/v1/elements/geometry"
ohsome_params = {
    "bboxes": "84.95,27.80,85.00,27.85",
    "time": "2024-08-01T00:00:00Z",
    "filter": "highway in (primary, secondary, tertiary, residential, trunk)"
}
try:
    ro = requests.post(ohsome_url, data=ohsome_params, headers=headers, timeout=20)
    print("Ohsome Status:", ro.status_code)
    if ro.status_code == 200:
        od = ro.json()
        print("Ohsome features count:", len(od.get("features", [])))
        print("Ohsome type:", od.get("type"))
except Exception as e:
    print("Ohsome Error:", e)
