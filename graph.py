import os
import requests

TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def get_access_token():
    url = TOKEN_URL.format(tenant=os.getenv("TENANT_ID"))

    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "scope": "https://graph.microsoft.com/.default"
    }

    r = requests.post(url, data=data, timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


def graph_get(endpoint: str):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(f"{GRAPH_BASE}/{endpoint}", headers=headers, timeout=15)
    r.raise_for_status()
    return r.json()
