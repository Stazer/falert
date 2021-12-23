from falert.backend.analyzing import Application

# follow https://developers.google.com/earth-engine/datasets/catalog/JAXA_ALOS_PALSAR_YEARLY_FNF

import geemap.foliumap as geemap #follow https://pypi.org/project/geemap/

from IPython.display import display
import ee
import folium
import pprint
import webbrowser

ee.Initialize()

Map = geemap.Map()

dataset = ee.ImageCollection('JAXA/ALOS/PALSAR/YEARLY/FNF').filterDate('2017-01-01', '2017-12-31');
forestNonForest = dataset.select('fnf');
forestNonForestVis = {
  'min': 1.0,
  'max': 3.0,
  'palette': ['006400', 'FEFF99', '0000FF'],
};

Map.setCenter(136.85, 37.37, 4);
Map.addLayer(forestNonForest, forestNonForestVis, 'Forest/Non-Forest');

Map.save("map.html")
webbrowser.open("map.html")

Application.run()
