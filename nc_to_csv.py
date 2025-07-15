#!/usr/bin/env python3
import netCDF4 as nc
import pandas as pd
import numpy as np

# Replace with your actual NetCDF file path
netcdf_file = 'sst_today.nc'
output_csv = 'sst_data.csv'

# Open the NetCDF file
ds = nc.Dataset(netcdf_file)

# Print variables to help you identify correct names if needed
print("Variables in NetCDF file:", ds.variables.keys())

# Extract variables (update keys if different in your file)
sst = ds.variables['sst'][:]      # shape: [time, lat, lon] or [lat, lon]
lat = ds.variables['lat'][:]
lon = ds.variables['lon'][:]

# Check if sst has time dimension
if len(sst.shape) == 3:
    # Loop through time to flatten all data into rows
    data = []
    for t in range(sst.shape[0]):
        for i in range(len(lat)):
            for j in range(len(lon)):
                data.append([lat[i], lon[j], sst[t, i, j]])
    df = pd.DataFrame(data, columns=['lat', 'lon', 'sst'])
else:
    # 2D SST
    lat_grid, lon_grid = np.meshgrid(lat, lon, indexing='ij')
    df = pd.DataFrame({
        'lat': lat_grid.flatten(),
        'lon': lon_grid.flatten(),
        'sst': sst[:].flatten()
    })

# Optional: Drop NaNs
df.dropna(subset=['sst'], inplace=True)

# Save to CSV
df.to_csv(output_csv, index=False)
print(f"Saved CSV: {output_csv}")
