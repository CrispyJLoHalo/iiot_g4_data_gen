import paho.mqtt.client as mqtt
import random
import time
import json

# Waage
waage_mqtt_broker = "wi-vm162-01.rz.fh-ingolstadt.de"
waage_mqtt_port = 1870
kennzeichen_topic = "group4/feldwirtschaft/sensordaten/waage/kennzeichen"
gewicht_topic = "group4/feldwirtschaft/sensordaten/waage/gewicht"

kennzeichen_prefixes = ['A', 'AN', 'BT', 'CO', 'DEG', 'FFB', 'B', 'IN', 'M', 'REG', 'BN']

waage_client = mqtt.Client()
waage_client.connect(waage_mqtt_broker, waage_mqtt_port, 60)

# Bodentemperatur
bodentemperatur_mqtt_broker = "wi-vm162-01.rz.fh-ingolstadt.de"
bodentemperatur_mqtt_port = 1870
bodentemperatur_topic = "group4/feldwirtschaft/sensordaten/bodentemperatur"

bodentemperatur_client = mqtt.Client()

def generate_sensor_data(min_value, max_value):
    return int(round(random.uniform(min_value, max_value)))

def on_connect(client, userdata, flags, rc):
    print("Verbunden mit dem MQTT-Broker mit dem Resultat: " + str(rc))

bodentemperatur_client.on_connect = on_connect
bodentemperatur_client.connect(bodentemperatur_mqtt_broker, bodentemperatur_mqtt_port, 60)

# pH-Wert
ph_mqtt_broker = "wi-vm162-01.rz.fh-ingolstadt.de"
ph_mqtt_port = 1870
ph_topic = "group4/feldwirtschaft/sensordaten/ph_sensor"

ph_client = mqtt.Client()
ph_client.on_connect = on_connect
ph_client.connect(ph_mqtt_broker, ph_mqtt_port, 60)

# Nitratwerte
nitrat_mqtt_broker = "wi-vm162-01.rz.fh-ingolstadt.de"
nitrat_mqtt_port = 1870
nitrat_topic = "group4/feldwirtschaft/sensordaten/nitratsensor"

nitrat_client = mqtt.Client()
nitrat_client.on_connect = on_connect
nitrat_client.connect(nitrat_mqtt_broker, nitrat_mqtt_port, 60)

last_ph_value = 0
last_nitrat_value = 0
last_bodentemperatur_value = 0

try:
    while True:
        # Waage Daten
        prefix = random.choice(kennzeichen_prefixes)
        buchstaben = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(2))
        kennzeichen = f"{prefix} {buchstaben} {random.randint(1000, 9999)}"
        gewicht = random.randint(40000, 50000)
        waage_client.publish(kennzeichen_topic, json.dumps(kennzeichen))
        waage_client.publish(gewicht_topic, json.dumps(gewicht))
        
        # Bodentemperatur Daten
        min_temp = max(last_bodentemperatur_value - 2, -20)
        max_temp = min(last_bodentemperatur_value + 2, 40)
        sensor_data_bodentemperatur = {f"sensor{sensor_id}": generate_sensor_data(min_temp, max_temp) for sensor_id in range(1, 13)}
        for sensor_id, value in sensor_data_bodentemperatur.items():
            sensor_topic = f"{bodentemperatur_topic}/{sensor_id}"
            bodentemperatur_client.publish(sensor_topic, value)
        last_bodentemperatur_value = list(sensor_data_bodentemperatur.values())[0]
        
        # pH-Wert Daten
        min_ph = max(last_ph_value - 2, 4)
        max_ph = min(last_ph_value + 2, 7)
        sensor_data_ph = {f"sensor{sensor_id}": generate_sensor_data(min_ph, max_ph) for sensor_id in range(1, 13)}
        for sensor_id, value in sensor_data_ph.items():
            sensor_topic = f"{ph_topic}/{sensor_id}"
            ph_client.publish(sensor_topic, value)
        last_ph_value = list(sensor_data_ph.values())[0]
        
        # Nitratwerte Daten
        min_nitrat = max(last_nitrat_value - 10, 20)
        max_nitrat = min(last_nitrat_value + 10, 55)
        sensor_data_nitrat = {f"sensor{sensor_id}": generate_sensor_data(min_nitrat, max_nitrat) for sensor_id in range(1, 13)}
        for sensor_id, value in sensor_data_nitrat.items():
            sensor_topic = f"{nitrat_topic}/{sensor_id}"
            nitrat_client.publish(sensor_topic, value)
        last_nitrat_value = list(sensor_data_nitrat.values())[0]
        
        time.sleep(5)

except KeyboardInterrupt:
    print("Programm wurde beendet.")
    waage_client.disconnect()
    bodentemperatur_client.disconnect()
    ph_client.disconnect()
    nitrat_client.disconnect()
