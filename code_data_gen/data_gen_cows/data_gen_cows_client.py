import json
#import shapely
#Vlt noch import requests um Felder & Movement Patterns per HTTP zu managen

class Cow:
    DEFAULT_LAT = 0.
    DEFAULT_LON = 0.
    def __init__(self, id, position_lat=None, position_lon=None, movement_pattern):
        self.id =  id
        self.position_lat = position_lat if position_lat is not None else DEFAULT_LAT
        self.position_lon = position_lon if position_lon is not None else DEFAULT_LON
        self.pattern = movement_pattern #geoJSON File

    def get_cow_location(self):
        return self.position_lat, self.position_lon

'''
TODO Methode die die Position ändert und returned
Festgelegte Bewegungsmuster mit GeoJSOn Lines -> Von position zu position (via Schleife) 
Beispiel Code für Check if in Polygon
import json
from shapely.geometry import shape, Point
# depending on your version, use: from shapely.geometry import shape, Point

# load GeoJSON file containing sectors
with open('sectors.json') as f:
    js = json.load(f)

# construct point based on lon/lat returned by geocoder
point = Point(-122.7924463, 45.4519896)

# check each polygon to see if it contains the point
for feature in js['features']:
    polygon = shape(feature['geometry'])
    if polygon.contains(point):
        print 'Found containing polygon:', feature 
'''

#Lesen des GEOJson Files für die Grenzen und Speicherung in einer Variabel
#Sollte vlt ein Polygon anstatt LineString sein
with open("boundaries_pasture.geojson", "r") as read_file:
    decoded_boundaries_pasture = json.load(read_file)
