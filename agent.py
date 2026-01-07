import os
import requests
from openai import OpenAI

# =========================
# OPENAI CLIENT
# =========================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# CONFIG
# =========================

MCP_BASE = "https://mcp-tagore.onrender.com"

SYSTEM_PROMPT = """
Eres Argo, un asistente experto en SharePoint y gestión documental.

Reglas:
- Nunca pidas IDs (site_id, list_id, drive_id) al usuario.
- Descubre automáticamente sites, listas y bibliotecas usando las tools MCP.
- Usa tools solo cuando necesites datos reales.
- Responde de forma clara y profesional.
"""

# =========================
# AGENTE
# =========================

def ejecutar_agente(mensaje_usuario: str):

    mensajes = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mensaje_usuario}
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "buscar_site",
                "description": "Busca sites de SharePoint por nombre",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nombre": {"type": "string"}
                    },
                    "required": ["nombre"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "buscar_lista",
                "description": "Busca una lista dentro de un site",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "nombre": {"type": "string"}
                    },
                    "required": ["site_id", "nombre"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "leer_items",
                "description": "Lee items de una lista",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "site_id": {"type": "string"},
                        "list_id": {"type": "string"},
                        "top": {"type": "integer"}
                    },
                    "required": ["site_id", "list_id"]
                }
            }
        }
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=mensajes,
            tools=tools,
            tool_choice="auto"
        )

        mensaje = response.choices[0].message

        # 🔁 CASO: el modelo pide usar tools
        if mensaje.tool_calls:
            mensajes.append(mensaje)  # MUY IMPORTANTE

            for llamada in mensaje.tool_calls:
                nombre = llamada.function.name
                argumentos = eval(llamada.function.arguments)

                if nombre == "buscar_site":
                    resultado = requests.post(
                        f"{MCP_BASE}/mcp/sites/buscar",
                        json=argumentos
                    ).json()

                elif nombre == "buscar_lista":
                    resultado = requests.post(
                        f"{MCP_BASE}/mcp/listas/buscar",
                        json=argumentos
                    ).json()

                elif nombre == "leer_items":
                    resultado = requests.post(
                        f"{MCP_BASE}/mcp/items",
                        json=argumentos
                    ).json()

                else:
                    resultado = {}

                mensajes.append({
                    "role": "tool",
                    "tool_call_id": llamada.id,
                    "content": str(resultado)
                })

        # ✅ RESPUESTA FINAL
        else:
            return mensaje.content
