import multiprocessing
import socket
import json
import time
from agente_ia import consultar_agente_ia

# Direcciones IP reales de las computadoras remotas de tus compañeros/laboratorio
WORKERS = [
    ("192.168.1.102", 7001),  # Computadora Remota 1 (Worker 1)
    #("192.168.100.120", 7001), # Computadora Remota 2 (Worker 2)
    ("192.168.1.112", 7001) # Computadora Remota 3 (Worker 3)
]

def productor_pruebas_simultaneas(queue_pedidos):
    print("\n==================================================")
    print("   SERVIDOR CENTRAL (10.20.203.118) ACTIVO        ")
    print("==================================================")
    
    # Ráfaga de pedidos simultáneos para la Fase 3[cite: 32]
    pedidos_prueba = [
        {"id_pedido": 1, "peticion": "Optimizar base de datos masiva con alto tráfico", "carga_nodo": "alta", "distancia_km": 15},
        {"id_pedido": 2, "peticion": "Consultar estado de cuenta simple", "carga_nodo": "normal", "distancia_km": 2},
        {"id_pedido": 3, "peticion": "Falla crítica en pasarela de pagos internacional", "carga_nodo": "alta", "distancia_km": 30},
        {"id_pedido": 4, "peticion": "Actualizar perfil de usuario estándar", "carga_nodo": "normal", "distancia_km": 5},
        {"id_pedido": 5, "peticion": "Alerta de seguridad: posible intrusión en servidor", "carga_nodo": "alta", "distancia_km": 50}
    ]

    print(f"[PRODUCTOR] Lanzando ráfaga de {len(pedidos_prueba)} pedidos simultáneos hacia la red...\n")
    for pedido in pedidos_prueba:
        queue_pedidos.put(pedido)
        print(f"[PRODUCTOR IPC] Pedido #{pedido['id_pedido']} colocado en la cola interna.")
        time.sleep(0.5)

def procesador(queue_entrada, queue_salida):
    while True:
        pedido = queue_entrada.get()
        print(f"[PROCESADOR IPC] Validando pedido ID: {pedido['id_pedido']}")
        pedido["estado"] = "VALIDADO"
        queue_salida.put(pedido)

def gateway_tcp_client(queue_procesados):
    while True:
        pedido = queue_procesados.get()
        print(f"[GATEWAY] Consultando a la IA para el pedido ID: {pedido['id_pedido']}...")
        
        idx_worker = consultar_agente_ia(pedido)
        
        # Validación estricta para evitar IndexError si la IA devuelve un índice inválido
        if idx_worker is None or not isinstance(idx_worker, int) or idx_worker < 0 or idx_worker >= len(WORKERS):
            idx_worker = 0  # Fallback seguro al primer worker
            print("[GATEWAY] Fallback activado: asignando al Worker por defecto (Índice 0)")

        destino = WORKERS[idx_worker]
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Tiempo límite de conexión de 5 segundos para evitar bloqueos si la IP remota no responde
            s.settimeout(5.0)
            s.connect(destino)
            s.send(json.dumps(pedido).encode())
            s.close()
            print(f"[GATEWAY TCP] Paquete #{pedido['id_pedido']} enrutado con éxito al Worker en {destino[0]}:{destino[1]}\n")
        except Exception as e:
            print(f"[ERROR TCP] No se pudo conectar con el worker remoto {destino}: {e}\n")

if __name__ == "__main__":
    cola_generacion = multiprocessing.Queue()
    cola_procesamiento = multiprocessing.Queue()

    proc_procesador = multiprocessing.Process(target=procesador, args=(cola_generacion, cola_procesamiento))
    proc_gateway = multiprocessing.Process(target=gateway_tcp_client, args=(cola_procesamiento,))
    proc_productor = multiprocessing.Process(target=productor_pruebas_simultaneas, args=(cola_generacion,))

    proc_procesador.start()
    proc_gateway.start()
    proc_productor.start()

    try:
        proc_productor.join()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SERVIDOR CENTRAL] Finalizando procesos...")
        proc_productor.terminate()
        proc_procesador.terminate()
        proc_gateway.terminate()