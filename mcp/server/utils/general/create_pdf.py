import base64
from playwright.sync_api import sync_playwright


def create_pdf(content: str, name: str = "reporte.pdf") -> dict:
    """
    Crea un PDF a partir de HTML usando Playwright y retorna los datos para descarga.
    
    Args:
        content: Contenido HTML para generar el PDF
        name: Nombre del archivo PDF (opcional, default: "reporte.pdf")

    Returns:
        dict: Diccionario con:
            - "success": bool - True si se creó correctamente
            - "pdf_base64": str - Contenido del PDF codificado en base64 (si success=True)
            - "filename": str - Nombre del archivo PDF
            - "mime_type": str - Tipo MIME del archivo (si success=True)
            - "error": str - Mensaje de error (si success=False)
    """
    try:
        with sync_playwright() as p:
            # Usar Chromium para generación de PDF (mejor soporte)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Cargar el contenido HTML
            page.set_content(content, wait_until="networkidle")
            
            # Generar el PDF en bytes
            pdf_bytes = page.pdf(
                format="A4",
                print_background=True,
                margin={
                    "top": "20mm",
                    "bottom": "20mm",
                    "left": "15mm",
                    "right": "15mm"
                }
            )
            
            browser.close()
        
        # Codificar en base64 para transmisión
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return {
            "success": True,
            "pdf_base64": pdf_base64,
            "filename": name,
            "mime_type": "application/pdf"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error al crear el PDF: {str(e)}"
        }