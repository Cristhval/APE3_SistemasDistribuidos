import json
import time
import random
import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PUERTO = 1883
VEHICULOS = ["VH-001", "VH-002", "VH-003"]

def on_connect(client, userdata, flags, rc):
    print(f"[{datetime.datetime.now()}] Conectado al broker MQTT (rc={rc})")

def simular_gps():
    return {
        "lat": round(-2.1709 + random.uniform(-0.01, 0.01), 6),
        "lng": round(-79.9224 + random.uniform(-0.01, 0.01), 6),
        "speed": round(random.uniform(20, 80), 1)
    }

def simular_temperatura():
    return {
        "temperature": round(random.uniform(-5, 8), 1),
        "unit": "celsius"
    }

def simular_combustible():
    return {
        "fuel_level": round(random.uniform(10, 100), 1),
        "unit": "percent"
    }

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(BROKER, PUERTO, 60)
    client.loop_start()

    print("Iniciando simulador de sensores IoT...")
    try:
        while True:
            for vehiculo in VEHICULOS:
                timestamp = datetime.datetime.now().isoformat()
                
                # GPS
                datos_gps = {"vehicle_id": vehiculo, "timestamp": timestamp, **simular_gps()}
                client.publish(f"flota/{vehiculo}/gps", json.dumps(datos_gps))
                
                # Temperatura
                datos_temp = {"vehicle_id": vehiculo, "timestamp": timestamp, **simular_temperatura()}
                client.publish(f"flota/{vehiculo}/temperatura", json.dumps(datos_temp))
                
                # Combustible
                datos_fuel = {"vehicle_id": vehiculo, "timestamp": timestamp, **simular_combustible()}
                client.publish(f"flota/{vehiculo}/combustible", json.dumps(datos_fuel))
                
                print(f"[{timestamp}] Datos publicados para {vehiculo}")
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("Deteniendo simulador...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()