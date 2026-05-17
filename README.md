# Bursa 2025 Wildfire Susceptibility Mapping with GIS and Machine Learning

This repository contains a GIS and machine learning-based wildfire susceptibility mapping project developed for the 2025 Bursa forest fire area in Türkiye.

The project focuses on the Gürsu–Kestel wildfire corridor, including the Gürsu TOKİ / İpekyolu, Karahıdır, and Ağlaşan surroundings. Satellite imagery, geospatial analysis, sample point generation, machine learning classification, and web-based GIS visualization are used to support wildfire risk assessment and decision-making.

## Project Overview

The main objective of this project is to develop a wildfire susceptibility mapping workflow by integrating remote sensing data, GIS-based environmental variables, and machine learning models.

The system is designed to:

- Analyze pre-fire and post-fire satellite imagery
- Identify burned and unburned areas
- Generate labeled training samples
- Extract wildfire-related spatial features
- Train and compare machine learning classifiers
- Produce a wildfire susceptibility map
- Visualize the results through a web-based GIS interface

## Study Area

The study area is located in Bursa Province, Türkiye, focusing on the 2025 Gürsu–Kestel forest fire region.

The selected area covers the main fire-affected corridor around:

- Gürsu TOKİ / İpekyolu
- Karahıdır
- Ağlaşan
- Surrounding forested areas

The study area was selected based on visible burn patterns in post-fire Sentinel-2 imagery and dNBR-based burn severity analysis.

## Data Sources

The project uses satellite and GIS-based spatial datasets, including:

- Sentinel-2 Surface Reflectance imagery
- Google Earth Engine datasets
- Burned and unburned training sample points
- Terrain and environmental raster layers
- Road, settlement, vegetation, and climate-related spatial variables

Sentinel-2 imagery is processed in Google Earth Engine to generate pre-fire and post-fire RGB composites and burn severity indicators.

## Remote Sensing Workflow

The initial remote sensing workflow includes:

1. Defining the Bursa wildfire study area
2. Loading Sentinel-2 Surface Reflectance imagery
3. Applying cloud masking using the Scene Classification Layer
4. Generating pre-fire and post-fire RGB composites
5. Calculating Normalized Burn Ratio (NBR)
6. Calculating differenced Normalized Burn Ratio (dNBR)
7. Identifying burned areas using dNBR analysis
8. Manually validating burned and unburned sample regions

### Pre-fire Image Period

2025-07-01 to 2025-07-20

### Post-fire Image Period

2025-07-28 to 2025-08-15

## Sample Point Dataset

The project includes a labeled point dataset generated from manually selected burned and unburned polygons.

The sample dataset contains:

- 500 burned points
- 500 unburned points
- 1000 total sample points

### Class Labels

- 1 = Burned
- 0 = Unburned

The sample points are exported as shapefiles:

- burned_points
- unburned_points
- samplepoints

These files are used as the basis for feature extraction and machine learning model training.

## Machine Learning Component

The machine learning part of the project is designed to classify wildfire susceptibility using extracted spatial features.

The planned model comparison includes three classifiers:

- Random Forest
- Support Vector Machine
- Gradient Boosting / XGBoost

The target model performance is at least 75% classification accuracy.

Model evaluation will include:

- Accuracy
- Confusion matrix
- Precision
- Recall
- F1-score
- Comparison between classifiers

The best-performing model will be used to generate the final wildfire susceptibility map.

## Wildfire Susceptibility Features

The project is designed to use 15 wildfire-related spatial features, such as:

- NDVI
- NBR / dNBR
- Elevation
- Slope
- Aspect
- Land cover
- Distance to roads
- Distance to settlements
- Distance to water bodies
- Temperature
- Precipitation
- Wind speed
- Vegetation density
- Soil moisture or drought-related indicators
- Human activity or built-up proximity

These features represent vegetation condition, topography, accessibility, climate, and human influence.

## Web GIS Decision Support System

The final system includes a web-based GIS interface for visualizing wildfire susceptibility results.

The web GIS interface is planned to use:

- Leaflet
- Flask
- HTML / CSS / JavaScript
- GeoJSON and raster map outputs

The interface will allow users to visualize:

- Study area boundary
- Pre-fire satellite image
- Post-fire satellite image
- Burned sample points
- Unburned sample points
- Wildfire susceptibility map
- Risk classes
- Map legend
- Interactive popups
- Layer controls

The purpose of the web interface is to support decision-making for wildfire management, planning, and risk assessment.

## Repository Structure

```text
Bursa_2025_Wildfire_ML_GIS/
│
├── gee/
│   └── bursa_2025_step1_rgb_dnbr.js
│
├── data/
│   ├── burned_points.shp
│   ├── burned_points.shx
│   ├── burned_points.dbf
│   ├── burned_points.prj
│   ├── unburned_points.shp
│   ├── unburned_points.shx
│   ├── unburned_points.dbf
│   ├── unburned_points.prj
│   ├── samplepoints.shp
│   ├── samplepoints.shx
│   ├── samplepoints.dbf
│   └── samplepoints.prj
│
├── models/
│
├── predictions/
│
├── static/
│
├── templates/
│
├── app.py
├── requirements.txt
└── README.md