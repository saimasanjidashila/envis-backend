#!/usr/bin/env python3
import geopandas as gpd
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os

# Load SST data
ds = xr.open_dataset("data/sst_today.nc")
sst = ds["sst"].squeeze()

# Convert longitudes from 0–360 → -180–180
lon = (sst.lon + 180) % 360 - 180
sst["lon"] = lon
sst = sst.sortby("lon")

# Extract coordinates and values
lat = sst.lat.values
lon = sst.lon.values
data = sst.values
data = np.where(np.isfinite(data), data, np.nan)

# Load GeoJSON files
coastline = gpd.read_file("data/coastline_simplified.geojson")
landmask = gpd.read_file("data/land_mask_simplified.geojson")
statemask = gpd.read_file("data/state_mask_simplified.geojson")

# Plot
fig, ax = plt.subplots(figsize=(14, 7))
img = ax.imshow(
    data,
    origin="lower",
    extent=[lon.min(), lon.max(), lat.min(), lat.max()],
    cmap="jet",
    vmin=np.nanmin(data),
    vmax=np.nanmax(data)
)
landmask.boundary.plot(ax=ax, color="gray", linewidth=0.5)
coastline.plot(ax=ax, color="black", linewidth=0.7)
statemask.boundary.plot(ax=ax, color="black", linewidth=0.4)

# Overlay bounds
ax.set_xlim([-180, 180])
ax.set_ylim([-90, 90])
ax.axis("off")

# Save image
os.makedirs("data", exist_ok=True)
output_path = "data/sst_today_overlay.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0)
plt.close()

output_path
