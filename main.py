from datetime import datetime, timedelta
from src.scraper import scrape_jobs

if __name__ == "__main__":
    # Calcular la fecha objetivo (día anterior)
    target_date = datetime.now().date() - timedelta(days=1)
    
    # URL de la primera página
    url = 'https://www.tecnoempleo.com/ofertas-trabajo/#'
    
    print(f"Buscando trabajos para la fecha: {target_date}")
    scrape_jobs(url, target_date)