import os
import rasterio


def parse_tiff_pixel(filename: str):
    with rasterio.open(filename) as dataset:
        # Get dataset dimensions
        width = dataset.width
        height = dataset.height
        print(f"Width: {width}, Height: {height}")

        # Specify the row and column of the pixel you want to access (x, y coordinates)
        row = 1000  # Row index (y)
        col = 1500  # Column index (x)

        # Read the pixel value at the specific row and column
        pixel_value = dataset.read(1)[row, col]  # '1' here refers to the first band
        print(f"Pixel value at row {row}, col {col}: {pixel_value}")


if __name__ == "__main__":
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(
        CUR_DIR,
        "../scene_out/LC09_L2SP_020030_20240905_20240906_02_T1/LC09_L2SP_020030_20240905_20240906_02_T1_SR_B1.TIF",
    )
    parse_tiff_pixel(filename)
