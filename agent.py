import os
import requests
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MCP_BASE = "https://mcp-tagore.onrender.com"

SYSTEM_PROMPT = """
Eres Argo, un asistente experto en SharePoint.

Reglas:
- Nunca pidas IDs al usuario.
- Si necesitas datos reales, usa las herramientas MCP.
- Explica siempre de forma clara.
"""

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

        # 👉 Si el modelo pide usar una tool
        if mensaje.tool_calls:
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

                mensajes.append({
                    "role": "tool",
                    "tool_call_id": llamada.id,
                    "content": str(resultado)
                })
        else:
            # 👉 Respuesta final al usuario
            return mensaje.content
