import json
from shapely.geometry import shape, Point
import time
import paho.mqtt.client as mqtt

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
            return True
        else:
            return False

def pub_gps_data(cow, point):
    msg = "Cow %s \nLon: %s \nLat: %s" % (cow.id, point.y, point.x)
    mqtt_client_gps.publish(mqtt_pub_topic_gps,
                            payload=msg,
                            qos=2,
                            retain=False)

def pub_alarm(cow, point, fence):
    if is_in_pasture(point, fence):
        msg = "Cow %s is in the pasture" % cow.id
    else:
        msg = "Cow %s is NOT in the pasture!" % cow.id
    mqtt_client_alarm.publish(mqtt_pub_topic_alarm,
                              payload=msg,
                              qos=2,
                              retain=False)

def pub_no_data_alarm(cow):
    msg = "No Alarm Data for Cow " + str(cow.id)
    mqtt_client_alarm.publish(mqtt_pub_topic_alarm,
                              payload=msg,
                              qos=2,
                              retain=False)
    
def pub_no_data_gps(cow):
    msg = "No GPS Data for Cow " + str(cow.id)
    mqtt_client_alarm.publish(mqtt_pub_topic_gps,
                              payload=msg,
                              qos=2,
                              retain=False)

def pub_all(list_cows, fence):
    while True:
        for i in range(get_longest_movement(list_cows)):
            for cow in list_cows:
                if i < len(cow.movement_points):
                    pub_alarm(cow, cow.movement_points[i], fence)
                else: 
                    pub_no_data_alarm(cow)
            for cow in list_cows:
                if i < len(cow.movement_points):
                    pub_gps_data(cow, cow.movement_points[i])
                else:
                    pub_no_data_gps(cow)
            time.sleep(5)

def get_longest_movement(list_cows):
    all_coords = []
    for cow in list_cows:
        all_coords.append(cow.movement_points)
    return len(max(all_coords, key=len))

#Definition MQTT Information
mqtt_broker_adr = "wi-vm162-01.rz.fh-ingolstadt.de"
mqtt_broker_port = 1870
mqtt_pub_topic_gps = "group4/livestock/gps_data"
mqtt_pub_topic_alarm = "group4/livestock/alarms"
#Clients Erstellen
mqtt_client_gps = mqtt.Client()
mqtt_client_alarm = mqtt.Client()
#Clients Verbinden
mqtt_client_gps.connect(host=mqtt_broker_adr, port=mqtt_broker_port)
mqtt_client_alarm.connect(host=mqtt_broker_adr, port=mqtt_broker_port)

#Lesen der Grenzen des virtuellen Zauns
with open("./code_data_gen/data_gen_cows/geodata/boundaries_pasture.json", "r") as read_file:
    decoded_boundaries_pasture = json.load(read_file)

cow_1 = Cow(1, "code_data_gen\data_gen_cows\geodata\cow_1_movingpattern.json")
cow_2 = Cow(2, "code_data_gen\data_gen_cows\geodata\cow_2_movingpattern.json")
list_cows = [cow_1, cow_2]
pub_all(list_cows, decoded_boundaries_pasture)