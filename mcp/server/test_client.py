"""
Cliente FastMCP para probar las herramientas del servidor MCP via HTTP
Actualizado para coincidir con las tools definidas en main.py

Uso:
    1. Primero inicia el servidor: python main.py
    2. Luego ejecuta este cliente: python test_client.py
"""
import asyncio
import base64
import sys
import json
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# Configuración del servidor MCP
MCP_SERVER_URL = "http://localhost:8000/mcp"


def create_client():
    """Crea y retorna un cliente FastMCP configurado para HTTP"""
    transport = StreamableHttpTransport(url=MCP_SERVER_URL)
    return Client(transport)


def extract_result(result):
    """Extrae el contenido del resultado de una llamada a tool"""
    if hasattr(result, 'content'):
        content = result.content
        if isinstance(content, list) and len(content) > 0:
            first_content = content[0]
            if hasattr(first_content, 'text'):
                try:
                    return json.loads(first_content.text)
                except json.JSONDecodeError:
                    return first_content.text
        elif hasattr(content, 'text'):
            try:
                return json.loads(content.text)
            except json.JSONDecodeError:
                return content.text
    elif hasattr(result, 'text'):
        try:
            return json.loads(result.text)
        except json.JSONDecodeError:
            return result.text
    elif isinstance(result, dict):
        return result
    return result


async def list_tools(client):
    """Lista todas las herramientas disponibles"""
    tools = await client.list_tools()
    tools_list = tools if isinstance(tools, list) else getattr(tools, 'tools', tools)
    return tools_list


# =============================================================================
# TESTS GENERALES
# =============================================================================

async def test_ping():
    """Prueba la herramienta ping (health check)"""
    client = create_client()
    
    print("\n" + "=" * 60)
    print("TEST: Ping (Health Check)")
    print("=" * 60)
    print("\nConectando al servidor MCP...")
    
    async with client:
        print("Conectado al servidor MCP")
        print(f"Servidor: {client.initialize_result.serverInfo.name if client.initialize_result else 'N/A'}\n")
        
        print("Ejecutando tool: ping")
        print("-" * 50)
        
        result = await client.call_tool("ping", {})
        data = extract_result(result)
        
        print(f"Respuesta: {data}")
        print("-" * 50)
        print("Test completado")


async def test_create_pdf():
    """Prueba la herramienta create_pdf usando el cliente FastMCP"""
    client = create_client()
    
    print("\n" + "=" * 60)
    print("TEST: Crear PDF desde HTML")
    print("=" * 60)
    print("\nConectando al servidor MCP...")
    
    async with client:
        print("Conectado al servidor MCP")
        print(f"Servidor: {client.initialize_result.serverInfo.name if client.initialize_result else 'N/A'}\n")
        
        # HTML de prueba para generar el PDF
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reporte de Prueba</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .header {
                    background-color: #3498db;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px;
                }
                .content {
                    background-color: white;
                    padding: 20px;
                    margin-top: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }
                th {
                    background-color: #3498db;
                    color: white;
                }
                tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                .footer {
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                    font-size: 12px;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Reporte de Prueba - MCP Server</h1>
                <p>Generado con Playwright</p>
            </div>
            
            <div class="content">
                <h2>Informacion del Documento</h2>
                <p>Este es un documento PDF generado automaticamente usando <strong>Playwright</strong> 
                   desde el servidor MCP.</p>
                
                <h3>Datos de Ejemplo</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Estado</th>
                        <th>Fecha</th>
                    </tr>
                    <tr>
                        <td>001</td>
                        <td>Proyecto Alpha</td>
                        <td>Completado</td>
                        <td>2026-01-15</td>
                    </tr>
                    <tr>
                        <td>002</td>
                        <td>Proyecto Beta</td>
                        <td>En Progreso</td>
                        <td>2026-01-20</td>
                    </tr>
                    <tr>
                        <td>003</td>
                        <td>Proyecto Gamma</td>
                        <td>Pendiente</td>
                        <td>2026-01-25</td>
                    </tr>
                </table>
            </div>
            
            <div class="footer">
                <p>Documento generado automaticamente - MCP Server IA UNP</p>
            </div>
        </body>
        </html>
        """
        
        print("Ejecutando tool: create_pdf")
        print("-" * 50)
        
        result = await client.call_tool("create_pdf", {
            "html": html_content,
            "filename": "reporte_prueba.pdf"
        })
        
        data = extract_result(result)
        
        if data and isinstance(data, dict):
            if data.get("success"):
                print("PDF generado exitosamente!")
                print(f"   Filename: {data.get('filename')}")
                print(f"   MIME Type: {data.get('mime_type')}")
                
                pdf_base64 = data.get("pdf_base64")
                if pdf_base64:
                    pdf_bytes = base64.b64decode(pdf_base64)
                    output_path = Path("output_test.pdf")
                    output_path.write_bytes(pdf_bytes)
                    print(f"   PDF guardado en: {output_path.absolute()}")
                    print(f"   Tamano: {len(pdf_bytes)} bytes")
            else:
                print(f"Error al generar PDF: {data.get('error')}")
        else:
            print(f"Respuesta: {data}")
        
        print("-" * 50)
        print("Test completado")


async def test_send_email():
    """Prueba la herramienta send_email_report (sin PDF)"""
    client = create_client()
    
    print("\n" + "=" * 60)
    print("TEST: Enviar correo electronico (sin PDF)")
    print("=" * 60)
    
    # Solicitar datos al usuario
    print("\nIngrese los datos del correo:")
    email = input("   Correo destino: ").strip()
    if not email:
        print("Error: El correo es requerido")
        return
    
    subject = input("   Asunto (Enter para default): ").strip()
    if not subject:
        subject = "Prueba desde MCP Client"
    
    message = input("   Mensaje (Enter para default): ").strip()
    if not message:
        message = "Este es un correo de prueba enviado desde el cliente MCP.\n\nSaludos!"
    
    print("\nConectando al servidor MCP...")
    
    async with client:
        print("Conectado al servidor MCP")
        
        print("\nEjecutando tool: send_email_report")
        print("-" * 50)
        
        result = await client.call_tool("send_email_report", {
            "email": email,
            "subject": subject,
            "message": message
        })
        
        data = extract_result(result)
        
        if data and isinstance(data, dict):
            if data.get("success"):
                print("Correo enviado exitosamente!")
            else:
                print(f"Error al enviar el correo: {data.get('error', 'Error desconocido')}")
        else:
            print(f"Respuesta: {data}")
        
        print("-" * 50)
        print("Test completado")


async def test_send_email_with_pdf():
    """Prueba enviar correo con PDF adjunto"""
    client = create_client()
    
    print("\n" + "=" * 60)
    print("TEST: Enviar correo electronico con PDF adjunto")
    print("=" * 60)
    
    # Solicitar datos al usuario
    print("\nIngrese los datos del correo:")
    email = input("   Correo destino: ").strip()
    if not email:
        print("Error: El correo es requerido")
        return
    
    subject = input("   Asunto (Enter para default): ").strip()
    if not subject:
        subject = "Reporte con PDF - MCP Test"
    
    message = input("   Mensaje (Enter para default): ").strip()
    if not message:
        message = "Adjunto encontraras el reporte generado automaticamente."
    
    pdf_name = input("   Nombre del PDF (Enter para 'reporte.pdf'): ").strip()
    if not pdf_name:
        pdf_name = "reporte.pdf"
    
    # HTML para el PDF adjunto
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Reporte Adjunto</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            h1 { color: #3498db; text-align: center; }
            .info { 
                background: #f0f0f0; 
                padding: 15px; 
                border-radius: 8px;
                margin: 20px 0;
            }
            .footer {
                text-align: center;
                color: #666;
                font-size: 12px;
                margin-top: 30px;
            }
        </style>
    </head>
    <body>
        <h1>Reporte Generado Automaticamente</h1>
        <div class="info">
            <p><strong>Fecha de generacion:</strong> 2026-01-30</p>
            <p><strong>Estado:</strong> Completado</p>
            <p><strong>Descripcion:</strong> Este PDF fue generado y enviado por correo desde el servidor MCP.</p>
        </div>
        <div class="footer">
            <p>MCP Server IA - Universidad Nacional de Piura</p>
        </div>
    </body>
    </html>
    """
    
    print("\nConectando al servidor MCP...")
    
    async with client:
        print("Conectado al servidor MCP")
        
        print("\nEjecutando tool: send_email_report (con PDF)")
        print("-" * 50)
        
        result = await client.call_tool("send_email_report", {
            "email": email,
            "subject": subject,
            "message": message,
            "content_pdf": html_content,
            "name_pdf": pdf_name
        })
        
        data = extract_result(result)
        
        if data and isinstance(data, dict):
            if data.get("success"):
                print("Correo con PDF enviado exitosamente!")
            else:
                print(f"Error al enviar el correo: {data.get('error', 'Error desconocido')}")
        else:
            print(f"Respuesta: {data}")
        
        print("-" * 50)
        print("Test completado")


async def test_web_spider():
    """Prueba la herramienta web_spider para buscar palabras clave en URLs"""
    client = create_client()
    
    print("\n" + "=" * 60)
    print("TEST: Web Spider - Busqueda en Prensa")
    print("=" * 60)
    
    # Solicitar datos al usuario
    print("\nIngrese los datos para la busqueda:")
    
    urls_input = input("   URLs a analizar (separadas por coma): ").strip()
    if not urls_input:
        # URLs de ejemplo por defecto
        urls = ["https://www.python.org", "https://docs.python.org"]
        print(f"   Usando URLs de ejemplo: {urls}")
    else:
        urls = [url.strip() for url in urls_input.split(",")]
    
    keywords_input = input("   Palabras clave a buscar (separadas por coma): ").strip()
    if not keywords_input:
        keywords = ["python", "programming"]
        print(f"   Usando palabras clave de ejemplo: {keywords}")
    else:
        keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
        print(f"   Buscando: {keywords}")
    
    deep_search_input = input("   Busqueda profunda? (s/n, default=s): ").strip().lower()
    deep_search = deep_search_input != 'n'
    print(f"   Busqueda profunda: {'Si' if deep_search else 'No'}")
    
    max_links_input = input("   Max enlaces por pagina (Enter = sin limite): ").strip()
    if max_links_input:
        try:
            max_links = int(max_links_input)
        except ValueError:
            max_links = None
            print("   Valor invalido, usando sin limite")
    else:
        max_links = None
        print("   Usando sin limite de enlaces")
    
    # Parametros de fecha
    print("\n   --- Filtro de Fechas ---")
    months_input = input("   Meses hacia atras (default=6): ").strip()
    if months_input:
        try:
            months_back = int(months_input)
        except ValueError:
            months_back = 6
            print("   Valor invalido, usando 6 meses")
    else:
        months_back = 6
        print("   Usando ultimos 6 meses")
    
    date_from_input = input("   Fecha desde (YYYY-MM-DD, Enter=auto): ").strip()
    date_from = date_from_input if date_from_input else None
    
    date_to_input = input("   Fecha hasta (YYYY-MM-DD, Enter=hoy): ").strip()
    date_to = date_to_input if date_to_input else None
    
    print("\nConectando al servidor MCP...")
    
    async with client:
        print("Conectado al servidor MCP")
        print(f"Servidor: {client.initialize_result.serverInfo.name if client.initialize_result else 'N/A'}\n")
        
        print("Ejecutando tool: web_spider")
        print(f"   URLs: {urls}")
        print(f"   Keywords: {keywords}")
        print(f"   Deep search: {deep_search}")
        print(f"   Max links: {'Sin limite' if max_links is None else max_links}")
        print(f"   Meses atras: {months_back}")
        print(f"   Fecha desde: {date_from or 'auto (hace ' + str(months_back) + ' meses)'}")
        print(f"   Fecha hasta: {date_to or 'hoy'}")
        print("-" * 50)
        
        # Construir parametros
        tool_params = {
            "urls": urls,
            "keywords": keywords,
            "deep_search": deep_search,
            "months_back": months_back
        }
        if max_links is not None:
            tool_params["max_links_per_page"] = max_links
        if date_from:
            tool_params["date_from"] = date_from
        if date_to:
            tool_params["date_to"] = date_to
        
        result = await client.call_tool("web_spider", tool_params)
        
        data = extract_result(result)
        
        if data and isinstance(data, dict):
            if data.get("success"):
                print("\nBusqueda completada!")
                
                # Date range info
                date_range = data.get("date_range", {})
                print(f"\n   Rango de fechas: {date_range.get('from', 'N/A')} a {date_range.get('to', 'N/A')}")
                
                # Summary
                summary = data.get("summary", {})
                print(f"\n   {'='*55}")
                print(f"   RESUMEN")
                print(f"   {'='*55}")
                print(f"   Keywords buscadas: {summary.get('keywords_searched', keywords)}")
                print(f"   Rango fechas: {summary.get('date_from', 'N/A')} - {summary.get('date_to', 'N/A')}")
                print(f"   Paginas analizadas: {summary.get('total_source_pages', 0)}")
                print(f"   URLs con coincidencias: {summary.get('total_matching_urls', 0)}")
                print(f"   URLs filtradas por fecha: {summary.get('urls_filtered_by_date', 0)}")
                
                # Matching URLs
                matching = data.get("matching_urls", [])
                if matching:
                    print(f"\n   {'='*55}")
                    print(f"   URLS CON COINCIDENCIAS ({len(matching)} encontradas)")
                    print(f"   {'='*55}")
                    for i, match in enumerate(matching[:20], 1):
                        print(f"\n   {i}. {match.get('url', '')[:70]}")
                        if match.get('title'):
                            print(f"      Titulo: {match['title'][:60]}")
                        print(f"      Keywords encontradas: {match.get('keywords_found', [])}")
                    
                    if len(matching) > 20:
                        print(f"\n   ... y {len(matching) - 20} URLs mas")
                else:
                    print(f"\n   No se encontraron URLs con las palabras clave")
                
                # Guardar resultados
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"web_spider_results_{timestamp}.json"
                
                with open(output_filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"\n   Resultados guardados en: {output_filename}")
            else:
                print(f"Error: {data.get('error')}")
        else:
            print(f"Respuesta: {data}")
        
        print("-" * 50)
        print("Test completado")


# =============================================================================
# TESTS AQUA
# =============================================================================

async def test_investigar_objetivo():
    """Prueba la herramienta investigar_objetivo_unp"""
    client = create_client()
    
    print("\n" + "=" * 60)
    print("TEST: Investigar Objetivo (AQUA - EXTERNO)")
    print("=" * 60)
    
    print("\nEsta herramienta investiga un objetivo en Internet y guarda el reporte.")
    objetivo = input("   Ingrese el objetivo a investigar: ").strip()
    if not objetivo:
        objetivo = "Universidad Nacional de Piura"
        print(f"   Usando objetivo de ejemplo: {objetivo}")
    
    print("\nConectando al servidor MCP...")
    print("NOTA: Esta operacion puede tardar varios minutos.")
    
    async with client:
        print("Conectado al servidor MCP")
        print(f"Servidor: {client.initialize_result.serverInfo.name if client.initialize_result else 'N/A'}\n")
        
        print("Ejecutando tool: investigar_objetivo_unp")
        print(f"   Objetivo: {objetivo}")
        print("-" * 50)
        
        result = await client.call_tool("investigar_objetivo_unp", {
            "objetivo": objetivo
        })
        
        data = extract_result(result)
        print(f"Respuesta: {data[:500] if isinstance(data, str) and len(data) > 500 else data}...")
        
        print("-" * 50)
        print("Test completado")


async def test_consultar_rag():
    """Prueba la herramienta consultar_rag"""
    client = create_client()
    
    print("\n" + "=" * 60)
    print("TEST: Consultar RAG (AQUA - INTERNO)")
    print("=" * 60)
    
    print("\nEsta herramienta busca antecedentes en la base de datos interna (RAG).")
    consulta = input("   Ingrese la consulta: ").strip()
    if not consulta:
        consulta = "Plan Democracia"
        print(f"   Usando consulta de ejemplo: {consulta}")
    
    print("\nConectando al servidor MCP...")
    
    async with client:
        print("Conectado al servidor MCP")
        print(f"Servidor: {client.initialize_result.serverInfo.name if client.initialize_result else 'N/A'}\n")
        
        print("Ejecutando tool: consultar_rag")
        print(f"   Consulta: {consulta}")
        print("-" * 50)
        
        result = await client.call_tool("consultar_rag", {
            "consulta": consulta
        })
        
        data = extract_result(result)
        print(f"Respuesta: {data[:1000] if isinstance(data, str) and len(data) > 1000 else data}")
        
        print("-" * 50)
        print("Test completado")


async def test_consultar_conocimiento():
    """Prueba la herramienta consultar_conocimiento"""
    client = create_client()
    
    print("\n" + "=" * 60)
    print("TEST: Consultar Conocimiento (AQUA - ANALITICA)")
    print("=" * 60)
    
    print("\nEsta herramienta realiza consultas SQL sobre metricas usando lenguaje natural.")
    pregunta = input("   Ingrese la pregunta: ").strip()
    if not pregunta:
        pregunta = "Cuantos registros hay en la base de conocimiento?"
        print(f"   Usando pregunta de ejemplo: {pregunta}")
    
    print("\nConectando al servidor MCP...")
    
    async with client:
        print("Conectado al servidor MCP")
        print(f"Servidor: {client.initialize_result.serverInfo.name if client.initialize_result else 'N/A'}\n")
        
        print("Ejecutando tool: consultar_conocimiento")
        print(f"   Pregunta: {pregunta}")
        print("-" * 50)
        
        result = await client.call_tool("consultar_conocimiento", {
            "pregunta": pregunta
        })
        
        data = extract_result(result)
        print(f"Respuesta: {data}")
        
        print("-" * 50)
        print("Test completado")


async def test_reportar_objetivo():
    """Prueba la herramienta reportar_objetivo"""
    client = create_client()
    
    print("\n" + "=" * 60)
    print("TEST: Reportar Objetivo (AQUA - REPORTES)")
    print("=" * 60)
    
    print("\nEsta herramienta genera un informe ejecutivo sobre un objetivo.")
    objetivo = input("   Ingrese el objetivo: ").strip()
    if not objetivo:
        objetivo = "Universidad Nacional de Piura"
        print(f"   Usando objetivo de ejemplo: {objetivo}")
    
    print("\nConectando al servidor MCP...")
    print("NOTA: Esta operacion puede tardar varios minutos.")
    
    async with client:
        print("Conectado al servidor MCP")
        print(f"Servidor: {client.initialize_result.serverInfo.name if client.initialize_result else 'N/A'}\n")
        
        print("Ejecutando tool: reportar_objetivo")
        print(f"   Objetivo: {objetivo}")
        print("-" * 50)
        
        result = await client.call_tool("reportar_objetivo", {
            "objetivo": objetivo
        })
        
        data = extract_result(result)
        print(f"Respuesta: {data[:1000] if isinstance(data, str) and len(data) > 1000 else data}...")
        
        print("-" * 50)
        print("Test completado")


async def test_evaluar_hechos():
    """Prueba la herramienta evaluar_hechos_victimizantes"""
    client = create_client()
    
    print("\n" + "=" * 60)
    print("TEST: Evaluar Hechos Victimizantes (AQUA - FORENSE)")
    print("=" * 60)
    
    print("\nEsta herramienta realiza auditoria forense sobre riesgos detectados.")
    objetivo = input("   Ingrese el objetivo: ").strip()
    if not objetivo:
        objetivo = "Caso de prueba"
        print(f"   Usando objetivo de ejemplo: {objetivo}")
    
    print("\nConectando al servidor MCP...")
    print("NOTA: Esta operacion puede tardar varios minutos.")
    
    async with client:
        print("Conectado al servidor MCP")
        print(f"Servidor: {client.initialize_result.serverInfo.name if client.initialize_result else 'N/A'}\n")
        
        print("Ejecutando tool: evaluar_hechos_victimizantes")
        print(f"   Objetivo: {objetivo}")
        print("-" * 50)
        
        result = await client.call_tool("evaluar_hechos_victimizantes", {
            "objetivo": objetivo
        })
        
        data = extract_result(result)
        print(f"Respuesta: {data[:1000] if isinstance(data, str) and len(data) > 1000 else data}...")
        
        print("-" * 50)
        print("Test completado")


# =============================================================================
# LISTAR TOOLS
# =============================================================================

async def test_list_tools():
    """Lista todas las herramientas disponibles en el servidor"""
    client = create_client()
    
    print("\n" + "=" * 60)
    print("HERRAMIENTAS DISPONIBLES EN EL SERVIDOR MCP")
    print("=" * 60)
    print("\nConectando al servidor MCP...")
    
    async with client:
        print("Conectado al servidor MCP")
        print(f"Servidor: {client.initialize_result.serverInfo.name if client.initialize_result else 'N/A'}\n")
        
        tools = await list_tools(client)
        
        print(f"Total de herramientas: {len(tools)}\n")
        print("-" * 50)
        
        for i, tool in enumerate(tools, 1):
            tool_name = getattr(tool, 'name', str(tool))
            tool_desc = getattr(tool, 'description', None) or 'Sin descripcion'
            
            print(f"\n{i}. {tool_name}")
            print(f"   Descripcion: {tool_desc[:100]}{'...' if len(tool_desc) > 100 else ''}")
            
            # Mostrar parametros si estan disponibles
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema = tool.inputSchema
                if 'properties' in schema:
                    print("   Parametros:")
                    for param_name, param_info in schema['properties'].items():
                        param_type = param_info.get('type', 'any')
                        required = param_name in schema.get('required', [])
                        req_str = " (requerido)" if required else " (opcional)"
                        print(f"      - {param_name}: {param_type}{req_str}")
        
        print("\n" + "-" * 50)


# =============================================================================
# MENU PRINCIPAL
# =============================================================================

def show_menu():
    """Muestra el menu principal"""
    print("\n" + "=" * 60)
    print("       CLIENTE DE PRUEBAS - MCP SERVER IA UNP")
    print("=" * 60)
    print(f"\n  Servidor: {MCP_SERVER_URL}")
    print("  NOTA: Asegurate de que el servidor este corriendo (python main.py)")
    print("\nSeleccione una opcion:\n")
    print("  === GENERAL ===")
    print("  [1] Listar herramientas disponibles")
    print("  [2] Probar ping (health check)")
    print("  [3] Probar crear PDF (create_pdf)")
    print("  [4] Probar enviar correo (send_email_report)")
    print("  [5] Probar enviar correo con PDF adjunto")
    print("  [6] Probar web spider (web_spider)")
    print()
    print("  === AQUA ===")
    print("  [7] Investigar objetivo (investigar_objetivo_unp)")
    print("  [8] Consultar RAG (consultar_rag)")
    print("  [9] Consultar conocimiento (consultar_conocimiento)")
    print("  [10] Reportar objetivo (reportar_objetivo)")
    print("  [11] Evaluar hechos victimizantes")
    print()
    print("  [0] Salir")
    print("\n" + "-" * 60)


async def run_all_tests():
    """Ejecuta todas las pruebas basicas en secuencia"""
    print("\n" + "=" * 60)
    print("EJECUTANDO PRUEBAS BASICAS")
    print("=" * 60)
    
    await test_list_tools()
    
    input("\nPresione Enter para continuar con ping...")
    await test_ping()
    
    input("\nPresione Enter para continuar con la prueba de PDF...")
    await test_create_pdf()
    
    print("\n" + "=" * 60)
    print("PRUEBAS BASICAS COMPLETADAS")
    print("=" * 60)


def handle_connection_error(e):
    """Maneja errores de conexión de forma amigable"""
    error_str = str(e).lower()
    if "connection" in error_str or "connect" in error_str or "refused" in error_str:
        print("\n" + "=" * 60)
        print("ERROR DE CONEXION")
        print("=" * 60)
        print(f"\nNo se pudo conectar al servidor MCP en: {MCP_SERVER_URL}")
        print("\nVerifica que:")
        print("  1. El servidor este corriendo (python main.py)")
        print("  2. El puerto 8000 este disponible")
        print("  3. No haya firewall bloqueando la conexion")
        print("=" * 60)
        return True
    return False


async def main_menu():
    """Menu principal interactivo"""
    while True:
        show_menu()
        
        try:
            opcion = input("Ingrese su opcion: ").strip()
            
            if opcion == "0":
                print("\nSaliendo del cliente de pruebas...")
                break
            elif opcion == "1":
                await test_list_tools()
            elif opcion == "2":
                await test_ping()
            elif opcion == "3":
                await test_create_pdf()
            elif opcion == "4":
                await test_send_email()
            elif opcion == "5":
                await test_send_email_with_pdf()
            elif opcion == "6":
                await test_web_spider()
            elif opcion == "7":
                await test_investigar_objetivo()
            elif opcion == "8":
                await test_consultar_rag()
            elif opcion == "9":
                await test_consultar_conocimiento()
            elif opcion == "10":
                await test_reportar_objetivo()
            elif opcion == "11":
                await test_evaluar_hechos()
            else:
                print("\nOpcion no valida. Intente de nuevo.")
            
            input("\nPresione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\nInterrumpido por el usuario")
            break
        except Exception as e:
            if not handle_connection_error(e):
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
            input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    import os
    
    # Permitir configurar URL via variable de entorno
    env_url = os.getenv("MCP_SERVER_URL")
    if env_url:
        MCP_SERVER_URL = env_url
    
    # Mapeo de tests disponibles
    test_map = {
        "list": test_list_tools,
        "ping": test_ping,
        "pdf": test_create_pdf,
        "email": test_send_email,
        "email_pdf": test_send_email_with_pdf,
        "spider": test_web_spider,
        "investigar": test_investigar_objetivo,
        "rag": test_consultar_rag,
        "conocimiento": test_consultar_conocimiento,
        "reportar": test_reportar_objetivo,
        "evaluar": test_evaluar_hechos,
        "all": run_all_tests
    }
    
    # Si se pasa un argumento, ejecutar ese test directamente
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        # Mostrar ayuda
        if test_name in ("-h", "--help", "help"):
            print("Uso: python test_client.py [test_name]")
            print(f"\nServidor: {MCP_SERVER_URL}")
            print("  (Configurable via MCP_SERVER_URL env var)")
            print(f"\nTests disponibles: {', '.join(test_map.keys())}")
            print("\nEjemplos:")
            print("  python test_client.py ping")
            print("  python test_client.py list")
            print("  python test_client.py all")
            sys.exit(0)
        
        if test_name in test_map:
            try:
                print(f"Conectando a: {MCP_SERVER_URL}")
                asyncio.run(test_map[test_name]())
            except KeyboardInterrupt:
                print("\n\nInterrumpido por el usuario")
            except Exception as e:
                if not handle_connection_error(e):
                    print(f"\nError: {e}")
                    import traceback
                    traceback.print_exc()
        else:
            print(f"Test desconocido: {test_name}")
            print(f"Tests disponibles: {', '.join(test_map.keys())}")
            sys.exit(1)
    else:
        # Sin argumentos, mostrar menu interactivo
        try:
            asyncio.run(main_menu())
        except KeyboardInterrupt:
            print("\n\nSaliendo...")
