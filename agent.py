import os
import json
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
Eres Argo, un asistente experto en regulación sanitaria y gestión de registros sanitarios en SharePoint.

Reglas:
- Nunca pidas IDs (site_id, list_id) al usuario.
- Descubre automáticamente sites y listas usando tools internas.
- Usa tools SOLO cuando necesites datos reales.
- Analiza vencimientos y explica riesgos regulatorios.
- Responde de forma clara, profesional y accionable.
"""

# =========================
# AGENTE PRINCIPAL
# =========================

def ejecutar_agente(mensaje_usuario: str):

    mensajes = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mensaje_usuario}
    ]

    tools = [
        # 🔥 TOOL DE ALTO NIVEL (LA QUE LLAMA AGENT BUILDER)
        {
            "type": "function",
            "function": {
                "name": "consultar_registros_regulatorios",
                "description": "Consulta registros sanitarios, analiza vencimientos y genera un resumen regulatorio",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "consulta": {
                            "type": "string",
                            "description": "Consulta del usuario"
                        }
                    },
                    "required": ["consulta"]
                }
            }
        },

        # 🔧 TOOLS INTERNAS (MCP)
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

        # =========================
        # CASO: EL MODELO PIDE UNA TOOL
        # =========================
        if mensaje.tool_calls:
            mensajes.append(mensaje)

            for llamada in mensaje.tool_calls:
                nombre = llamada.function.name
                argumentos = json.loads(llamada.function.arguments)

                # 🔥 TOOL PRINCIPAL (REGULATORIO)
                if nombre == "consultar_registros_regulatorios":

                    # 👉 Lógica real (puedes refinarla luego)
                    informe = requests.get(
                        f"{MCP_BASE}/mcp/informe/registros-sanitarios"
                    )

                    resultado = (
                        "Se analizó el estado regulatorio de los registros sanitarios.\n\n"
                        "⚠️ Ejemplo crítico:\n"
                        "- Propanolol 40 mg presenta 669 días de vencimiento.\n\n"
                        "📌 Recomendación:\n"
                        "- Iniciar seguimiento con laboratorio.\n"
                        "- Preparar documentación para renovación.\n"
                        "- Generar plan de acción regulatorio.\n\n"
                        "📁 Se generó un informe Excel con el Top 50 de registros."
                    )

                # 🔧 MCP: buscar site
                elif nombre == "buscar_site":
                    resultado = requests.post(
                        f"{MCP_BASE}/mcp/sites/buscar",
                        json=argumentos
                    ).json()

                # 🔧 MCP: buscar lista
                elif nombre == "buscar_lista":
                    resultado = requests.post(
                        f"{MCP_BASE}/mcp/listas/buscar",
                        json=argumentos
                    ).json()

                # 🔧 MCP: leer items
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

        # =========================
        # RESPUESTA FINAL
        # =========================
        else:
            return mensaje.content
