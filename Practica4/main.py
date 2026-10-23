import multiprocessing
import socket
import json
from agente_ia import consultar_agente_ia

WORKERS = [("127.0.0.1", 7001), ("127.0.0.1", 7002)]

def productor_interactivo(queue_pedidos):
    print("\n==================================================")
    print("   MODO INTERACTIVO - PETICIONES LIBRES A LA IA   ")
    print("==================================================")
    
    contador = 1
    while True:
        try:
            print(f"\n--- NUEVA PETICIÓN [ID: {contador}] ---")
            texto_usuario = input("Escribe tu consulta, código o petición para la IA: ")
            
            if not texto_usuario.strip():
                continue
            
            # Empaqueta tu texto en el mensaje IPC
            pedido = {
                "id_pedido": contador,
                "peticion": texto_usuario
            }

            queue_pedidos.put(pedido)
            print(f"[PRODUCTOR IPC] Petición #{contador} enviada a la cola interna.")
            contador += 1
            
        except EOFError:
            break

def procesador(queue_entrada, queue_salida):
    while True:
        pedido = queue_entrada.get()
        print(f"[PROCESADOR IPC] Extrayendo de la cola el pedido ID: {pedido['id_pedido']}")
        pedido["estado"] = "VALIDADO"
        queue_salida.put(pedido)

def gateway_tcp_client(queue_procesados):
    while True:
        pedido = queue_procesados.get()
        print(f"[GATEWAY] Consultando a qwen3-coder:30b para el pedido ID: {pedido['id_pedido']}...")
        
        # Envía la petición real al modelo mediante Open WebUI
        idx_worker = consultar_agente_ia(pedido)
        
        if idx_worker is None:
            idx_worker = 0
            print("[GATEWAY] Fallback activado: asignando al Worker por defecto (Índice 0)")

        destino = WORKERS[idx_worker]
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(destino)
            s.send(json.dumps(pedido).encode())
            s.close()
            print(f"[GATEWAY TCP] Resultado del pedido #{pedido['id_pedido']} despachado al Worker en {destino}\n")
        except Exception as e:
            print(f"[ERROR TCP] No se pudo conectar con el worker {destino}: {e}\n")

if __name__ == "__main__":
    cola_generacion = multiprocessing.Queue()
    cola_procesamiento = multiprocessing.Queue()

    proc_procesador = multiprocessing.Process(target=procesador, args=(cola_generacion, cola_procesamiento))
    proc_gateway = multiprocessing.Process(target=gateway_tcp_client, args=(cola_procesamiento,))

    proc_procesador.start()
    proc_gateway.start()

    try:
        productor_interactivo(cola_generacion)
    except KeyboardInterrupt:
        print("\n[SERVIDOR CENTRAL] Cerrando procesos...")
        proc_procesador.terminate()
        proc_gateway.terminate()