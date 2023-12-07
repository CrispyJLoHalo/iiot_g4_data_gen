import json
from shapely.geometry import shape, Point
import time

class Cow:
    def __init__(self, id, movement_pattern):
        self.id =  id
        with open(movement_pattern, "r") as read_file:
            self.decoded_movement = json.load(read_file)
        self.movement_points = []
        self.movement_coords = self.decoded_movement['features'][0]['geometry']['coordinates']
        for tuple in self.movement_coords:
            self.movement_points.append(Point(tuple[0],tuple[1]))

def is_in_pasture(point, fence):
    for feature in fence['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            print('In Pasture!', point)
        else:
            print('Not in pasture!', point)

#Lesen der Grenzen des virtuellen Zauns
with open("./code_data_gen/data_gen_cows/geodata/boundaries_pasture.json", "r") as read_file:
    decoded_boundaries_pasture = json.load(read_file)

cow_1 = Cow(1, "code_data_gen\data_gen_cows\geodata\cow_1_movingpattern.json")

while True:
    for point in cow_1.movement_points:
        is_in_pasture(point, decoded_boundaries_pasture)
        time.sleep(3)
