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
Eres Argo, un asistente experto en regulación sanitaria.

Tu función es:
- Analizar registros sanitarios almacenados en SharePoint.
- Identificar productos vencidos o próximos a vencer.
- Explicar riesgos regulatorios.
- Recomendar acciones claras (seguimiento con laboratorios, renovación, alertas).

Reglas:
- NO pidas IDs al usuario.
- Cuando la pregunta implique análisis real, DEBES usar la tool
  consultar_registros_regulatorios.
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
                "name": "consultar_registros_regulatorios",
                "description": "Obtiene registros sanitarios desde SharePoint para análisis regulatorio",
                "parameters": {
                    "type": "object",
                    "properties": {}
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
        # TOOL CALL
        # =========================
        if mensaje.tool_calls:
            mensajes.append(mensaje)

            for llamada in mensaje.tool_calls:

                if llamada.function.name == "consultar_registros_regulatorios":
                    print("Ejecutando tool: consultar_registros_regulatorios")

                    # 🔗 LLAMADA REAL A TU BACKEND MCP
                    response_api = requests.get(
                        f"{MCP_BASE}/mcp/informe/registros-sanitarios"
                    )

                   try:
    data = response_api.json()
except Exception:
    data = {
        "status": "ok",
        "mensaje": "Informe generado, revisar Excel"
    }

mensajes.append({
    "role": "tool",
    "tool_call_id": llamada.id,
    "content": json.dumps({
        "fuente": "SharePoint",
        "registros": data,
        "accion": "Analisis regulatorio ejecutado"
    })
})

        # =========================
        # RESPUESTA FINAL
        # =========================
        else:
            return mensaje.content
