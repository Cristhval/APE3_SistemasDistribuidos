import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")
API_KEY = os.getenv("OPEN_WEBUI_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3-coder:30b")

def consultar_agente_ia(data):
    """
    Envía la petición en lenguaje natural del usuario a qwen3-coder:30b 
    a través de Open WebUI y obtiene tanto la respuesta como la clasificación.
    """
    try:
        texto_peticion = data.get("peticion", str(data))
        
        prompt = f"""
        El usuario ha enviado la siguiente petición o consulta técnica: "{texto_peticion}".
        
        Instrucciones estrictas:
        1. Resuelve, explica o responde detalladamente a lo que el usuario está solicitando.
        2. Debes incluir obligatoriamente en tu respuesta la palabra "CRITICO" o "NORMAL" al inicio para clasificar la prioridad de la tarea.
        """

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }

        response = requests.post(OLLAMA_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        resultado = response.json()
        texto = resultado["choices"][0]["message"]["content"].strip()
        
        print(f"\n==========================================")
        print(f"[RESPUESTA DE LA IA - qwen3-coder:30b]:\n{texto}")
        print(f"==========================================\n")

        # Clasificación para el enrutamiento por sockets TCP
        if "CRITICO" in texto.upper():
            return 0  # Redirige al Worker 7001
        return 1      # Redirige al Worker 7002

    except Exception as e:
        print(f"[AGENTE IA] Error al conectar con Open WebUI: {e}")
        return None