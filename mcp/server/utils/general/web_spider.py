from playwright.sync_api import sync_playwright


def web_filter(urls: list[str], keywords: list[str], deep_search: bool = True, max_links_per_page: int = None) -> dict:
    """
    Busqueda en prensa: visita URLs, extrae enlaces, y busca multiples palabras clave
    en titulo, descripcion, URL y TODO el texto de la pagina.
    
    Args:
        urls: Lista de URLs iniciales a visitar
        keywords: Lista de palabras clave para buscar (ej: ["corrupcion", "gobierno", "investigacion"])
        deep_search: Si True, visita cada enlace encontrado para extraer su contenido
        max_links_per_page: Maximo de enlaces a analizar por pagina (None = sin limite)
    
    Returns:
        dict: Diccionario con:
            - "success": bool
            - "keywords_used": list - Palabras clave utilizadas
            - "source_pages": dict - Informacion de las paginas fuente
            - "analyzed_links": list - Lista de todos los enlaces analizados
            - "matching_urls": list - Lista final de URLs con coincidencias
            - "summary": dict - Resumen de resultados
    """
    if not urls:
        return {"success": False, "error": "La lista de URLs esta vacia."}
    
    if not keywords:
        return {"success": False, "error": "La lista de palabras clave esta vacia."}
    
    # Normalizar keywords
    if isinstance(keywords, str):
        keywords = [keywords]
    
    keywords = [kw.lower().strip() for kw in keywords if kw and kw.strip()]
    
    if not keywords:
        return {"success": False, "error": "No hay palabras clave validas."}
    
    source_pages = {}
    analyzed_links = []
    matching_urls = []
    errors = []
    
    def extract_page_content(page):
        """Extrae titulo, descripcion, metadata y el contenido PRINCIPAL de la noticia (excluyendo menus, sidebars, etc)"""
        return page.evaluate('''() => {
            const getMeta = (selector) => {
                const el = document.querySelector(selector);
                return el ? el.getAttribute('content') : '';
            };
            
            // Selectores para el contenido PRINCIPAL de la noticia
            const articleSelectors = [
                'article.article-content',
                'article .article-body',
                'article .post-content',
                'article .entry-content',
                'article .news-body',
                'article .story-body',
                'article .content-body',
                '.article-content',
                '.article-body',
                '.post-content',
                '.entry-content',
                '.news-body',
                '.news-content',
                '.story-body',
                '.story-content',
                '.content-body',
                '.nota-contenido',
                '.cuerpo-nota',
                '.texto-nota',
                '[itemprop="articleBody"]',
                '[data-component="text-block"]',
                'article > div.content',
                'article',
                'main article',
                '[role="article"]',
                'main [role="main"]',
                'main .content',
                '#article-body',
                '#story-body',
                '#content-body'
            ];
            
            // Selectores a EXCLUIR (menus, sidebars, noticias relacionadas, etc)
            const excludeSelectors = [
                'nav', 'header', 'footer', 'aside',
                '.nav', '.menu', '.navigation', '.navbar',
                '.sidebar', '.side-bar', '.lateral',
                '.related', '.relacionadas', '.mas-noticias', '.more-news',
                '.recommended', '.recomendadas', '.sugeridas',
                '.comments', '.comentarios',
                '.social', '.share', '.compartir',
                '.advertisement', '.ad', '.ads', '.publicidad',
                '.footer', '.header',
                '.breadcrumb', '.breadcrumbs',
                '.tags', '.etiquetas',
                '.author-bio', '.autor',
                '.newsletter', '.suscripcion',
                '[role="navigation"]',
                '[role="complementary"]',
                '[role="banner"]',
                '[role="contentinfo"]',
                '.widget', '.module-related'
            ];
            
            // Funcion para verificar si un elemento esta dentro de zonas excluidas
            const isExcluded = (element) => {
                let parent = element;
                while (parent && parent !== document.body) {
                    for (const selector of excludeSelectors) {
                        try {
                            if (parent.matches && parent.matches(selector)) {
                                return true;
                            }
                        } catch (e) {}
                    }
                    parent = parent.parentElement;
                }
                return false;
            };
            
            // Buscar el contenedor del articulo principal
            let articleContainer = null;
            for (const selector of articleSelectors) {
                try {
                    const el = document.querySelector(selector);
                    if (el && el.innerText && el.innerText.trim().length > 200) {
                        articleContainer = el;
                        break;
                    }
                } catch (e) {}
            }
            
            // Extraer contenido del articulo principal
            const getArticleContent = () => {
                if (!articleContainer) {
                    return { article_text: '', article_paragraphs: [] };
                }
                
                // Obtener parrafos del articulo (excluyendo zonas no deseadas)
                const paragraphs = [];
                articleContainer.querySelectorAll('p').forEach(p => {
                    if (!isExcluded(p)) {
                        const text = p.innerText.trim();
                        if (text.length > 30) {
                            paragraphs.push(text);
                        }
                    }
                });
                
                // Texto completo del articulo
                let articleText = '';
                const clonedArticle = articleContainer.cloneNode(true);
                
                // Remover elementos excluidos del clon
                excludeSelectors.forEach(selector => {
                    try {
                        clonedArticle.querySelectorAll(selector).forEach(el => el.remove());
                    } catch (e) {}
                });
                
                articleText = clonedArticle.innerText.trim();
                
                return {
                    article_text: articleText.substring(0, 12000),
                    article_paragraphs: paragraphs.slice(0, 30)
                };
            };
            
            // Extraer H1 y H2 solo del articulo principal
            const getArticleHeadings = () => {
                const h1s = [];
                const h2s = [];
                
                const container = articleContainer || document;
                
                container.querySelectorAll('h1').forEach(h => {
                    if (!isExcluded(h)) {
                        const text = h.innerText.trim();
                        if (text) h1s.push(text);
                    }
                });
                
                container.querySelectorAll('h2').forEach(h => {
                    if (!isExcluded(h)) {
                        const text = h.innerText.trim();
                        if (text) h2s.push(text);
                    }
                });
                
                // Si no encontramos H1 en el articulo, usar el titulo de la pagina
                if (h1s.length === 0) {
                    const pageTitle = document.querySelector('h1.title, h1.headline, .article-title h1, .post-title h1');
                    if (pageTitle && !isExcluded(pageTitle)) {
                        h1s.push(pageTitle.innerText.trim());
                    }
                }
                
                return { h1: h1s.slice(0, 3), h2: h2s.slice(0, 8) };
            };
            
            const articleContent = getArticleContent();
            const headings = getArticleHeadings();
            
            return {
                url: window.location.href,
                title: document.title || '',
                description: getMeta('meta[name="description"]') || getMeta('meta[property="og:description"]') || '',
                keywords_meta: getMeta('meta[name="keywords"]') || '',
                og_title: getMeta('meta[property="og:title"]') || '',
                og_description: getMeta('meta[property="og:description"]') || '',
                og_image: getMeta('meta[property="og:image"]') || '',
                twitter_title: getMeta('meta[name="twitter:title"]') || '',
                twitter_description: getMeta('meta[name="twitter:description"]') || '',
                author: getMeta('meta[name="author"]') || getMeta('meta[property="article:author"]') || '',
                published_date: getMeta('meta[property="article:published_time"]') || getMeta('meta[name="date"]') || '',
                h1: headings.h1,
                h2: headings.h2,
                paragraphs: articleContent.article_paragraphs,
                article_text: articleContent.article_text,
                has_article_content: articleContent.article_text.length > 200
            };
        }''')
    
    def extract_snippet(text, keyword, context_chars=150):
        """Extrae un fragmento de texto alrededor de la keyword encontrada"""
        text_lower = text.lower()
        kw_lower = keyword.lower()
        
        pos = text_lower.find(kw_lower)
        if pos == -1:
            return None
        
        # Calcular inicio y fin del extracto
        start = max(0, pos - context_chars)
        end = min(len(text), pos + len(keyword) + context_chars)
        
        # Ajustar para no cortar palabras
        if start > 0:
            space_pos = text.find(' ', start)
            if space_pos != -1 and space_pos < pos:
                start = space_pos + 1
        
        if end < len(text):
            space_pos = text.rfind(' ', pos + len(keyword), end)
            if space_pos != -1:
                end = space_pos
        
        snippet = text[start:end].strip()
        
        # Agregar elipsis si es necesario
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet
    
    def check_keywords_match(data, kws):
        """
        Verifica si alguna de las keywords esta presente en el CONTENIDO PRINCIPAL de la noticia.
        Retorna las ubicaciones Y los extractos donde se encontro cada keyword.
        """
        all_matches = {}
        
        # Solo campos relevantes para el contenido de la noticia
        title = data.get('title', '') or ''
        og_title = data.get('og_title', '') or ''
        description = data.get('description', '') or ''
        og_description = data.get('og_description', '') or ''
        
        # Contenido del articulo principal (ya filtrado, sin menus/sidebars)
        h1_list = data.get('h1', [])
        h2_list = data.get('h2', [])
        paragraphs_list = data.get('paragraphs', [])
        article_text = data.get('article_text', '') or ''
        
        for kw in kws:
            match_info = {
                "locations": [],
                "snippets": []
            }
            
            kw_lower = kw.lower()
            
            # Buscar en titulo
            if kw_lower in title.lower():
                match_info["locations"].append('titulo')
                match_info["snippets"].append({
                    "location": "titulo",
                    "text": title
                })
            elif kw_lower in og_title.lower():
                match_info["locations"].append('titulo')
                match_info["snippets"].append({
                    "location": "titulo",
                    "text": og_title
                })
            
            # Buscar en descripcion/resumen
            if kw_lower in description.lower():
                match_info["locations"].append('descripcion')
                match_info["snippets"].append({
                    "location": "descripcion",
                    "text": description
                })
            elif kw_lower in og_description.lower():
                match_info["locations"].append('descripcion')
                match_info["snippets"].append({
                    "location": "descripcion",
                    "text": og_description
                })
            
            # Buscar en H1 del articulo
            for h1 in h1_list:
                if kw_lower in h1.lower():
                    if 'h1_articulo' not in match_info["locations"]:
                        match_info["locations"].append('h1_articulo')
                    match_info["snippets"].append({
                        "location": "h1_articulo",
                        "text": h1
                    })
            
            # Buscar en H2 del articulo
            for h2 in h2_list:
                if kw_lower in h2.lower():
                    if 'h2_articulo' not in match_info["locations"]:
                        match_info["locations"].append('h2_articulo')
                    match_info["snippets"].append({
                        "location": "h2_articulo",
                        "text": h2
                    })
            
            # Buscar en parrafos del articulo
            for para in paragraphs_list:
                if kw_lower in para.lower():
                    if 'parrafos_articulo' not in match_info["locations"]:
                        match_info["locations"].append('parrafos_articulo')
                    snippet = extract_snippet(para, kw, 120)
                    if snippet:
                        match_info["snippets"].append({
                            "location": "parrafo",
                            "text": snippet
                        })
            
            # Buscar en texto completo del articulo (si no se encontro en parrafos)
            if 'parrafos_articulo' not in match_info["locations"] and kw_lower in article_text.lower():
                match_info["locations"].append('cuerpo_articulo')
                snippet = extract_snippet(article_text, kw, 150)
                if snippet:
                    match_info["snippets"].append({
                        "location": "cuerpo_articulo",
                        "text": snippet
                    })
            
            # Limitar snippets a los 5 mas relevantes
            match_info["snippets"] = match_info["snippets"][:5]
            
            if match_info["locations"]:
                all_matches[kw] = match_info
        
        return all_matches
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            for source_url in urls:
                try:
                    # Normalizar URL
                    if not source_url.startswith(('http://', 'https://')):
                        source_url = 'https://' + source_url
                    
                    page = browser.new_page()
                    page.goto(source_url, timeout=30000, wait_until="domcontentloaded")
                    
                    # Extraer contenido completo de la pagina fuente
                    source_content = extract_page_content(page)
                    source_matches = check_keywords_match(source_content, keywords)
                    
                    # Extraer todos los enlaces
                    all_links = page.eval_on_selector_all(
                        'a[href]',
                        '''elements => elements.map(el => ({
                            href: el.href,
                            text: el.innerText.trim(),
                            title: el.getAttribute('title') || ''
                        })).filter(link => 
                            link.href && 
                            link.href.startsWith('http') && 
                            !link.href.includes('javascript:') &&
                            !link.href.includes('#')
                        )'''
                    )
                    
                    # Eliminar duplicados y clasificar enlaces
                    seen = set()
                    unique_links = []
                    keyword_links = []  # Enlaces que contienen keywords en URL o texto
                    
                    for link in all_links:
                        href = link.get('href', '')
                        if href and href not in seen:
                            seen.add(href)
                            
                            # Verificar si el enlace contiene alguna keyword
                            href_lower = href.lower()
                            text_lower = (link.get('text', '') or '').lower()
                            title_lower = (link.get('title', '') or '').lower()
                            
                            keywords_in_link = []
                            for kw in keywords:
                                if kw in href_lower or kw in text_lower or kw in title_lower:
                                    keywords_in_link.append(kw)
                            
                            link['keywords_in_link'] = keywords_in_link
                            link['has_keyword'] = len(keywords_in_link) > 0
                            
                            unique_links.append(link)
                            
                            if keywords_in_link:
                                keyword_links.append(link)
                    
                    # Priorizar enlaces con keywords, luego el resto
                    # Los enlaces con keywords se visitan primero
                    prioritized_links = keyword_links.copy()
                    
                    # Si deep_search es True y hay limite, completar con otros enlaces
                    if max_links_per_page is not None:
                        remaining_slots = max_links_per_page - len(keyword_links)
                        if remaining_slots > 0:
                            other_links = [l for l in unique_links if not l.get('has_keyword')]
                            prioritized_links.extend(other_links[:remaining_slots])
                        links_to_analyze = prioritized_links[:max_links_per_page]
                    else:
                        # Sin limite: primero los que tienen keywords, luego el resto
                        other_links = [l for l in unique_links if not l.get('has_keyword')]
                        links_to_analyze = prioritized_links + other_links
                    
                    source_pages[source_url] = {
                        "title": source_content.get('title', ''),
                        "description": source_content.get('description', ''),
                        "author": source_content.get('author', ''),
                        "published_date": source_content.get('published_date', ''),
                        "keyword_matches": source_matches,
                        "keywords_found": list(source_matches.keys()),
                        "has_match": len(source_matches) > 0,
                        "total_links_found": len(unique_links),
                        "links_with_keywords": len(keyword_links),
                        "links_analyzed": len(links_to_analyze)
                    }
                    
                    # Si la pagina fuente tiene match, agregarla
                    if source_matches:
                        matching_urls.append({
                            "url": source_url,
                            "title": source_content.get('title', ''),
                            "description": source_content.get('description', ''),
                            "author": source_content.get('author', ''),
                            "published_date": source_content.get('published_date', ''),
                            "keywords_found": list(source_matches.keys()),
                            "matches_detail": source_matches,
                            "source": "initial_url"
                        })
                    
                    page.close()
                    
                    # Deep search: visitar enlaces (priorizando los que tienen keywords)
                    if deep_search:
                        for link in links_to_analyze:
                            link_url = link.get('href', '')
                            if not link_url:
                                continue
                            
                            try:
                                link_page = browser.new_page()
                                link_page.goto(link_url, timeout=15000, wait_until="domcontentloaded")
                                
                                # Extraer contenido completo del enlace
                                link_content = extract_page_content(link_page)
                                link_matches = check_keywords_match(link_content, keywords)
                                
                                link_data = {
                                    "url": link_url,
                                    "source_url": source_url,
                                    "link_text": link.get('text', ''),
                                    "keywords_in_link": link.get('keywords_in_link', []),
                                    "title": link_content.get('title', ''),
                                    "description": link_content.get('description', ''),
                                    "author": link_content.get('author', ''),
                                    "published_date": link_content.get('published_date', ''),
                                    "h1": link_content.get('h1', []),
                                    "keywords_found": list(link_matches.keys()),
                                    "keyword_matches": link_matches,
                                    "has_match": len(link_matches) > 0
                                }
                                
                                analyzed_links.append(link_data)
                                
                                # Si tiene match en el contenido, agregar a la lista final
                                if link_matches:
                                    matching_urls.append({
                                        "url": link_url,
                                        "title": link_content.get('title', ''),
                                        "description": link_content.get('description', ''),
                                        "author": link_content.get('author', ''),
                                        "published_date": link_content.get('published_date', ''),
                                        "keywords_in_link": link.get('keywords_in_link', []),
                                        "keywords_found": list(link_matches.keys()),
                                        "matches_detail": link_matches,
                                        "source": source_url
                                    })
                                
                                link_page.close()
                                
                            except Exception as link_error:
                                analyzed_links.append({
                                    "url": link_url,
                                    "source_url": source_url,
                                    "link_text": link.get('text', ''),
                                    "keywords_in_link": link.get('keywords_in_link', []),
                                    "error": str(link_error),
                                    "has_match": False
                                })
                    
                except Exception as e:
                    errors.append(f"Error al procesar {source_url}: {str(e)}")
                    source_pages[source_url] = {"error": str(e)}
            
            browser.close()
        
        # Eliminar duplicados de matching_urls por URL
        seen_matching = set()
        unique_matching = []
        for item in matching_urls:
            if item['url'] not in seen_matching:
                seen_matching.add(item['url'])
                unique_matching.append(item)
        
        response = {
            "success": True,
            "keywords_used": keywords,
            "source_pages": source_pages,
            "analyzed_links": analyzed_links,
            "matching_urls": unique_matching,
            "summary": {
                "keywords_searched": keywords,
                "total_source_pages": len(urls),
                "total_links_analyzed": len(analyzed_links),
                "links_with_keywords_visited": len([l for l in analyzed_links if l.get('keywords_in_link')]),
                "total_matching_urls": len(unique_matching),
                "deep_search_enabled": deep_search,
                "max_links_per_page": max_links_per_page if max_links_per_page else "unlimited"
            }
        }
        
        if errors:
            response["warnings"] = errors
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error al inicializar el navegador: {str(e)}"
        }