// Bursa 2025 Wildfire Project - Step 1
// Pre-fire and post-fire Sentinel-2 RGB visualization + dNBR burn analysis

// Study area focused on the main Bursa 2025 fire corridor:
// Gürsu TOKİ / İpekyolu - Karahıdır - Ağlaşan
var studyArea = ee.Geometry.Rectangle([
  29.235, 40.235,   // west, south
  29.305, 40.295    // east, north
]);

// Alternative smaller test area for Gürsu-Kestel / Ağlaşan-İpekyolu side
// If the large area is too noisy, comment the first studyArea and use this one.
/*
var studyArea = ee.Geometry.Rectangle([
  29.18, 40.12,   // west, south
  29.36, 40.24    // east, north
]);
*/

Map.centerObject(studyArea, 11);
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
// Threshold is experimental. We tried 0.25 first, but it detected very few pixels.
// 0.15 shows more possible burned areas, but it may include false positives.
var burnedArea = dNBR.gt(0.15).selfMask();

Map.addLayer(
  burnedArea,
  {palette: ['red']},
  'Initial Burned Area Mask dNBR > 0.15'
);

// 15. Print dNBR information
print('dNBR image:', dNBR);