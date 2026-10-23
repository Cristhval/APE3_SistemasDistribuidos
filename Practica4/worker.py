import socket
import json
import sys

def worker_servidor(puerto):
    HOST = "0.0.0.0"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permite reutilizar el puerto inmediatamente si se reinicia el script
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, puerto))
    s.listen()

    print(f"[WORKER] Nodo trabajador activo y escuchando en el puerto {puerto}...")

    while True:
        conn, addr = s.accept()
        try:
            data = conn.recv(1024)
            if data:
                decoded = json.loads(data.decode())
                print(f"\n[WORKER {puerto}] Pedido recibido exitosamente desde el Servidor Central:")
                print(json.dumps(decoded, indent=2))
                # Aquí puedes simular la ejecución o procesamiento del pedido en el nodo
        except Exception as e:
            print(f"[ERROR WORKER {puerto}] Fallo al recibir datos: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    # Permite especificar el puerto como argumento al ejecutar el script (ej: python worker.py 7001)
    if len(sys.argv) > 1:
        puerto = int(sys.argv[1])
    else:
        puerto = 7001  # Puerto por defecto
    
    worker_servidor(puerto)