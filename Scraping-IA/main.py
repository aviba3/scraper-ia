from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from scraper import ScraperEngine

# Inicializamos la aplicación FastAPI
app = FastAPI(title="AI Smart Scraper Pro")

# Configuramos la carpeta donde estará nuestra interfaz web (HTML)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/scrape")
def perform_scraping(
    url: str = Form(...), 
    api_key: str = Form(...),
    keyword: str = Form(...) # NUEVO: Recibimos lo que el usuario quiere buscar
):
    try:
        engine = ScraperEngine(api_key=api_key)
        
        # Ejecutamos el motor inteligente (busca URL, saca selectores y pagina)
        data, selectors = engine.run_smart_scrape(base_url=url, keyword=keyword, max_pages=3)
        
        return JSONResponse(content={
            "status": "success",
            "message": "Scraping completado con éxito",
            "selectors_used": selectors,
            "total_items": len(data),
            "data": data
        })
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))