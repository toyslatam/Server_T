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
