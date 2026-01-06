from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp_tools import listar_listas, leer_items, resumen_lista

app = FastAPI(title="MCP SharePoint Server")

# -------------------------
# MODELOS
# -------------------------

class ListaRequest(BaseModel):
    site_id: str


class ItemsRequest(BaseModel):
    site_id: str
    list_id: str
    top: int | None = 50


# -------------------------
# HEALTH (Render)
# -------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# -------------------------
# MCP TOOLS
# -------------------------

@app.post("/mcp/listas")
def mcp_listas(req: ListaRequest):
    try:
        return listar_listas(req.site_id)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/mcp/items")
def mcp_items(req: ItemsRequest):
    try:
        return leer_items(req.site_id, req.list_id, req.top)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/mcp/resumen")
def mcp_resumen(req: ItemsRequest):
    try:
        return resumen_lista(req.site_id, req.list_id)
    except Exception as e:
        raise HTTPException(500, str(e))


# -------------------------
# WEBHOOK EJEMPLO
# -------------------------

@app.post("/webhook/quickbooks")
def quickbooks_webhook(payload: dict):
    # aquí procesas eventos
    print("Webhook recibido:", payload)
    return {"ok": True}
