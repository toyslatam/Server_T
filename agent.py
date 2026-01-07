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

        # 👉 CASO 1: el modelo pide usar tools
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

        # 👉 CASO 2: respuesta final (NO tools)
        else:
            return mensaje.content
