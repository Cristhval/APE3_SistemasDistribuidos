import json
import sqlite3
import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PUERTO = 1883
DB_NAME = "telemetria.db"

def inicializar_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS gps_data 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id TEXT, lat REAL, lng REAL, speed REAL, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS temp_data 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id TEXT, temperature REAL, unit TEXT, timestamp TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS fuel_data 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, vehicle_id TEXT, fuel_level REAL, unit TEXT, timestamp TEXT)''')
    
    conn.commit()
    conn.close()
    print("Base de datos inicializada.")

def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if "/gps" in topic:
        cursor.execute("INSERT INTO gps_data (vehicle_id, lat, lng, speed, timestamp) VALUES (?, ?, ?, ?, ?)",
                       (payload["vehicle_id"], payload["lat"], payload["lng"], payload["speed"], payload["timestamp"]))
    
    elif "/temperatura" in topic:
        temp = payload["temperature"]
        if temp > 4:
            print(f"🚨 ALERTA: {payload['vehicle_id']} temperatura alta ({temp}°C)")
        cursor.execute("INSERT INTO temp_data (vehicle_id, temperature, unit, timestamp) VALUES (?, ?, ?, ?)",
                       (payload["vehicle_id"], temp, payload["unit"], payload["timestamp"]))
    
    elif "/combustible" in topic:
        fuel = payload["fuel_level"]
        if fuel < 20:
            print(f"🚨 ALERTA: {payload['vehicle_id']} combustible bajo ({fuel}%)")
        cursor.execute("INSERT INTO fuel_data (vehicle_id, fuel_level, unit, timestamp) VALUES (?, ?, ?, ?)",
                       (payload["vehicle_id"], fuel, payload["unit"], payload["timestamp"]))

    conn.commit()
    conn.close()

def main():
    inicializar_db()
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PUERTO, 60)
    
    client.subscribe("flota/+/gps")
    client.subscribe("flota/+/temperatura")
    client.subscribe("flota/+/combustible")
    
    print("Suscriptor activo. Escuchando topics flota/+/...")
    client.loop_forever()

if __name__ == "__main__":
    main()