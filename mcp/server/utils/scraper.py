import requests
import urllib3
import sys
from bs4 import BeautifulSoup
from typing import Optional

# Deshabilitar advertencias de seguridad SSL para peticiones a IPs internas
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuracion de la API interna de la oficina
INTERNAL_API_URL = "http://172.16.20.31:8001/api/extraer"

class Scraper:
    """
    Herramienta de Extraccion Hibrida.
    
    Logica de funcionamiento:
    1. Intenta consumir el servicio interno de la oficina (API UNP).
    2. Si falla o no hay conexion, ejecuta una extraccion local utilizando BeautifulSoup
       con filtros de limpieza para eliminar publicidad y menus.
    """

    def _extraer_local_quirurgico(self, url: str) -> str:
        """
        Metodo de Respaldo (Fallback).
        Se ejecuta SOLO si la API interna falla. Descarga y limpia el HTML localmente.
        
        Args:
            url (str): URL a procesar.
            
        Returns:
            str: Contenido limpio formateado.
        """
        print(f"[SCRAPER] API interna no disponible. Ejecutando extraccion LOCAL para: {url}", file=sys.stderr)
        
        # Headers para simular un navegador real y evitar bloqueos (Error 403)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        
        try:
            # Timeout de 15s para conexiones locales (internet abierto)
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. LIMPIEZA ESTRUCTURAL
            # Eliminamos etiquetas que contienen ruido (menus, scripts, publicidad)
            etiquetas_basura = [
                'script', 'style', 'nav', 'header', 'footer', 'aside', 
                'form', 'iframe', 'button', 'svg', 'noscript', 'menu', 'figure', 'ads'
            ]
            for tag in soup(etiquetas_basura):
                tag.decompose()
            
            # 2. EXTRACCION DE TITULO
            titulo = "Sin Titulo"
            meta_title = soup.find('meta', property='og:title')
            if meta_title:
                titulo = meta_title['content']
            elif soup.title:
                titulo = soup.title.string
            
            # 3. EXTRACCION DE CONTENIDO LIMPIO
            texto_acumulado = []
            parrafos = soup.find_all('p')
            
            for p in parrafos:
                texto = p.get_text(strip=True)
                
                # Filtro de calidad: Ignorar parrafos muy cortos (menus, firmas)
                if len(texto) > 60: 
                    texto_lower = texto.lower()
                    # Filtro de palabras clave de basura
                    palabras_basura = ["derechos reservados", "clic aqui", "suscribete", "copyright", "siguenos"]
                    if any(x in texto_lower for x in palabras_basura):
                        continue
                    
                    texto_acumulado.append(texto)
            
            contenido_limpio = "\n\n".join(texto_acumulado)
            
            # Fallback local: Si no se encontraron parrafos <p>, intentar texto plano
            if len(contenido_limpio) < 100:
                lineas = soup.get_text(separator='\n', strip=True).split('\n')
                contenido_limpio = "\n".join([l for l in lineas if len(l) > 80])

            return f"TITULO: {titulo}\n\nCONTENIDO:\n{contenido_limpio}"

        except Exception as e:
            return f"Error Local: {str(e)[:100]}"

    def procesar(self, url: str) -> str:
        """
        Punto de entrada principal.
        Intenta primero la red de la oficina, luego la red local.
        """
        # --- INTENTO 1: API OFICINA ---
        try:
            # Timeout corto (4s) para detectar rapido si estamos fuera de la oficina
            payload = {"url": url}
            resp = requests.post(INTERNAL_API_URL, json=payload, timeout=4, verify=False)
            
            if resp.status_code == 200:
                data = resp.json()
                titulo = data.get("titulo", "Sin Titulo")
                texto = data.get("texto", "")
                
                # Validacion: Si la API devuelve texto vacio, forzamos el local
                if not texto or len(texto) < 50:
                    print(f"[SCRAPER] API interna devolvio contenido vacio. Cambiando a local.", file=sys.stderr)
                    return self._extraer_local_quirurgico(url)
                
                # Exito con API Interna
                print(f"[SCRAPER] Extraccion exitosa via API Oficina.", file=sys.stderr)
                return f"TITULO: {titulo}\n\nCONTENIDO:\n{texto}"
            
            else:
                print(f"[SCRAPER] API interna retorno codigo {resp.status_code}. Cambiando a local.", file=sys.stderr)

        except requests.exceptions.ConnectionError:
            # Error comun si no estamos conectados a la VPN o red de oficina
            pass
        except requests.exceptions.Timeout:
            print(f"[SCRAPER] Timeout conectando a API oficina. Cambiando a local.", file=sys.stderr)
        except Exception as e:
            print(f"[SCRAPER] Error general en API oficina: {e}", file=sys.stderr)

        # --- INTENTO 2: FALLBACK LOCAL ---
        # Si llegamos aqui, la API de la oficina fallo. Usamos internet directo.
        return self._extraer_local_quirurgico(url)

# Instancia global exportada
scraper_engine = Scraper()