import paho.mqtt.client as mqtt
import random
import time
import json

mqtt_broker = "wi-vm162-01.rz.fh-ingolstadt.de"
mqtt_port = 1870
beleuchtung_topic = "group4/gewächshaus/beleuchtung"
temperatur_topic = "group4/gewächshaus/temperatur"
luftfeuchtigkeit_topic = "group4/gewächshaus/luftfeuchtigkeit"
lueftungssystem_topic = "group4/gewächshaus/lüftungssystem"


client = mqtt.Client()
client.connect(mqtt_broker, mqtt_port, 60)

def temperatur_nachricht(threshold):
    temperature = random.randint(20, 35)  # Simulierte Temperaturdaten zwischen 20 und 35 Grad Celsius

    if temperature > threshold:
        temp_msg = {"temperatur": temperature,
                               "temperatur_notif": "Die Temperatur ist über dem Schwellenwert von %s Grad !" % threshold,
                               "status":True}
        return temp_msg
    else:
        temp_msg = {"temperatur": temperature,
                    "temperatur_notif": "Die Temperatur ist unter dem Schwellenwert von %s Grad !" % threshold,
                    "status":False}
        return temp_msg


def luftfeuchtigkeit_nachricht():
    humidity = random.randint(40, 80)  # Simulierte Luftfeuchtigkeitsdaten zwischen 40 und 80 Prozent
    if humidity > 60:
        humidity_msg = {"luftfeuchtigkeit": humidity,
                        "luftfeuchtigkeit_notif": "Die Luftfeuchtigkeit ist über 60 % !",
                        "status":True}
        return humidity_msg
    else:
        humidity_msg = {"luftfeuchtigkeit": humidity,
                        "luftfeuchtigkeit_notif": "Die Luftfeuchtigkeit ist OK! (<= 60%)",
                        "status":False}
        return humidity_msg

def beleuchtung_nachricht():
    licht = random.randint(0, 1500)  # Simulieren eines Sensorwerts für Lichtintensität
    if licht > 1000:
        beleuchtung_msg = {"licht":licht,
                            "licht_notif": "Lichtintensität zu hoch!"}
        return beleuchtung_msg
    elif licht < 200:
        beleuchtung_msg = {"licht":licht,
                                      "licht_notif": "Lichtintensität zu niedrig!"}
        return beleuchtung_msg
    else:
        beleuchtung_msg = {"licht":licht,
                            "licht_notif": "Lichtintensität im optimalen Bereich!"}
        return beleuchtung_msg


def lueftungssystem_nachricht(temp_msg, humidity_msg):
    # Fälle in denen die Lüftung angeht
    # Zu hohe Temperatur, Zu hohe Feuchte, Beides
    
    get_bool_temp = temp_msg["status"]
    get_bool_humidity = humidity_msg["status"]

    if (get_bool_temp and get_bool_humidity) or (get_bool_humidity or get_bool_temp):
        # Lüftung ein
        lueftung_msg = {"payload": True}
        return lueftung_msg
    else:
        # Lüftung aus
        lueftung_msg = {"payload": False}
        return lueftung_msg
 

    
while True:
    # Schwellenwert für eine Nachricht definieren
    threshold = 28
    temperatur_msg = temperatur_nachricht(threshold)
    luftfeuchtigkeit_msg = luftfeuchtigkeit_nachricht()
    brightness_msg = beleuchtung_nachricht()
    lueftung_notif = lueftungssystem_nachricht(temperatur_msg, luftfeuchtigkeit_msg)


    client.publish(temperatur_topic, json.dumps(temperatur_msg))
    client.publish(luftfeuchtigkeit_topic, json.dumps(luftfeuchtigkeit_msg))
    client.publish(beleuchtung_topic, json.dumps(brightness_msg))
    client.publish(lueftungssystem_topic, json.dumps(lueftung_notif))

    time.sleep(5)
