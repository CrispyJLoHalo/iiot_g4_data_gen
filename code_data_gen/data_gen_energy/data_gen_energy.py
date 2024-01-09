import time
import random
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json
import datetime

# MQTT Broker Konfiguration
mqtt_broker  = "wi-vm162-01.rz.fh-ingolstadt.de"
mqtt_port  = 1870 

# Beispielhafte realistische Werte für die Biogasanlage
temperature = 35.5
pressure = 2 # bar in Fermenter
Biogas_power_production = 500 # in kWatt (470kW deutschlandweiter durchschnitt)

# Beispielhafte realistische Werte für die PV-Anlage
power_production = 100  # in kWatt
voltage = 230

# Beispielhafte realistische Werte für den Netzbezug
current_consumption = 50 # in Watt


# MQTT Topics
biogas_topic = "group4/energiemanagement/Biogasanlage"
pv_topic = "group4/energiemanagement/PV-Anlage"
buffer_topic = "group4/energiemanagement/Pufferspeicher"
consumption_topic = "group4/energiemanagement/Netzbezug"
mqtt_subscribe_Puffermodus = "group4/energiemanagement/Puffermodus"
mqtt_subscribe_Biogasanlage = "group4/energiemanagement/Biogasanlage"
mqtt_subscribe_PV = "group4/energiemanagement/PV"

# Initialwert für SoC_Pufferspeicher
SoC_Pufferspeicher = 50  # Setze einen Initialwert
# Variable zur Speicherung des aktuellen Befehls (1 für Aufladen, -1 für Entladen, 0 für keine Aktion)
current_command = 0
charging_flag = False  # Flagge, um anzuzeigen, ob das Laden im Gange ist

def decrease_SoC_Pufferspeicher():
    global SoC_Pufferspeicher
    SoC_Pufferspeicher = max(0, SoC_Pufferspeicher - 1)

def charge_SoC_Pufferspeicher():
    global SoC_Pufferspeicher
    SoC_Pufferspeicher = min(100, SoC_Pufferspeicher + 1)


# MQTT-Callback, wenn die Verbindung hergestellt wird
def on_connect(client, userdata, flags, rc):
    # Auf das Eingangsthema abonnieren, wenn die Verbindung hergestellt wird
    client.subscribe(mqtt_subscribe_Puffermodus)

    client.subscribe(mqtt_subscribe_Biogasanlage)
    client.subscribe(mqtt_subscribe_PV)


# MQTT-Callback, wenn eine Nachricht empfangen wird
def on_message(client, userdata, msg):
    global current_command, charging_flag, SoC_Pufferspeicher, Betrieb_Biogasanlage, Betrieb_PV

    # Auswertung der Nachricht
    
    if msg.topic == mqtt_subscribe_Puffermodus:
        if msg.payload.decode() == "1":
            current_command = 1
           
        if msg.payload.decode() == "-1":
            current_command = -1
           
        if msg.payload.decode() == "0":
            current_command = 0
            

    # Verarbeite Nachrichten von Biogasanlage und PV
        
    if msg.topic == mqtt_subscribe_Biogasanlage:
        if msg.payload.decode().lower() == "true":
           Betrieb_Biogasanlage = True
        if msg.payload.decode().lower() == "false":
           Betrieb_Biogasanlage = False

    if msg.topic == mqtt_subscribe_PV:
        if msg.payload.decode().lower() == "true":
            Betrieb_PV = True
        else:
            Betrieb_PV = False



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_broker, mqtt_port, 60)

# Starte die Ereignisschleife des MQTT-Clients
client.loop_start()

Betrieb_Biogasanlage = False
Betrieb_PV = False
biogas_status = "offline"
pv_status = "offline"

while True:
    # Aktualisiere die Werte für die Biogasanlage
    if Betrieb_Biogasanlage == True:
        biogas_status = "online"
        temperature = 35.5
        pressure = 2
        Biogas_power_production = 500 
        temperature += random.uniform(-1, 1)
        pressure += random.uniform(-0.1, 0.1)
        Biogas_power_production += random.uniform(-5, 5)
     
    if Betrieb_Biogasanlage == False:
        biogas_status = "offline"
        Biogas_power_production= 0
        temperature = 0
        pressure = 0

    # Aktualisiere die Werte für die PV-Anlage
    if Betrieb_PV == True:
        pv_status = "online"  
        power_production = 100  # in kWatt
        voltage = 230  
        power_production += random.uniform(-10, 10)
        voltage += random.uniform(-1, 1)

    else:
        pv_status = "offline"
        power_production = 0
        voltage = 0



    # Aktualisiere die Werte für den Netzbezug
    current_consumption += random.uniform(-4, 4)
    current_consumption=max(0, current_consumption)
    Einspeisung_Stromnetz= max(0, round(((Biogas_power_production+power_production)-current_consumption), 2))
    Bezug_Stromnetz= max(0, round((current_consumption-(Biogas_power_production+power_production)), 2))
    Anteil_Strombezug= min(100, round((Bezug_Stromnetz/max(Bezug_Stromnetz, current_consumption))*100, 2))


    if Betrieb_PV == False and Betrieb_Biogasanlage == False:
        Anteil_Eigenbedarf= 100
    else:
        Anteil_Eigenbedarf= round(((current_consumption/(Biogas_power_production+power_production))*100))
        Anteil_Eigenbedarf=max(0, Anteil_Eigenbedarf)

    # Pufferspeicher aktualisieren
    if current_command == 1:
        charge_SoC_Pufferspeicher()
        Anteil_Eigenbedarf= Anteil_Eigenbedarf + 3
        Anteil_Eigenbedarf=min(100, Anteil_Eigenbedarf)
  
    elif current_command == -1:
        decrease_SoC_Pufferspeicher()
        Anteil_Eigenbedarf= Anteil_Eigenbedarf - 3
        Anteil_Eigenbedarf=max(0, Anteil_Eigenbedarf)
    
        
    # Generiere einen Timestamp
    timestamp = datetime.datetime.now().isoformat()


    try:
        publish.single(biogas_topic, payload=json.dumps({"Status Biogasanlage": biogas_status, "Stromerzeugung": round(Biogas_power_production, 2), "Temperatur": round(temperature, 2), "Druck": round(pressure, 2),"Zeitstempel": timestamp}), hostname=mqtt_broker, port=mqtt_port)
        publish.single(pv_topic, payload=json.dumps({"Status PV-Anlage": pv_status, "Stromerzeugung": round(power_production, 2), "Spannung": round(voltage, 2),"Zeitstempel": timestamp}), hostname=mqtt_broker, port=mqtt_port)
        publish.single(buffer_topic, payload=json.dumps({"SoC Pufferspeicher": round(SoC_Pufferspeicher, 2),"Zeitstempel": timestamp}), hostname=mqtt_broker, port=mqtt_port)
        publish.single(consumption_topic, payload=json.dumps({"Aktueller Stromverbrauch": round(current_consumption, 2),"Einspeisung_Stromnetz": Einspeisung_Stromnetz, "Bezug_Stromnetz": Bezug_Stromnetz,"Anteil_Eigenbedarf": Anteil_Eigenbedarf,"Anteil_Strombezug": Anteil_Strombezug,"Zeitstempel": timestamp}), hostname=mqtt_broker, port=mqtt_port)
    except Exception as e:
        print(f"Fehler beim Veröffentlichen auf MQTT: {e}")

    # Hier könnte eine kurze Wartezeit eingefügt werden, bevor die nächsten Daten veröffentlicht werden
    time.sleep(2)
