from collections import defaultdict
from datetime import timedelta
import json
from typing import List

from skyfield.iokit import os
from landsatxplore.api import API
from skyfield.api import EarthSatellite, Time, Topos, load
from pprint import pprint

satellites: List[EarthSatellite] = []


def load_sat_data(filename: str) -> True:
    # Load the TLE file
    satFile = load.tle_file(filename)

    # Find Landsat 8 and 9 satellites
    landsat8 = [sat for sat in satFile if "LANDSAT 8" in sat.name][0]
    landsat9 = [sat for sat in satFile if "LANDSAT 9" in sat.name][0]
    satellites.append(landsat8)
    satellites.append(landsat9)
    return True


def predict_passover(lat: float, lon: float, start_time: Time, end_time: Time):
    # Holds all the dates
    results = defaultdict(list)

    print(enumerate(["joe", "mama"]))
    for sat in satellites:
        location = Topos(latitude_degrees=lat, longitude_degrees=lon)

        # Predict passes over the location
        t0, events = sat.find_events(
            location, start_time, end_time, altitude_degrees=80
        )

        # Display the next pass details
        for ti, event in zip(t0, events):
            event_time = ti.utc_iso()  # ti is a Time object, we call utc_iso() on it
            event_name = ["rise", "culmination", "set"][event]
            if event == 0:
                results[sat.name].append([event_time])
            print(f"Event: {sat.name} {event_name} at {event_time}")
    return results


curdir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(curdir, "data/tle.txt")
load_sat_data(filename)

lat = 42.18856439825814
lon = -82.82869985045305

# Load timescale
ts = load.timescale()
# start_time = ts.now()
# end_time = ts.utc(ts.now().utc_datetime() + timedelta(days=2))
start_time = ts.utc(ts.now().utc_datetime() - timedelta(days=35))
end_time = ts.now()

print(predict_passover(lat, lon, start_time, end_time))

# Define your EarthExplorer credentials
username = "spaceapps43"
password = "EdBB4#XDQcz@Kr"

# Initialize the EarthExplorer instance
api = API(username, password)

# Define the latitude and longitude
lat = 42.59113799085078
lon = -83.19858770096863

scenes = api.search(
    dataset="landsat_ot_c2_l2",
    latitude=lat,
    longitude=lon,
    start_date="2024-09-01",
    end_date="2024-10-18",
    max_cloud_cover=20,
)

print(f"{len(scenes)} found")

for scene in scenes:
    print(scene['acquisition_date'].strftime('%Y-%m-%d'))
    # Write scene footprints to disk
    fname = f"{scene['display_id']}.geojson"
    print(scene)
    with open(fname, "w") as f:
        json.dump(scene['spatial_coverage'].__geo_interface__, f)

