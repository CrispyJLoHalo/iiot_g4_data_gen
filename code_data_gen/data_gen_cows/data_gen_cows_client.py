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

def get_longest_movement(list_cows):
    all_coords = []
    for cow in list_cows:
        all_coords.append(cow.movement_points)
    return len(max(all_coords, key=len))

def pub_gps_data(cow, point, check):
    if check:
        msg_txt = "Cow %s \nLon: %s \nLat: %s" % (cow.id, point.y, point.x)
        msg_data = tuple(point.x, point.y)
    else:
        msg_txt = "No GPS Data for Cow " + str(cow.id)
        msg_data = None
    mqtt_client_gps_txt.publish(mqtt_pub_topic_gps,
                            payload=msg_txt,
                            qos=2,
                            retain=False)
    mqtt_client_gps_data.publish(mqtt_pub_topic_gps,
                            payload=msg_data,
                            qos=2,
                            retain=False)
    return msg_txt, msg_data

def pub_alarm(cow, point, fence):
    if is_in_pasture(point, fence):
        msg_txt = "Cow %s is in the pasture" % cow.id
        msg_bool = True
    elif is_in_pasture(point, fence) is False:
        msg_txt = "Cow %s is NOT in the pasture!" % cow.id
        msg_bool = False
    else:
        msg_txt = "No Alarm Data for Cow " + str(cow.id)
        msg_bool = None
    mqtt_client_alarm_txt.publish(mqtt_pub_topic_alarm_txt,
                              payload=msg_txt,
                              qos=2,
                              retain=False)
    mqtt_client_alarm_bool.publish(mqtt_pub_topic_alarm_bool,
                              payload=msg_bool,
                              qos=2,
                              retain=False)
    return msg_txt, msg_bool

def pub_all(list_cows, fence):
    while True:
        for i in range(get_longest_movement(list_cows)):
            for cow in list_cows:
                check = i<len(cow.movement_points)
                if check:
                    pub_alarm(cow, cow.movement_points[i], fence)
                    pub_gps_data(cow, cow.movement_points[i], check)
                    print(create_json_payload(cow, cow.movement_points[i], check, fence))
                else: 
                    pub_alarm(cow, cow.movement_points[i], fence)
                    pub_gps_data(cow, cow.movement_points[i], check)
                    print(create_json_payload(cow, cow.movement_points[i], check, fence))
            time.sleep(5)

#TODO Include JSON Payload in MQTT transmission

def create_json_payload(cow, point, check, fence):
    alarm_txt, alarm_bool = pub_alarm(cow, point, fence)
    gps_txt, gps_data = pub_gps_data(cow, point, check)
    dict_json = {
        "alarm_txt":alarm_txt,
        "alarm_bool":alarm_bool,
        "gps_txt":gps_txt,
        "gps_data":gps_data
    }
    json_payload = json.dumps(dict_json, indent=4)
    return json_payload

#Definition MQTT Information
mqtt_broker_adr = "wi-vm162-01.rz.fh-ingolstadt.de"
mqtt_broker_port = 1870
mqtt_pub_topic_gps = "group4/livestock/gps_data"
mqtt_pub_topic_alarm_txt = "group4/livestock/alarms/txt"
mqtt_pub_topic_alarm_bool = "group4/livestock/alarms/bool"
#Clients Erstellen
mqtt_client_gps_txt = mqtt.Client()
mqtt_client_gps_data = mqtt.Client()
mqtt_client_alarm_txt = mqtt.Client()
mqtt_client_alarm_bool = mqtt.Client()
#Clients Verbinden
mqtt_client_gps_txt.connect(host=mqtt_broker_adr, port=mqtt_broker_port)
mqtt_client_gps_data.connect(host=mqtt_broker_adr, port=mqtt_broker_port)
mqtt_client_alarm_txt.connect(host=mqtt_broker_adr, port=mqtt_broker_port)
mqtt_client_alarm_bool.connect(host=mqtt_broker_adr, port=mqtt_broker_port)


#Lesen der Grenzen des virtuellen Zauns
with open("./code_data_gen/data_gen_cows/geodata/boundaries_pasture.json", "r") as read_file:
    decoded_boundaries_pasture = json.load(read_file)

cow_1 = Cow(1, "code_data_gen\data_gen_cows\geodata\cow_1_movingpattern.json")
cow_2 = Cow(2, "code_data_gen\data_gen_cows\geodata\cow_2_movingpattern.json")
list_cows = [cow_1, cow_2]
pub_all(list_cows, decoded_boundaries_pasture)