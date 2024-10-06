import os
from typing import DefaultDict, List
from collections import defaultdict
from datetime import datetime

from shapely.geometry import Polygon
from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
from skyfield.api import Time, Topos, load
import os


def load_sat_data(filename: str):
    # Load the TLE file
    satFile = load.tle_file(filename)

    # Find Landsat 8 and 9 satellites
    landsat8 = [sat for sat in satFile if "LANDSAT 8" in sat.name][0]
    landsat9 = [sat for sat in satFile if "LANDSAT 9" in sat.name][0]
    return [landsat8, landsat9]


def predict_passover(lat: float, lon: float, start_time: Time, end_time: Time):
    # Load TLE orbital data
    curdir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(curdir, "data/tle.txt")
    satellites = load_sat_data(filename)

    # Holds all the dates
    results: DefaultDict[str, List[str]] = defaultdict(list)

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
                results[sat.name].append(event_time)
                print(f"Event: {sat.name} {event_name} at {event_time}")
    return dict(results)


def get_scene_metadata(
    lat: float, lon: float, start_date: str, end_date: str, cloud_coverage: float = 100
):
    username = "spaceapps43"
    password = "EdBB4#XDQcz@Kr"

    api = API(username, password)

    scenes = api.search(
        dataset="landsat_ot_c2_l2",
        latitude=lat,
        longitude=lon,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover=cloud_coverage,
    )

    if not scenes:
        return None

    results = []
    for scene in scenes:
        print(scene)
        bounds: Polygon = scene["spatial_coverage"]

        results.append(
            {
                "spatial_coverage": list(bounds.exterior.coords),
                "acquisition_date": scene["start_time"].isoformat(),
                "cloud_cover": scene["cloud_cover"],
                "wrs_path": scene["wrs_path"],
                "wrs_row": scene["wrs_path"],
                "land_cloud_cover": scene["land_cloud_cover"],
                "scene_cloud_cover": scene["scene_cloud_cover"],
                "entity_id": scene["entity_id"],
                "display_id": scene["display_id"],
                "satellite": scene["satellite"],
            }
        )
    return results

    # "cloud_cover": 0,
    # "entity_id": "LC80200282024273LGN00",
    # "display_id": "LC08_L2SP_020028_20240929_20241005_02_T1",
    # "ordering_id": "None",
    # "landsat_product_id": "LC08_L1TP_020028_20240929_20241005_02_T1",
    # "landsat_scene_id": "LC80200282024273LGN00",
    # "acquisition_date": datetime(2024, 9, 29, 0, 0),
    # "collection_category": datetime(2024, 10, 1, 0, 0),
    # "collection_number": 2,
    # "wrs_path": 20,
    # "wrs_row": 28,
    # "target_wrs_path": 20,
    # "target_wrs_row": 28,
    # "nadir-off_nadir": "NADIR",
    # "roll_angle": -0.001,
    # "date_product_generated": datetime(2024, 10, 5, 0, 0),
    # "start_time": datetime(2024, 9, 29, 16, 14, 53),
    # "stop_time": datetime(2024, 9, 29, 16, 15, 25),
    # "station_id": "LGN",
    # "day-night_indicator": "DAY",
    # "land_cloud_cover": 0.01,
    # "scene_cloud_cover": 0.01,
    # "ground_control_points_model": 851,
    # "ground_control_points_version": 5,
    # "geometric_rmse_model": 7.438,
    # "geometric_rmse_model_x": 4.982,
    # "geometric_rmse_model_y": 5.523,
    # "processing_software_version": "LPGS_16.4.0",
    # "sun_elevation_l0ra": 39.20054755,
    # "sun_azimuth_l0ra": 159.33949597,
    # "tirs_ssm_model": "FINAL",
    # "data_type": "OLI_TIRS_L2SP",
    # "sensor_id": "OLI_TIRS",
    # "satellite": 8,
    # "product_map_projection": "UTM",
    # "utm_zone": 17,
    # "datum": "WGS84",
    # "ellipsoid": "WGS84",
    # "scene_center_latitude": 46.02948,
    # "scene_center_longitude": -82.15787,
    # "corner_upper_left_latitude": 47.07639,
    # "corner_upper_left_longitude": -83.74122,
    # "corner_upper_right_latitude": 47.10859,
    # "corner_upper_right_longitude": -80.62305,
    # "corner_lower_left_latitude": 44.92139,
    # "corner_lower_left_longitude": -83.63674,
    # "corner_lower_right_latitude": 44.95126,
    # "corner_lower_right_longitude": -80.63743,
    # "has_customized_metadata": None,
    # "options": {"bulk": True, "download": True, "order": False, "secondary": False},
    # "selected": {"bulk": False, "compare": False, "order": False},
    # "spatial_bounds": (-83.65527, 44.9521, -80.62815, 47.09059),
    # "spatial_coverage": "<POLYGON ((-83.655 45.382, -81.298 44.952, -80.628 46.657, -83.058 47.091, -...>",
    # "temporal_coverage": [datetime(2024, 9, 29, 0, 0), datetime(2024, 9, 29, 0, 0)],
    # "publish_date": datetime(2024, 10, 5, 16, 9, 23),


SERVICE_URL = "https://m2m.cr.usgs.gov/api/api/json/development/"

if __name__ == "__main__":
    # Define the latitude and longitude
    lat = 46.00
    lon = -83.00

    end_date = datetime.now()
    start_date = datetime(year=2024, month=9, day=1).strftime("%Y-%m-%d")
    print(get_scene_metadata(lat, lon, start_date, end_date.strftime("%Y-%m-%d")))

    # # Initialize the EarthExplorer instance
    # username = "spaceapps43"
    # password = "EdBB4#XDQcz@Kr"
    # ee = EarthExplorer(username, password)
    # # Download a specific scene by scene's entity_id
    # ee.download("LC90200302024249LGN00", "./scene_out", dataset="landsat_ot_c2_l2")
