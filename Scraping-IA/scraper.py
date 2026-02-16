from bs4 import BeautifulSoup
from openai import OpenAI
import json
import time
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright # NUESTRA NUEVA ARMA SECRETA

class ScraperEngine:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_search_url(self, base_url: str, keyword: str) -> str:
        print(f"🧠 IA calculando la URL de búsqueda para: '{keyword}' en {base_url}...")
        prompt = f"""
        Eres un experto en e-commerce. El usuario quiere buscar "{keyword}" en la tienda {base_url}.
        Deduce cuál sería la URL directa de resultados de búsqueda.
        Ejemplos: 
        - amazon.es + zapatos -> https://www.amazon.es/s?k=zapatos
        - elcorteingles.es + nike -> https://www.elcorteingles.es/search/?s=nike
        
        Devuelve ÚNICAMENTE un JSON válido con esta clave:
        {{
            "search_url": "la url de busqueda generada"
        }}
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.1
        )
        url = json.loads(response.choices[0].message.content).get("search_url", base_url)
        print(f"🔗 URL generada: {url}")
        return url

    def get_html_snippet(self, url: str):
        print(f"👻 Abriendo navegador fantasma para: {url}")
        
        # INICIO DE LA MAGIA DE PLAYWRIGHT
        with sync_playwright() as p:
            # Lanzamos Chromium en modo invisible (headless=True)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="es-ES"
            )
            page = context.new_page()
            
            try:
                # networkidle: espera a que no haya peticiones de red (JavaScript terminado)
                page.goto(url, wait_until="networkidle", timeout=30000)
                print("⏳ Web cargada. Haciendo scroll para forzar la carga de imágenes y JS...")
                
                # Simulamos scroll humano hacia abajo
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(1) # Pequeña pausa
                page.evaluate("window.scrollBy(0, 1000)")
                time.sleep(2) # Esperamos a que todo se pinte en pantalla
                
                html_content = page.content()
                print("✅ HTML renderizado capturado con éxito.")
            except Exception as e:
                print(f"⚠️ Aviso durante la carga (probablemente un timeout menor): {e}")
                html_content = page.content() # Salvamos lo que haya podido cargar
            finally:
                browser.close()
        
        # Limpieza con BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for tag in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
            tag.extract()
            
        main_content = soup.find('main') or soup.body
        body_html = str(main_content)[:40000] 
        return body_html, soup

    def get_selectors_from_ai(self, html_snippet: str) -> dict:
        print("🤖 IA analizando la estructura de la tienda y buscando la paginación...")
        prompt = f"""
        Eres un experto en Web Scraping. Analiza este HTML de una tienda online.
        Identifica los selectores CSS exactos para extraer: 
        1. Contenedor de CADA producto (clave: 'contenedor_producto')
        2. Nombre del producto (clave: 'nombre')
        3. Precio del producto (clave: 'precio')
        4. El selector CSS del enlace (etiqueta <a>) para ir a la "Siguiente Página" o "Next" (clave: 'siguiente_pagina'). Si no lo encuentras, devuelve "".

        Devuelve ÚNICAMENTE un objeto JSON válido con estas 4 claves.
        HTML:
        {html_snippet}
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.1 
        )
        selectors = json.loads(response.choices[0].message.content)
        print(f"🎯 Selectores encontrados: {selectors}")
        return selectors

    def extract_data(self, soup: BeautifulSoup, selectors: dict, base_url: str):
        data = []
        next_page_url = None
        
        contenedor_selector = selectors.get("contenedor_producto", "")
        if not contenedor_selector:
            return data, next_page_url

        containers = soup.select(contenedor_selector)
        
        for item in containers:
            try:
                name_elem = item.select_one(selectors.get("nombre", ""))
                price_elem = item.select_one(selectors.get("precio", ""))
                
                if name_elem:
                    data.append({
                        "Nombre": name_elem.text.strip(),
                        "Precio": price_elem.text.strip() if price_elem else "No disponible"
                    })
            except Exception:
                continue
                
        next_page_selector = selectors.get("siguiente_pagina", "")
        if next_page_selector:
            next_button = soup.select_one(next_page_selector)
            if next_button and next_button.has_attr('href'):
                next_page_url = urljoin(base_url, next_button['href'])
                
        return data, next_page_url

    def run_smart_scrape(self, base_url: str, keyword: str, max_pages: int = 3):
        all_data = []
        current_url = self.generate_search_url(base_url, keyword)
        
        html_snippet, soup = self.get_html_snippet(current_url)
        selectors = self.get_selectors_from_ai(html_snippet)
        
        print(f"📄 Extrayendo página 1: {current_url}")
        page_data, next_page_url = self.extract_data(soup, selectors, current_url)
        all_data.extend(page_data)
        print(f"✅ {len(page_data)} productos encontrados en página 1.")
        
        pages_scraped = 1
        while next_page_url and pages_scraped < max_pages:
            pages_scraped += 1
            print(f"📄 Extrayendo página {pages_scraped}: {next_page_url}")
            
            try:
                # Usamos Playwright también para las páginas siguientes
                _, soup = self.get_html_snippet(next_page_url)
                page_data, next_page_url = self.extract_data(soup, selectors, current_url)
                all_data.extend(page_data)
                print(f"✅ {len(page_data)} productos encontrados en página {pages_scraped}.")
            except Exception as e:
                print(f"❌ Error al cargar la página {pages_scraped}: {e}")
                break
                
        return all_data, selectors