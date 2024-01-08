import paho.mqtt.client as mqtt
import random
import time
import json

# MQTT Broker Konfiguration
broker_address = "wi-vm162-01.rz.fh-ingolstadt.de"
broker_port = 1870
topic_prefix = "group4/gewaechshaus"

# Funktion zur Generierung simulierter Sensorwerte
def generate_sensor_data():
    temperature = round(random.uniform(20.0, 30.0), 2)  # Temperatur zwischen 20 und 30 Grad Celsius
    soil_moisture_1 = round(random.uniform(30, 70), 2)  # Bodenfeuchtigkeit 1
    soil_moisture_2 = round(random.uniform(30, 70), 2)  # Bodenfeuchtigkeit 2
    humidity_1 = round(random.uniform(40, 80), 2)  # Luftfeuchtigkeit 1
    humidity_2 = round(random.uniform(40, 80), 2)  # Luftfeuchtigkeit 2
    plant_height = round(random.uniform(10, 100), 2)  # Pflanzenhöhe in Zentimetern
    plant_color = {"red": random.randint(0, 255),"green": random.randint(0, 255),"blue": random.randint(0, 255),} # Farbe im RGB Spektrum

    sensor_data = {
        "Temperatur": temperature,
        "Bodenfeuchtigkeit_1": soil_moisture_1,
        "Bodenfeuchtigkeit_2": soil_moisture_2,
        "Luftfeuchtigkeit_1": humidity_1,
        "Luftfeuchtigkeit_2": humidity_2,
        "Pflanzenhöhe": plant_height,
        "Pflanzenfarbe": plant_color,
    }

    return sensor_data

# MQTT Client erstellen
client = mqtt.Client()

# Mit dem Broker verbinden
client.connect(broker_address, broker_port, 60)
client.loop_start()

try:
    while True:
        # Sensorwerte generieren
        sensor_data = generate_sensor_data()

        # Daten in JSON umwandeln
        payload = sensor_data
        payload_farbe = json.dumps(sensor_data["Pflanzenfarbe"])
        # Topics für die verschiedenen Sensoren erstellen
        temperature_topic = f"{topic_prefix}/Temperatur"
        soil_moisture_1_topic = f"{topic_prefix}/Bodenfeuchtigkeit_1"
        soil_moisture_2_topic = f"{topic_prefix}/Bodenfeuchtigkeit_2"
        humidity_1_topic = f"{topic_prefix}/Luftfeuchtigkeit_1"
        humidity_2_topic = f"{topic_prefix}/Luftfeuchtigkeit_2"
        plant_height_topic = f"{topic_prefix}/Pflanzenhöhe"
        plant_color_topic = f"{topic_prefix}/Pflanzenfarbe"

        # Daten über MQTT senden
        client.publish(temperature_topic, payload=payload["Temperatur"])
        client.publish(soil_moisture_1_topic, payload=payload["Bodenfeuchtigkeit_1"])
        client.publish(soil_moisture_2_topic, payload=payload["Bodenfeuchtigkeit_2"])
        client.publish(humidity_1_topic, payload=payload["Luftfeuchtigkeit_1"])
        client.publish(humidity_2_topic, payload=payload["Luftfeuchtigkeit_2"])
        client.publish(plant_height_topic, payload=payload["Pflanzenhöhe"])
        client.publish(plant_color_topic, payload=payload_farbe)

        # Wartezeit zwischen den Messungen
        time.sleep(10)

except KeyboardInterrupt:
    print("Programm durch Benutzer unterbrochen")
    client.disconnect()
    client.loop_stop()