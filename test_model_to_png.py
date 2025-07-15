#!/usr/bin/env python3
#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import joblib
import os

# Parse arguments
parser = argparse.ArgumentParser(description="Predict tomorrow SST and generate PNG.")
parser.add_argument("-d", "--date", type=str, required=True, help="Date in YYYY/MM/DD format (e.g., 2025/07/01)")
args = parser.parse_args()

# Extract year, month, day
date_parts = args.date.split("/")
year, month, day = map(int, date_parts)

# Load trained XGBoost model
model = joblib.load("xgboost_sst_model.pkl")
print("✅ Model loaded.")

# Create prediction grid
lats = np.linspace(-89.75, 89.75, 360)    # ~0.5 degree step
lons = np.linspace(-179.75, 179.75, 720)

mesh_lon, mesh_lat = np.meshgrid(lons, lats)
grid_df = pd.DataFrame({
    "year": year,
    "month": month,
    "day": day,
    "lat": mesh_lat.ravel(),
    "lon": mesh_lon.ravel()
})

# Predict
y_pred = model.predict(grid_df)
grid_df["pred_sst"] = y_pred

# Save CSV
csv_filename = f"predicted_sst_{year}_{month:02d}_{day:02d}.csv"
grid_df[["lat", "lon", "pred_sst"]].to_csv(csv_filename, index=False)
print(f"✅ CSV saved: {csv_filename}")

# Convert to pivot table for plotting
sst_grid = grid_df.pivot(index="lat", columns="lon", values="pred_sst")
sst_grid = sst_grid.sort_index(ascending=True)

# Load coastlines and states
coastline = gpd.read_file("geojson/coastline_simplified.geojson")
landmask = gpd.read_file("geojson/land_mask_simplified.geojson")
states = gpd.read_file("geojson/state_mask_simplified.geojson")

# Plot
fig, ax = plt.subplots(figsize=(16, 8))

# Show SST background
im = ax.imshow(
    sst_grid.values,
    cmap="jet",
    extent=[lons.min(), lons.max(), lats.min(), lats.max()],
    origin="lower",
    interpolation="bilinear"
)

# Overlay land and coast
landmask.plot(ax=ax, color="black")
coastline.boundary.plot(ax=ax, color="black", linewidth=0.5)
states.boundary.plot(ax=ax, color="gray", linewidth=0.3)

# Add colorbar and title
cbar = plt.colorbar(im, ax=ax, orientation="vertical", fraction=0.025)
cbar.set_label("Predicted SST (°C)")
ax.set_title(f"Predicted SST for {year}-{month:02d}-{day:02d}")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# Save PNG
png_filename = f"predicted_sst_{year}_{month:02d}_{day:02d}.png"
plt.savefig(png_filename, dpi=300, bbox_inches="tight")
plt.close()
print(f"✅ PNG image saved: {png_filename}")
