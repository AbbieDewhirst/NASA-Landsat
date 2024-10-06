import json
import requests
import sys
import datetime
import threading
import re
import time

from collections import defaultdict
from datetime import timedelta

from skyfield.iokit import os
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
from skyfield.api import Time, Topos, load


def load_sat_data(filename: str):
    # Load the TLE file
    satFile = load.tle_file(filename)

    # Find Landsat 8 and 9 satellites
    landsat8 = [sat for sat in satFile if "LANDSAT 8" in sat.name][0]
    landsat9 = [sat for sat in satFile if "LANDSAT 9" in sat.name][0]
    return [landsat8, landsat9]


def predict_passover(lat: float, lon: float, start_time: Time, end_time: Time):
    # Holds all the dates
    results = defaultdict(list)

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


SERVICE_URL = "https://m2m.cr.usgs.gov/api/api/json/development/"


if __name__ == "__main__":
    curdir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(curdir, "data/tle.txt")
    satellites = load_sat_data(filename)

    # Define the latitude and longitude
    lat = 42.59113799085078
    lon = -83.19858770096863

    # Define your EarthExplorer credentials
    username = "spaceapps43"
    password = "EdBB4#XDQcz@Kr"

    # Load timescale

    ts = load.timescale()
    # start_time = ts.now()
    # end_time = ts.utc(ts.now().utc_datetime() + timedelta(days=2))
    start_time = ts.utc(ts.now().utc_datetime() - timedelta(days=35))
    end_time = ts.now()

    print(predict_passover(lat, lon, start_time, end_time))

    api = API(username, password)

    scenes = api.search(
        dataset="landsat_ot_c2_l2",
        latitude=lat,
        longitude=lon,
        start_date="2024-09-05",
        end_date="2024-09-06",
        max_cloud_cover=20,
    )

    print(f"{len(scenes)} found")

    for scene in scenes:
        print(scene["acquisition_date"].strftime("%Y-%m-%d"))
        # Write scene footprints to disk
        fname = f"{scene['display_id']}.geojson"
        print(scene)
        # with open(fname, "w") as f:
        #     json.dump(scene["spatial_coverage"].__geo_interface__, f)

    # Initialize the EarthExplorer instance
    ee = EarthExplorer(username, password)
    # Download a specific scene by scene's entity_id
    ee.download("LC90200302024249LGN00", "./scene_out", dataset="landsat_ot_c2_l2")
