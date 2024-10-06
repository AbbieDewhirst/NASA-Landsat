import os
import rasterio
from rasterio.warp import transform


def latlon_to_pixel(dataset, lat, lon):
    tiff_crs = dataset.crs

    # Transform the point coordinates from lon/lat (EPSG:4326) to the CRS of the GeoTIFF
    point_x, point_y = transform("EPSG:4326", tiff_crs, [lon], [lat])

    # Convert to row and column indices
    row, col = dataset.index(point_x[0], point_y[0])
    return row, col


def parse_tiff_pixel(display_id: str, lat: float, lon: float):
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(
        CUR_DIR,
        f"../scene_out/{display_id}/{display_id}_SR_B{{}}.TIF",
    )

    bands_data = []
    rgb_data = [[] for i in range(9)]
    maxes = [0, 0, 0]

    for band in range(1, 8):
        formated_filename = filename.format(band)
        print("Opening", formated_filename)
        with rasterio.open(formated_filename) as dataset:
            # Read the data value at the specific row and column
            row, col = latlon_to_pixel(dataset, lat, lon)
            data_value = dataset.read(1)[row, col]

            print(f"Data value at ({lon}, {lat} -> {row}, {col}): {data_value}")
            bands_data.append(int(data_value))
            # if 2<= band <= 4:
            #     for i in range(3):
            #         for j in range(3):
            #             rgb_data[i*3+j].append(data_value)

    return bands_data


if __name__ == "__main__":
    display_id = "LC09_L2SP_020030_20240905_20240906_02_T1"

    lon, lat = -84.346, 42.679

    print(parse_tiff_pixel(display_id, lat, lon))
