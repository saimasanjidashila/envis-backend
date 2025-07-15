#!/usr/bin/env python3
#!/usr/bin/env python3
import xarray as xr
import rioxarray

# Load SST data
ds = xr.open_dataset("data/sst_today.nc")
sst = ds["sst"].squeeze()

# Fix longitude: convert from 0–360 to -180–180
sst["lon"] = (sst.lon + 180) % 360 - 180
sst = sst.sortby("lon")

# ✅ Flip latitude (make sure it's in increasing order)
if sst.lat.values[0] > sst.lat.values[-1]:
    sst = sst.sortby("lat")  # ascending from -90 → 90

# Assign spatial metadata
sst.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
sst.rio.write_crs("EPSG:4326", inplace=True)

# Save GeoTIFF
sst.rio.to_raster("data/sst.tif")
