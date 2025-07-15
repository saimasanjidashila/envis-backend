#!/usr/bin/env python3
import xarray as xr
import pandas as pd
import numpy as np
from pyproj import Proj
import os

FILE_PATH = "ABI-L2-ACMC_2025_001_01_OR_ABI-L2-ACMC-M6_G19_s20250010106173_e20250010108546_c20250010109472.nc"
OUTPUT_CSV = FILE_PATH.replace(".nc", ".csv")

print("Opening:", FILE_PATH)
ds = xr.open_dataset(FILE_PATH)

# Projection info
proj_info = ds['goes_imager_projection']
sat_height = proj_info.perspective_point_height
semi_major = proj_info.semi_major_axis
semi_minor = proj_info.semi_minor_axis
lon_0 = proj_info.longitude_of_projection_origin
sweep = proj_info.sweep_angle_axis

# Setup the projection
p = Proj(proj='geos',
         h=sat_height,
         lon_0=lon_0,
         sweep=sweep,
         a=semi_major,
         b=semi_minor)

# Get x and y coordinates in radians
x = ds['x'].values * sat_height
y = ds['y'].values * sat_height
xx, yy = np.meshgrid(x, y)

# Convert projection to lat/lon
lon, lat = p(xx, yy, inverse=True)

# Select variable (e.g., 'ACM_CLOUD')
var_name = 'ACM'
data = ds[var_name].values

# Flatten arrays
lat_flat = lat.flatten()
lon_flat = lon.flatten()
data_flat = data.flatten()

# Filter out invalid values
valid = np.isfinite(lat_flat) & np.isfinite(lon_flat) & np.isfinite(data_flat)
df = pd.DataFrame({
    "lat": lat_flat[valid],
    "lon": lon_flat[valid],
    var_name: data_flat[valid]
})

# Optional: sample to reduce size for Leaflet rendering
if len(df) > 15000:
    df = df.sample(n=15000, random_state=42)

# Save to CSV
df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved: {OUTPUT_CSV} with {len(df)} records")
