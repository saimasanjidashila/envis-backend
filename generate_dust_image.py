#!/usr/bin/env python3
import os
import numpy as np
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt

# Paths
NC_PATH = "MERRA2_400.tavg1_2d_aer_Nx.20250501.nc4"
OUTPUT_IMG = "data/ducmass_overlay.png"
COAST_PATH = "data/coastline_simplified.geojson"
LAND_PATH = "data/land_mask_simplified.geojson"
STATE_PATH = "data/state_mask_simplified.geojson"

# Load dataset and select variable
ds = xr.open_dataset(NC_PATH)
dust = ds["DUCMASS"].isel(time=0).squeeze()  # shape: (lat, lon)

# Convert longitudes from 0–360 → -180–180
lon = (dust.lon + 180) % 360 - 180
dust["lon"] = lon
dust = dust.sortby("lon")

# Mask NaNs or fill values
data = dust.values
data = np.where(np.isfinite(data), data, np.nan)

# Extract coordinates
lat = dust.lat.values
lon = dust.lon.values

# Load GeoJSON masks
coastline = gpd.read_file(COAST_PATH)
landmask = gpd.read_file(LAND_PATH)
statemask = gpd.read_file(STATE_PATH)

# Plot
fig, ax = plt.subplots(figsize=(14, 7))

img = ax.imshow(
    data,
    origin="lower",
    extent=[lon.min(), lon.max(), lat.min(), lat.max()],
    cmap="YlOrRd",
    vmin=np.nanmin(data),
    vmax=np.nanmax(data)
)

landmask.boundary.plot(ax=ax, color="gray", linewidth=0.5)
coastline.plot(ax=ax, color="black", linewidth=0.7)
statemask.boundary.plot(ax=ax, color="black", linewidth=0.4)

ax.set_xlim([-180, 180])
ax.set_ylim([-90, 90])
ax.axis("off")

os.makedirs("data", exist_ok=True)
plt.savefig(OUTPUT_IMG, dpi=600, bbox_inches="tight", pad_inches=0)
plt.close()

print(f"✅ Saved: {OUTPUT_IMG}")
