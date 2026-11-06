import json
import paho.mqtt.client as mqtt
import pika
import sys

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
RABBIT_HOST = "localhost"
RABBIT_PORT = 5672

def conectar_rabbitmq():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT))
        channel = connection.channel()
        
        # DECLARAR LAS 3 COLAS DURADERAS 
        channel.queue_declare(queue='cola.gps.telemetria', durable=True)
        channel.queue_declare(queue='cola.alertas.temperatura', durable=True)
        channel.queue_declare(queue='cola.combustible.nivel', durable=True)
        
        print("Conectado a RabbitMQ y 3 colas declaradas.")
        return connection, channel
    except Exception as e:
        print(f"Error conectando a RabbitMQ: {e}")
        sys.exit(1)

def on_message(client, userdata, msg):
    channel = userdata['rabbitmq_channel']
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        return

    # 1. LÓGICA PARA GPS (Todos los mensajes GPS van a su cola)
    if "/gps" in topic:
        channel.basic_publish(
            exchange='',
            routing_key='cola.gps.telemetria',
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"[Bridge] GPS enviado a RabbitMQ: {payload['vehicle_id']}")

    # 2. LÓGICA PARA TEMPERATURA
    elif "/temperatura" in topic:
        if payload.get("temperature", 0) > 4:
            alerta = {"type": "TEMP_ALERT", "message": "Temperatura excedida", **payload}
            channel.basic_publish(
                exchange='',
                routing_key='cola.alertas.temperatura',
                body=json.dumps(alerta),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            print(f"[Bridge] ALERTA enviada a RabbitMQ: {payload['vehicle_id']} - Temp Alta")

    # 3. LÓGICA PARA COMBUSTIBLE
    elif "/combustible" in topic:
        if payload.get("fuel_level", 100) < 20:
            alerta = {"type": "FUEL_LOW", "message": "Combustible bajo", **payload}
            channel.basic_publish(
                exchange='',
                routing_key='cola.combustible.nivel',
                body=json.dumps(alerta),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            print(f"[Bridge] ALERTA enviada a RabbitMQ: {payload['vehicle_id']} - Combustible Bajo")

def main():
    conn_rabbit, channel_rabbit = conectar_rabbitmq()
    
    # Usamos CallbackAPIVersion.VERSION2 para evitar warnings
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata={'rabbitmq_channel': channel_rabbit})
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    client.subscribe("flota/#")
    print("Bridge MQTT-RabbitMQ iniciado. Esperando mensajes...")
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Deteniendo Bridge...")
        client.disconnect()
        conn_rabbit.close()

if __name__ == "__main__":
    main()