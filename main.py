from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# =========================
# IMPORTS MCP
# =========================

from mcp_tools import (
    buscar_site_por_nombre,
    listar_listas,
    buscar_lista_por_nombre,
    leer_items
)

from agent import ejecutar_agente

from fastapi.responses import FileResponse
from excel_utils import generar_excel_registros
from mcp_tools import obtener_registros_sanitarios_top50

# =========================
# APP
# =========================

app = FastAPI(title="MCP SharePoint Server")

# =========================
# MODELOS (REQUEST)
# =========================

class ListaRequest(BaseModel):
    site_id: str


class ItemsRequest(BaseModel):
    site_id: str
    list_id: str
    top: int | None = 50


class BuscarSiteRequest(BaseModel):
    nombre: str


class BuscarListaRequest(BaseModel):
    site_id: str
    nombre: str


class AgenteRequest(BaseModel):
    mensaje: str


# =========================
# HEALTH CHECK (Render)
# =========================

@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# MCP — SITES
# =========================

@app.post("/mcp/sites/buscar")
def mcp_buscar_site(req: BuscarSiteRequest):
    try:
        return buscar_site_por_nombre(req.nombre)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# MCP — LISTAS
# =========================

@app.post("/mcp/listas")
def mcp_listas(req: ListaRequest):
    try:
        return listar_listas(req.site_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/listas/buscar")
def mcp_buscar_lista(req: BuscarListaRequest):
    try:
        lista = buscar_lista_por_nombre(req.site_id, req.nombre)
        if not lista:
            raise HTTPException(status_code=404, detail="Lista no encontrada")
        return lista
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# MCP — ITEMS
# =========================

@app.post("/mcp/items")
def mcp_items(req: ItemsRequest):
    try:
        return leer_items(req.site_id, req.list_id, req.top)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# WEBHOOKS
# =========================

@app.post("/webhook/quickbooks")
def quickbooks_webhook(payload: dict):
    print("Webhook QuickBooks recibido:", payload)
    return {"ok": True}


# =========================
# AGENTE (CEREBRO)
# =========================

@app.get("/agente")
def agente_get():
    return {
        "status": "OK",
        "mensaje": "El agente está vivo 🚀"
    }


@app.post("/agente")
def agente_post(req: AgenteRequest):
    respuesta = ejecutar_agente(req.mensaje)
    return {"respuesta": respuesta}


# =========================
# UI (STATIC FILES)
# ⚠️ SIEMPRE AL FINAL
# =========================

app.mount(
    "/ui",
    StaticFiles(directory="static", html=True),
    name="ui"
)


@app.post("/mcp/informe/registros-sanitarios")
def generar_informe_excel():
    """
    Genera informe Excel Top 50 de registros sanitarios
    """

    SITE_ID = "5e65fbe9-8adb-408a-95b4-b60f30be1896,09c9fdc9-750f-44cc-9e00-1d98779eca3d"
    LIST_ID = "c0353b87-cc7a-4ccc-9e14-9d328d4d505f"

    datos = obtener_registros_sanitarios_top50(
        site_id=SITE_ID,
        list_id=LIST_ID
    )

    archivo = generar_excel_registros(datos)

    return FileResponse(
        archivo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="Informe_Registros_Sanitarios_Top50.xlsx"
    )
