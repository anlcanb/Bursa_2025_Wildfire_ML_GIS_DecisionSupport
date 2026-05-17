// Bursa 2025 Wildfire Project - Step 1
// Pre-fire and post-fire Sentinel-2 RGB visualization + dNBR burn analysis

// IMPORTANT:
// In the Imports section, you must have two geometry imports:
// 1) burnedArea   = polygons drawn over burned areas
// 2) unburnedArea = polygons drawn over unburned forest areas
//
// Do NOT use the name "burnedArea" for the dNBR mask.
// The dNBR mask is named "burnedMask" below.

// Study area focused on the main Bursa 2025 fire corridor:
// Gürsu TOKİ / İpekyolu - Karahıdır - Ağlaşan
var studyArea = ee.Geometry.Rectangle([
  29.225, 40.225,   // west, south
  29.325, 40.300    // east, north
]);

// Alternative smaller test area for Gürsu-Kestel / Ağlaşan-İpekyolu side
// If the current area is too noisy, comment the first studyArea and use this one.
/*
var studyArea = ee.Geometry.Rectangle([
  29.18, 40.12,   // west, south
  29.36, 40.24    // east, north
]);
*/

Map.centerObject(studyArea, 12);
Map.addLayer(studyArea, {color: 'red'}, 'Study Area - Bursa Gürsu/Kestel');

// 2. Date ranges
var preFireStart = '2025-07-01';
var preFireEnd   = '2025-07-20';

var postFireStart = '2025-07-28';
var postFireEnd   = '2025-08-15';

// 3. Sentinel-2 cloud mask using SCL band
function maskS2clouds(image) {
  var scl = image.select('SCL');

  // Remove cloud shadow, medium/high cloud, thin cirrus, snow
  var mask = scl.neq(3)
                .and(scl.neq(8))
                .and(scl.neq(9))
                .and(scl.neq(10))
                .and(scl.neq(11));

  return image.updateMask(mask)
              .copyProperties(image, ['system:time_start']);
}

// 4. Load Sentinel-2 Surface Reflectance data
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(studyArea)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
  .map(maskS2clouds);

// 5. Create pre-fire image
var preFireCollection = s2
  .filterDate(preFireStart, preFireEnd);

var preFireImage = preFireCollection
  .median()
  .clip(studyArea);

// 6. Create post-fire image
var postFireCollection = s2
  .filterDate(postFireStart, postFireEnd);

var postFireImage = postFireCollection
  .median()
  .clip(studyArea);

// 7. RGB visualization parameters
var rgbVis = {
  bands: ['B4', 'B3', 'B2'],
  min: 0,
  max: 3000,
  gamma: 1.2
};

// 8. Add RGB layers to map
Map.addLayer(
  preFireImage,
  rgbVis,
  'Pre-fire RGB: 2025-07-01 to 2025-07-20'
);

Map.addLayer(
  postFireImage,
  rgbVis,
  'Post-fire RGB: 2025-07-28 to 2025-08-15'
);

// 9. Print image information
print('Pre-fire Sentinel-2 images:', preFireCollection);
print('Post-fire Sentinel-2 images:', postFireCollection);
print('Pre-fire image count:', preFireCollection.size());
print('Post-fire image count:', postFireCollection.size());

// 10. Calculate NBR for pre-fire and post-fire images
// Sentinel-2 NIR = B8, SWIR = B12
var preNBR = preFireImage
  .normalizedDifference(['B8', 'B12'])
  .rename('preNBR');

var postNBR = postFireImage
  .normalizedDifference(['B8', 'B12'])
  .rename('postNBR');

// 11. Calculate dNBR
// Higher positive dNBR usually indicates stronger burn effect
var dNBR = preNBR.subtract(postNBR).rename('dNBR');

// 12. Visualization parameters for dNBR
// Positive dNBR values are emphasized for burn severity inspection
var dNBRVis = {
  min: 0,
  max: 0.5,
  palette: ['white', 'yellow', 'orange', 'red', 'darkred']
};

// 13. Add dNBR layer
Map.addLayer(
  dNBR,
  dNBRVis,
  'dNBR - Burn Severity'
);

// 14. Create initial burned area mask
// Threshold is experimental.
// We tried 0.25 first, but it detected very few pixels.
// 0.15 shows more possible burned areas, but it may include false positives.
//
// IMPORTANT:
// This is only a visual/analysis mask.
// It is NOT the same as the manually drawn burnedArea polygon.
var burnedMask = dNBR.gt(0.15).selfMask();

Map.addLayer(
  burnedMask,
  {palette: ['cyan']},
  'Initial Burned Area Mask dNBR > 0.15'
);

// 15. Print dNBR information
print('dNBR image:', dNBR);

// 16. Display manually drawn training polygons
// burnedArea and unburnedArea must come from the Imports section.
Map.addLayer(
  burnedArea,
  {color: 'red'},
  'Manual Burned Area Polygons'
);

Map.addLayer(
  unburnedArea,
  {color: 'green'},
  'Manual Unburned Area Polygons'
);

// 17. Generate random sample points from burned and unburned polygons

// Burned points: label = 1
var burnedPoints = ee.FeatureCollection.randomPoints({
  region: burnedArea,
  points: 500,
  seed: 42,
  maxError: 10
}).map(function(feature) {
  return feature.set('label', 1);
});

// Unburned points: label = 0
var unburnedPoints = ee.FeatureCollection.randomPoints({
  region: unburnedArea,
  points: 500,
  seed: 84,
  maxError: 10
}).map(function(feature) {
  return feature.set('label', 0);
});

// Merge burned and unburned points
var samplepoints = burnedPoints.merge(unburnedPoints);

// Display sample points
// Burned points are cyan so they are visible over red burned polygons.
Map.addLayer(
  burnedPoints,
  {color: 'cyan'},
  'Burned Points - 500'
);

Map.addLayer(
  unburnedPoints,
  {color: 'blue'},
  'Unburned Points - 500'
);

Map.addLayer(
  samplepoints,
  {color: 'yellow'},
  'Samplepoints - 1000'
);

// Print counts
print('Burned points count:', burnedPoints.size());
print('Unburned points count:', unburnedPoints.size());
print('Total samplepoints count:', samplepoints.size());

// 18. Export samplepoints as shapefile to Google Drive
Export.table.toDrive({
  collection: samplepoints,
  description: 'Bursa_2025_samplepoints',
  folder: 'Bursa_2025_Wildfire_Project',
  fileNamePrefix: 'samplepoints',
  fileFormat: 'SHP'
});

// 19. Export burned points separately as shapefile
Export.table.toDrive({
  collection: burnedPoints,
  description: 'Bursa_2025_burned_points',
  folder: 'Bursa_2025_Wildfire_Project',
  fileNamePrefix: 'burned_points',
  fileFormat: 'SHP'
});

// 20. Export unburned points separately as shapefile
Export.table.toDrive({
  collection: unburnedPoints,
  description: 'Bursa_2025_unburned_points',
  folder: 'Bursa_2025_Wildfire_Project',
  fileNamePrefix: 'unburned_points',
  fileFormat: 'SHP'
});