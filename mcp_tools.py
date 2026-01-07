from graph import graph_get, buscar_sites_por_nombre

# -------- SITES --------

def buscar_site_por_nombre(nombre: str):
    data = buscar_sites_por_nombre(nombre)
    return data.get("value", [])

# -------- LISTAS --------

def listar_listas(site_id: str):
    return graph_get(f"sites/{site_id}/lists")

def buscar_lista_por_nombre(site_id: str, nombre: str):
    listas = listar_listas(site_id).get("value", [])

    for lista in listas:
        if nombre.lower() in lista["name"].lower():
            return lista

    return None

# -------- ITEMS --------

def leer_items(site_id: str, list_id: str, top: int = 50):
    return graph_get(
        f"sites/{site_id}/lists/{list_id}/items?expand=fields&$top={top}"
    )


#-------------Generar Exel--------------------##
def obtener_registros_sanitarios_top50(site_id, list_id):
    """
    Lee la lista de SharePoint y devuelve datos LIMPIOS
    """

    response = leer_items(site_id, list_id, top=200)

    items = response.get("value", [])

    registros = []

    for item in items:
        fields = item.get("fields", {})

        registro = {
            "Producto": fields.get("Producto"),
            "Principio Activo": fields.get("Principio_x0020_Activo"),
            "Registro Sanitario": fields.get("Registro"),
            "Fabricante": fields.get("Fabricante"),
            "País de Registro": fields.get("Pais_x0020_de_x0020_Registro"),
            "Tipo de Articulo": fields.get("Tipo_x0020_de_x0020_Articulo"),
            "Fecha de Vencimiento": fields.get("Vence"),
            "Dias Para Vencimiento": fields.get("Dias_x0020_Para_x0020_Vencimiento"),
            "Estatus Regulatorio": fields.get("ESTATUS_x0020_REGULATORIO")
        }

        registros.append(registro)

    return registros
