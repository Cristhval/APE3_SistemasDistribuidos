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
    Módulo independiente de IA: consulta a qwen3-coder:30b vía Open WebUI 
    solicitando una respuesta breve y una clasificación clara.
    """
    try:
        texto_peticion = data.get("peticion", str(data))
        
        # Prompt optimizado para respuestas breves que no saturen la terminal
        prompt = f"""
        Analiza brevemente la siguiente petición: "{texto_peticion}".
        Instrucciones estrictas:
        1. Responde de forma muy concisa y directa (máximo 3 líneas o viñetas cortas).
        2. Incluye obligatoriamente al inicio la palabra CRITICO o NORMAL.
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
        
        print(f"\n------------------------------------------")
        print(f"[RESPUESTA]:\n{texto}")
        print(f"------------------------------------------\n")

        # Criterio de distribución para los workers
        if "CRITICO" in texto.upper():
            return 0  # Enruta al Worker 7001
        return 1      # Enruta al Worker 7002

    except Exception as e:
        print(f"[AGENTE IA] Error al conectar con Open WebUI: {e}")
        return None