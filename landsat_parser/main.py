from datetime import timedelta
import json
from landsatxplore.api import API
from skyfield.api import Topos, load

# Load the TLE file
satellites = load.tle_file("../data/landsat8.tle.txt")

# Find Landsat 8 satellite
landsat8 = [sat for sat in satellites if "LANDSAT 8" in sat.name][0]

print(f"Landsat 8: {landsat8}")

lat = 42.18856439825814
lon = -82.82869985045305
location = Topos(latitude_degrees=lat, longitude_degrees=lon)

# Load timescale
ts = load.timescale()

# Calculate next 10 days
time_now = ts.now()
time_limit = ts.utc(time_now.utc_datetime() + timedelta(days=2))

# Predict passes over the location
t0, events = landsat8.find_events(location, time_now, time_limit, altitude_degrees=30.0)

# Display the next pass details
for ti, event in zip(t0, events):
    event_time = ti.utc_iso()  # ti is a Time object, we call utc_iso() on it
    event_name = ["rise", "culmination", "set"][event]
    print(f"Event: {event_name} at {event_time}")


# Define your EarthExplorer credentials
username = "spaceapps43"
password = "EdBB4#XDQcz@Kr"

# Initialize the EarthExplorer instance
api = API(username, password)

# Define the latitude and longitude
lat = 42.59113799085078
lon = -83.19858770096863

scenes = api.search(
    dataset="landsat_ot_c2_l1",
    latitude=lat,
    longitude=lon,
    start_date="2024-09-01",
    end_date="2024-10-18",
)

print(f"{len(scenes)} found")

for scene in scenes:
    print(scene['acquisition_date'].strftime('%Y-%m-%d'))
    # Write scene footprints to disk
    fname = f"{scene['landsat_product_id']}.geojson"
    with open(fname, "w") as f:
        json.dump(scene['spatial_coverage'].__geo_interface__, f)

