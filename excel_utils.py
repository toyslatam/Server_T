import pandas as pd
from datetime import datetime

def generar_excel_registros(datos, ruta="informe_registros_sanitarios.xlsx"):
    """
    datos: lista de dicts con campos ya procesados
    """

    df = pd.DataFrame(datos)

    # Ordenar por días para vencimiento (más urgentes primero)
    df = df.sort_values(by="Dias Para Vencimiento")

    # Top 50
    df = df.head(50)

    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Top 50 Vencimientos"
        )

        ws = writer.sheets["Top 50 Vencimientos"]

        # Ajustar ancho de columnas
        for col in ws.columns:
            max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_length + 3

    return ruta
