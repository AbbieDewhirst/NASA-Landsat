# NASA SpaceApps Challenge

## Poetry
- `pip install poetry`
- `poetry install`
- `poetry run python landsat_webapp/app.py`


## Dataset download
We're hosting the dataset on google drive. Download it and extract it in `data/`:

https://drive.google.com/file/d/1FfwMASyE7loSJNDDUXIrMpFD0TXd6dPZ/view?usp=sharing

or

```bash
cd data
wget "https://owncloud.jagrajaulakh.com/s/g9HfAdH1FIwuxTj/download" -O "LC08_L1GT_114213_20241002_20241002_02_RT.tar"
tar -xvf LC08_L1GT_114213_20241002_20241002_02_RT.tar 
```

## Requirements
- [X] 1. Allow users to define the target location. Will they specify the place name, latitude and longitude, or select a location on a map?
- [X] 2. Determine when a Landsat satellite is passing over the defined target location.
- [ ] 3. Enable users to select the appropriate lead time for notifications about the overpass time and the method of notification.
- [ ] 4. Display a 3x3 grid including a total of 9 Landsat pixels centered on the user-defined location (target pixel).
- [ ] 5. Determine which Landsat scene contains the target pixel using the Worldwide Reference System-2 (WRS-2) and display the Landsat scene extent on a map.
- [ ] 6. Allow users to set a threshold for cloud coverage (e.g., only return data with less than 15% land cloud cover).
- [ ] 7. Permit users to specify whether they want access to only the most recent Landsat acquisition or acquisitions spanning a particular time span.
- [ ] 8. Acquire scene metadata such as acquisition satellite, date, time, latitude/longitude, Worldwide Reference System path and row, percent cloud cover, and image quality.
- [ ] 9. Access and acquire Landsat SR data values (and possibly display the surface temperature data from the thermal infrared bands) for the target pixel by leveraging cloud data catalogs and existing applications.
- [ ] 10. Display a graph of the Landsat SR data along the spectrum (i.e., the spectral signature) in addition to scene metadata.
- [ ] 11. Allow users to download or share data in a useful format (e.g., csv).


## Extra Info
- Landsatxplore: Given lat/lon, we're getting:
    - acquisition_date
    - cloud coverage
    - display_id
    - landsat_product_id
    - wrs_path, wrs_row
    - spatial_coverage (bounding box)
    - AND NOW L1 DATA!!