import json
from shapely.geometry import shape, Point
import time
import paho.mqtt.client as mqtt

class Cow:
    def __init__(self, id, movement_pattern):
        self.id =  id
        #Read JSON and extract location points
        with open(movement_pattern, "r") as read_file:
            self.decoded_movement = json.load(read_file)
        self.movement_points = []
        self.movement_coords = self.decoded_movement['features'][0]['geometry']['coordinates']
        for tuple in self.movement_coords:
            self.movement_points.append(Point(tuple[0],tuple[1]))
        #Create Topic for every cow based on its ID
        self.topic = "group4/livestock/cows/" + str(self.id)
        self.topic_escaped = self.topic + "/escaped"
        self.counter = 0

def is_in_pasture(point, fence):
    for feature in fence['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return True
        else:
            return False

def escaped(cow):
    if cow.counter < 3:
        return False
    else:
        return True

def up_cow_counter (cow):
    cow.counter = cow.counter + 1

def reset_cow_counter (cow):
    cow.counter = 0

def check_next_move(cow, i, fence):
    if is_in_pasture(point=cow.movement_points[i+1], fence=fence):
        reset_cow_counter(cow)
    elif is_in_pasture(point=cow.movement_points[i+1], fence=fence) == False:
        up_cow_counter(cow)

def get_longest_movement(list_cows):
    all_coords = []
    for cow in list_cows:
        all_coords.append(cow.movement_points)
    return len(max(all_coords, key=len))

def pub_gps_data(cow, point, check):
    if check:
        msg_txt = "Cow %s \nLon: %s \nLat: %s" % (cow.id, point.x, point.y)
        msg_data_lon = point.x
        msg_data_lat = point.y
    else:
        msg_txt = "No GPS Data for Cow " + str(cow.id)
        msg_data = None
    return msg_txt, msg_data_lon, msg_data_lat

def pub_alarm(cow, point, fence):
    if is_in_pasture(point, fence):
        msg_txt = "Cow %s is in the pasture" % cow.id
        msg_bool = True
        reset_cow_counter(cow)
    elif is_in_pasture(point, fence) is False:
        msg_txt = "Cow %s is NOT in the pasture!" % cow.id
        msg_bool = False
        up_cow_counter(cow)
    else:
        msg_txt = "No Alarm Data for Cow " + str(cow.id)
        msg_bool = None
    return msg_txt, msg_bool

def pub_all(list_cows, fence):
    while True:
        for i in range(get_longest_movement(list_cows)):
            for cow in list_cows:
                if escaped(cow) == False:
                    check = i<len(cow.movement_points)
                    if check:
                        payload_json = create_json_payload(cow, cow.movement_points[i], check, fence)
                        mqtt_client_cow_data.publish(cow.topic,
                                payload=payload_json,
                                qos=0,
                                retain=False)
                    else: 
                        payload_json = create_json_payload(cow, cow.movement_points[i], check, fence)
                        mqtt_client_cow_data.publish(cow.topic,
                                payload=payload_json,
                                qos=0,
                                retain=False)
                elif escaped(cow):
                    mqtt_client_cow_data.publish(topic=cow.topic_escaped,
                                                 payload="Cow %s has escaped!!" % cow.id,
                                                 qos=0,
                                                 retain=False)
                    check_next_move(cow, i, fence)
            time.sleep(3)

def create_json_payload(cow, point, check, fence):
    alarm_txt, alarm_bool = pub_alarm(cow, point, fence)
    gps_txt, gps_data_lon, gps_data_lat = pub_gps_data(cow, point, check)
    send_message = escaped(cow)
    dict_json = {
        "id":cow.id,
        "alarm_txt":alarm_txt,
        "alarm_bool":alarm_bool,
        "gps_txt":gps_txt,
        "gps_data_lon":gps_data_lon,
        "gps_data_lat":gps_data_lat,
        "send_message":send_message
    }
    json_payload = json.dumps(dict_json, indent=4)
    return json_payload

#Definition MQTT Information
mqtt_broker_adr = "wi-vm162-01.rz.fh-ingolstadt.de"
mqtt_broker_port = 1870
#Client Erstellen
mqtt_client_cow_data = mqtt.Client()
#Clients Verbinden
mqtt_client_cow_data.connect(host=mqtt_broker_adr, port=mqtt_broker_port)

#Lesen der Grenzen des virtuellen Zauns
with open("/app/geodata/boundaries_pasture.json", "r") as read_file:
    decoded_boundaries_pasture = json.load(read_file)
                             
cow_1 = Cow(1, "/app/geodata/cow_1_movingpattern.json")
cow_2 = Cow(2, "/app/geodata/cow_2_movingpattern.json")
cow_3 = Cow(3, "/app/geodata/cow_3_movingpattern.json")
cow_4 = Cow(4, "/app/geodata/cow_4_movingpattern.json")
list_cows = [cow_1, cow_2, cow_3, cow_4]
pub_all(list_cows, decoded_boundaries_pasture)