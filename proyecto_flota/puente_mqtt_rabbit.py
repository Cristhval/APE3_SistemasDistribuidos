import json
import time
import random
import datetime
import paho.mqtt.client as mqtt

# IP de tu laptop principal (el servidor / broker)
BROKER_HOST = "10.20.200.115"
BROKER = BROKER_HOST
PUERTO = 1883

# Etiqueta única que identifica esta laptop
LAPTOP_ORIGEN = "Valverde"

VEHICULOS = ["vehiculo_01", "vehiculo_02", "vehiculo_03"]


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"[{datetime.datetime.now()}] Simulador de {LAPTOP_ORIGEN} conectado (rc={rc})")


def simular_gps():
    return {
        "lat": round(-2.1709 + random.uniform(-0.01, 0.01), 6),
        "lng": round(-79.9224 + random.uniform(-0.01, 0.01), 6),
        "speed": round(random.uniform(20, 80), 1),
    }


def simular_temperatura():
    return {
        "temperature": round(random.uniform(-5, 8), 1),
        "unit": "celsius",
    }


def simular_combustible():
    return {
        "fuel_level": round(random.uniform(10, 100), 1),
        "unit": "percent",
    }


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(BROKER, PUERTO, 60)
    client.loop_start()

    print(f"Iniciando simulador de sensores IoT para [{LAPTOP_ORIGEN}]...")
    try:
        while True:
            for vehiculo in VEHICULOS:
                timestamp = datetime.datetime.now().isoformat()

                # Se incluye la etiqueta de la laptop dentro del JSON también
                datos_gps = {
                    "laptop_origen": LAPTOP_ORIGEN,
                    "vehicle_id": vehiculo,
                    "timestamp": timestamp,
                    **simular_gps()
                }
                client.publish(f"flota/{LAPTOP_ORIGEN}/{vehiculo}/gps", json.dumps(datos_gps), qos=1)

                datos_temp = {
                    "laptop_origen": LAPTOP_ORIGEN,
                    "vehicle_id": vehiculo,
                    "timestamp": timestamp,
                    **simular_temperatura()
                }
                client.publish(f"flota/{LAPTOP_ORIGEN}/{vehiculo}/temperatura", json.dumps(datos_temp), qos=1)

                datos_fuel = {
                    "laptop_origen": LAPTOP_ORIGEN,
                    "vehicle_id": vehiculo,
                    "timestamp": timestamp,
                    **simular_combustible()
                }
                client.publish(f"flota/{LAPTOP_ORIGEN}/{vehiculo}/combustible", json.dumps(datos_fuel), qos=1)

                print(f"[{timestamp}] 3 mensajes publicados por {LAPTOP_ORIGEN} para {vehiculo}")
                time.sleep(5)
    except KeyboardInterrupt:
        print("Deteniendo simulador...")
        client.loop_stop()
        client.disconnect()


if _name_ == "_main_":
    main()