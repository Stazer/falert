from falert.backend.detection import Application

#follow https://developers.google.com/earth-engine/datasets/catalog/FIRMS

import geemap.foliumap as geemap #follow https://pypi.org/project/geemap/

from IPython.display import display
import ee
import folium
import pprint
import webbrowser

ee.Initialize()

Map = geemap.Map()

dataset = ee.ImageCollection('FIRMS').filter(
    ee.Filter.date('2018-08-01', '2018-08-10'));
fires = dataset.select('T21');
firesVis = {
  'min': 325.0,
  'max': 400.0,
  'palette': ['red', 'orange', 'yellow'],
};

Map.setCenter(-119.086, 47.295, 6);
Map.addLayer(fires, firesVis, 'Fires');


Map.save("map.html")
webbrowser.open("map.html")


Application.run()
