# NASA SpaceApps Challenge - `Satelleyes`

Created by Abbie Dewhirst, Mathew Pellarin, Jeremie Bornais, Zain Raza, Jagraj Aulakh, and Wahid Bawa

Satelleyes aims to provide users with a web-based application that allows them to identify when Landsat satellites will pass over a specific location. Users can select a point on the map, either by marking a spot or entering precise longitude and latitude coordinates. The application then provides notifications for upcoming satellite flyovers, making it easy for users to plan ground-based observations in sync with satellite data collection, which can be downloaded in JSON format. By facilitating the comparison of ground-based measurements with Landsat satellite data, our projects addresses the challenge of connecting satellite data with real-world applications. This tool fosters scientific exploration, encourages interdisciplinary learning, and empowers users with valuable spatial information. It is important because it helps researchers, educators and enthusiasts access and utilize remote sensing data for environmental monitoring, resource management, and educational purposes, enhancing their understanding of Earth's surface changes.

## Resources

- [Slides](https://abbiedewhirst.github.io/NASA-Landsat/satelleyes_slides.pdf)
- [Live Demo](https://nasa.matp101.com/)
- [Project Submission Page](https://www.spaceappschallenge.org/nasa-space-apps-2024/find-a-team/reesaholics/?tab=project)
- [Project Wiki](https://github.com/AbbieDewhirst/NASA-Landsat/wiki)

## Requirements
- [X] 1. Allow users to define the target location. Will they specify the place name, latitude and longitude, or select a location on a map?
- [X] 2. Determine when a Landsat satellite is passing over the defined target location.
- [X] 3. Enable users to select the appropriate lead time for notifications about the overpass time and the method of notification.
- [x] 4. Display a 3x3 grid including a total of 9 Landsat pixels centered on the user-defined location (target pixel).
- [x] 5. Determine which Landsat scene contains the target pixel using the Worldwide Reference System-2 (WRS-2) and display the Landsat scene extent on a map.
- [X] 6. Allow users to set a threshold for cloud coverage (e.g., only return data with less than 15% land cloud cover).
- [X] 7. Permit users to specify whether they want access to only the most recent Landsat acquisition or acquisitions spanning a particular time span.
- [X] 8. Acquire scene metadata such as acquisition satellite, date, time, latitude/longitude, Worldwide Reference System path and row, percent cloud cover, and image quality.
- [x] 9. Access and acquire Landsat SR data values (and possibly display the surface temperature data from the thermal infrared bands) for the target pixel by leveraging cloud data catalogs and existing applications.
- [x] 10. Display a graph of the Landsat SR data along the spectrum (i.e., the spectral signature) in addition to scene metadata.
- [X] 11. Allow users to download or share data in a useful format (e.g., csv).

