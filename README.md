# 🤖 Scraper IA | Extractor Web Asistido por Inteligencia Artificial

**Deja de escribir selectores CSS como un esclavo.** Este no es otro scraper que se rompe cuando cambian un `id`. Es una herramienta de extracción dinámica que usa LLMs para entender la web como lo haría un humano, pero con la velocidad de una máquina.

---

## 🎯 El Problema que Resuelve (Y por qué el scraping tradicional es basura)

El scraping clásico es una pesadilla de mantenimiento. Si la web cambia un `.product-card` por un `.item-wrapper`, tu código muere. Te pasas el día inspeccionando el DOM y llorando por cambios de diseño.

**Scraper IA** implementa el patrón de **Generación de Scrapers Asistida por IA**:

1. **Comprensión Real:** Delega el análisis estructural a la API de OpenAI.
2. **Resiliencia:** La IA genera los selectores exactos en tiempo real.
3. **Escalabilidad:** Una vez que la IA entiende la página, el motor de Python extrae miles de datos a coste casi cero.

---

## 🏗️ Arquitectura y Flujo de Trabajo

Aquí no hay magia, hay ingeniería. El sistema sigue un flujo híbrido diseñado para no quemar tu presupuesto en tokens.

### El Proceso:

1. **Inferencia de Búsqueda:** No tienes que buscar la URL exacta. Metes "zapatillas Nike" y la IA deduce el endpoint de búsqueda (ej. `tienda.com/search?q=zapatillas+nike`).
2. **Renderizado (CSR):** Usamos **Playwright** para levantar un Chromium. Si la web carga contenido con JavaScript o tiene *lazy-loading*, lo capturamos todo.
3. **Limpieza de Basura (DOM Stripping):** Antes de enviar nada a la IA, barremos el HTML. Eliminamos scripts, SVGs, estilos y menús innecesarios. Pasamos de 500KB de basura a menos de 40KB de puro contenido.
4. **Análisis Estructural (One-Shot):** Enviamos el HTML limpio a `gpt-4o-mini`. La IA nos devuelve un JSON con el "mapa" de la web: selectores de producto, precio y paginación.
5. **Extracción Masiva:** Con el mapa en la mano, el script navega solo. Las siguientes 50 páginas se scrapean con Python puro, sin llamadas extra a la API de OpenAI. **Velocidad máxima, coste mínimo.**

---

## 🛠️ El Arsenal (Stack Tecnológico)

* **Backend:** `FastAPI` — Porque la asincronía no es negociable.
* **Navegación:** `Playwright` — Para saltarnos el renderizado básico y actuar como un navegador real.
* **Parseo:** `BeautifulSoup4` — Cirugía rápida en el árbol HTML.
* **Cerebro:** `OpenAI API (gpt-4o-mini)` — Inteligencia lógica vía *Function Calling*.
* **Interfaz:** `TailwindCSS` & JS Vanilla — Simple, funcional y sin frameworks pesados.

---

## ⚙️ Instalación y Despliegue Local

### Requisitos

* **Python 3.9+**
* **OpenAI API Key**

### Setup Rápido

```bash
# 1. Clonar
git clone https://github.com/aviba3/scraper-ia.git && cd scraper-ia

# 2. Entorno (Hazlo bien)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Dependencias
pip install -r requirements.txt
playwright install chromium

# 4. Fuego
uvicorn main:app --reload

```

---

## ⚠️ Realidad y Candor (Disclaimer)

* **Anti-Bots:** Si intentas atacar Amazon o Zara a pelo, te van a banear la IP en 3 segundos. Usa proxies si vas a jugar en las grandes ligas.
* **Costes:** Cada "descubrimiento" de dominio cuesta una fracción de céntimo. No seas tonto y no limpies el HTML antes de enviarlo o te arruinarás.

---
