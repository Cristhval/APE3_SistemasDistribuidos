import json
import sqlite3
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

# NUEVO: Suscripción dentro de on_connect 
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Suscriptor conectado al broker (rc={rc})")
    client.subscribe("flota/+/gps")
    client.subscribe("flota/+/temperatura")
    client.subscribe("flota/+/combustible")
    print("Suscripción exitosa a los topics de la flota.")

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
        if temp > 4: # Regla PPT diapositiva 8
            print(f"ALERTA: {payload['vehicle_id']} temperatura alta ({temp}°C)")
        cursor.execute("INSERT INTO temp_data (vehicle_id, temperature, unit, timestamp) VALUES (?, ?, ?, ?)",
                       (payload["vehicle_id"], temp, payload["unit"], payload["timestamp"]))
    
    elif "/combustible" in topic:
        fuel = payload["fuel_level"]
        if fuel < 20: # Regla PPT diapositiva 8
            print(f"ALERTA: {payload['vehicle_id']} combustible bajo ({fuel}%)")
        cursor.execute("INSERT INTO fuel_data (vehicle_id, fuel_level, unit, timestamp) VALUES (?, ?, ?, ?)",
                       (payload["vehicle_id"], fuel, payload["unit"], payload["timestamp"]))

    conn.commit()
    conn.close()

def main():
    inicializar_db()
    # Se agrega CallbackAPIVersion.VERSION2
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    
    client.connect(BROKER, PUERTO, 60)
    print("Suscriptor activo. Esperando datos...")
    client.loop_forever()

if __name__ == "__main__":
    main()