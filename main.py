from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Any, Dict

# =========================
# IMPORTS MCP
# =========================
from mcp_tools import (
    buscar_site_por_nombre,
    listar_listas,
    buscar_lista_por_nombre,
    leer_items,
    obtener_registros_sanitarios_top50
)

from agent import ejecutar_agente
from excel_utils import generar_excel_registros

import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# =========================
# APP (MCP READY)
# =========================
app = FastAPI(
    title="MCP SharePoint Server",
    version="1.0.0",
    openapi_version="3.1.0",
    servers=[
        {
            "url": "https://mcp-tagore.onrender.com",
            "description": "Servidor MCP Tagore"
        }
    ]
)

# =========================
# CORS (OBLIGATORIO PARA MCP)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# MCP — SITES
# =========================
@app.post(
    "/mcp/sites/buscar",
    tags=["mcp"],
    operation_id="buscar_site",
    response_model=Dict[str, Any]
)
def mcp_buscar_site(req: BuscarSiteRequest):
    try:
        return JSONResponse(content=buscar_site_por_nombre(req.nombre))
    except Exception as e:
        raise HTTPException(500, str(e))


# =========================
# MCP — LISTAS
# =========================
@app.post(
    "/mcp/listas",
    tags=["mcp"],
    operation_id="listar_listas",
    response_model=Dict[str, Any]
)
def mcp_listas(req: ListaRequest):
    try:
        return JSONResponse(content=listar_listas(req.site_id))
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post(
    "/mcp/listas/buscar",
    tags=["mcp"],
    operation_id="buscar_lista",
    response_model=Dict[str, Any]
)
def mcp_buscar_lista(req: BuscarListaRequest):
    try:
        lista = buscar_lista_por_nombre(req.site_id, req.nombre)
        if not lista:
            raise HTTPException(404, "Lista no encontrada")
        return JSONResponse(content=lista)
    except Exception as e:
        raise HTTPException(500, str(e))


# =========================
# MCP — ITEMS
# =========================
@app.post(
    "/mcp/items",
    tags=["mcp"],
    operation_id="leer_items",
    response_model=Dict[str, Any]
)
def mcp_items(req: ItemsRequest):
    try:
        return JSONResponse(
            content=leer_items(req.site_id, req.list_id, req.top)
        )
    except Exception as e:
        raise HTTPException(500, str(e))


# =========================
# MCP — INFORME EXCEL
# =========================
@app.get(
    "/mcp/informe/registros-sanitarios",
    tags=["mcp"],
    operation_id="generar_informe_excel",
    response_model=Dict[str, Any]
)
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


# =========================
# AGENTE (NO MCP)
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
# =========================
app.mount(
    "/ui",
    StaticFiles(directory="static", html=True),
    name="ui"
)

#CHAT KIT -----
@app.post("/api/chatkit/session")
def crear_sesion_chatkit():
    """
    Crea una sesión ChatKit entre el navegador y Agent Builder
    """
    session = client.chatkit.sessions.create(
        workflow_id=os.environ["AGENT_WORKFLOW_ID"]
    )

    return {
        "client_secret": session.client_secret,
        "session_id": session.id
    }




