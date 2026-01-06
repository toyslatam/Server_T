from graph import graph_get


def listar_listas(site_id: str):
    return graph_get(f"sites/{site_id}/lists")


def leer_items(site_id: str, list_id: str, top: int = 50):
    return graph_get(
        f"sites/{site_id}/lists/{list_id}/items"
        f"?expand=fields&$top={top}"
    )


def resumen_lista(site_id: str, list_id: str):
    data = leer_items(site_id, list_id, 100)

    total = len(data.get("value", []))
    columnas = list(
        data["value"][0]["fields"].keys()
    ) if total > 0 else []

    return {
        "total_items": total,
        "columnas": columnas
    }
