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


- Landsatxplore: Given lat/lon, we're getting:
    - acquisition_date
    - cloud coverage
    - display_id
    - landsat_product_id
    - wrs_path, wrs_row
    - spatial_coverage (bounding box)
    - AND NOW L1 DATA!!
