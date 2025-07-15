#!/usr/bin/env python3
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

# Load CSV
df = pd.read_csv("predicted_sst_2025_07_01.csv")  # Adjust filename as needed
print("✅ CSV loaded.")

# Columns: lat, lon, sst_pred
lats = df["lat"].values
lons = df["lon"].values
sst_pred = df["pred_sst"].values  # Or adjust column name

# Create a 2D grid
lat_unique = np.sort(df["lat"].unique())
lon_unique = np.sort(df["lon"].unique())
grid = np.full((lat_unique.size, lon_unique.size), np.nan)

# Map values to grid
for _, row in df.iterrows():
    lat_idx = np.where(lat_unique == row["lat"])[0][0]
    lon_idx = np.where(lon_unique == row["lon"])[0][0]
    grid[lat_idx, lon_idx] = row["pred_sst"]

# Load GeoJSON files
coastline = gpd.read_file("data/coastline_simplified.geojson")
landmask = gpd.read_file("data/land_mask_simplified.geojson")
statemask = gpd.read_file("data/state_mask_simplified.geojson")

# Plot
fig, ax = plt.subplots(figsize=(14, 7))

img = ax.imshow(
    grid,
    origin="lower",
    extent=[lon_unique.min(), lon_unique.max(), lat_unique.min(), lat_unique.max()],
    cmap="jet",
    vmin=np.nanmin(grid),
    vmax=np.nanmax(grid)
)

landmask.boundary.plot(ax=ax, color="gray", linewidth=0.5)
coastline.plot(ax=ax, color="black", linewidth=0.7)
statemask.boundary.plot(ax=ax, color="black", linewidth=0.4)

# Hide axes and overlay bounds
ax.set_xlim([-180, 180])
ax.set_ylim([-90, 90])
ax.axis("off")

# Save image
os.makedirs("data", exist_ok=True)
output_path = "data/tomorrow_sst_overlay.png"
plt.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0)
plt.close()

print(f"✅ Image saved at: {output_path}")
