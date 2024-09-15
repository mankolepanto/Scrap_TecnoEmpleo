import time
import re
from datetime import datetime
from .utils import get_soup, find_next_page
from .data_handler import update_csv_with_job_data


def extract_targetas_principales(job, target_date):
    """Extrae la información relevante de una oferta de trabajo."""
    try:
        ''' Extraer la fecha de publicación '''
        date_div = job.find('div', class_='col-12 col-lg-3 text-gray-700 pt-2 text-right hidden-md-down')
        date_str = date_div.contents[0].strip() if date_div and date_div.contents else "Fecha no encontrada"
        
        # Convertir la fecha de string a objeto datetime
        job_date = datetime.strptime(date_str, "%d/%m/%Y")
        
        # Si la fecha del trabajo no coincide con la fecha objetivo, retornar None
        if job_date.date() != target_date:
            return None

        # El resto del código permanece igual
        ''' Extraer el nombre del trabajo '''
        job_element = job.find('a', class_='font-weight-bold text-cyan-700')
        job_name = job_element.get_text().strip() if job_element else "Trabajo no encontrado"

        '''Extraer el enlace'''
        link_tag = job.select_one('h3.fs-5.mb-2 a')
        link = link_tag['href'] if link_tag else "Enlace no encontrado"

        # Extraer id de la oferta
        offer_id = None
        if link != "Enlace no encontrado":
            match = re.search(r'/rf-([a-zA-Z0-9]+)', link)
            offer_id = match.group(1) if match else "ID no encontrado"

        # Extraer nombre de la empresa
        a_tag = job.find('a', class_='text-primary link-muted')
        company_name = a_tag.get_text().strip() if a_tag else "Empresa no encontrada"

        # Frameworks
        parent_span = job.find('span', class_='hidden-md-down text-gray-800')
        badges = parent_span.find_all('span', class_='badge')
        extracted_values = [badge.get_text() for badge in badges]

        return {
            "date": date_str,
            "job_name": job_name,
            "link": link,
            "offer_id": offer_id,
            "company_name": company_name,
            "technologies": extracted_values,
            "details": {},
            "additional_info": {}
        }

    except Exception as e:
        print(f"Error al procesar la oferta de trabajo: {e}")
        return None
    

def datos_oferta(link):
    """Extrae información adicional de la oferta de trabajo desde el enlace proporcionado."""
    prin_oferta = {}
    
    soup = get_soup(link)
    col_1 = soup.find_all('span', class_='d-inline-block px-2')
    col_2 = soup.find_all('span', class_="float-end")
    
    # Iterar sobre los elementos encontrados simultáneamente
    for span_1, span_2 in zip(col_1, col_2):
        content_1 = span_1.get_text().strip()
        content_2 = ' '.join(span_2.get_text().split())
        prin_oferta[content_1] = content_2

    return prin_oferta


def info_adicional(soup):
    """
    Extrae información adicional del objeto BeautifulSoup y la organiza en un diccionario.

    Args:
        soup (BeautifulSoup): Objeto BeautifulSoup con el contenido HTML.

    Returns:
        dict: Diccionario con tecnologías y textos limpios.
    """
    # Capturar tecnologías (enlaces con la clase .pl--12 a)
    enlaces_tecnologias = soup.select('.pl--12 a')
    tecnologias = [enlace.text.strip() for enlace in enlaces_tecnologias]

    # Capturar textos de párrafos (enlaces con la clase .pl--12 p)
    enlaces_parrafos = soup.select('.pl--12 p')
    textos = [enlace.text.lstrip() for enlace in enlaces_parrafos]

    # Limpiar los textos eliminando tabulaciones, saltos de línea, y retornos de carro
    tabla_traduccion = str.maketrans('', '', '\t\n\r')
    textos_limpios = [texto.translate(tabla_traduccion) for texto in textos]

    # Unir las listas de tecnologías y textos limpios en un diccionario
    info_adicional_data = {
        "tecnologias": tecnologias,
        "textos_limpios": textos_limpios
    }

    return info_adicional_data

def scrape_jobs(url, target_date):
    """Realiza el scraping de ofertas de trabajo desde la URL proporcionada y crea un CSV con los datos del día objetivo."""
    all_jobs = []
    
    while url:
        soup = get_soup(url)
        ofertas = soup.find_all('div', class_='p-3 border rounded mb-3 bg-white')

        page_has_jobs = False

        for job in ofertas:
            job_info = extract_targetas_principales(job, target_date)

            if job_info:
                # Convertir la fecha extraída en un objeto datetime.date si no lo es ya
                job_date = datetime.strptime(job_info['date'], "%d/%m/%Y").date()  # Asegúrate de que el formato es correcto
                print(f"Fecha extraída: {job_date}, Fecha objetivo: {target_date}")

                # Verifica si la fecha de la oferta coincide con la fecha objetivo
                if job_date != target_date:
                    print("NO HAY MÁS TRABAJOS HOY.")
                    return
                
                # Extraer información adicional usando datos_oferta
                job_info['details'] = datos_oferta(job_info['link'])
                
                # Extraer información adicional usando info_adicional
                job_soup = get_soup(job_info['link'])
                job_info['additional_info'] = info_adicional(job_soup)

                #print_job_info(job_info)
                all_jobs.append(job_info)
                page_has_jobs = True
        
        # Si no hemos encontrado trabajos en esta página
        if not page_has_jobs:
            print("NO HAY MÁS TRABAJOS HOY.")
            break

        # Buscar la siguiente página si aún hay trabajos para la fecha objetivo
        url = find_next_page(soup)
        if url:
            print(f"Pasando a la siguiente página: {url}")
            time.sleep(3)
        else:
            print("No hay más páginas.")
            break

    # Crear el CSV con todos los trabajos recopilados si hay alguno
    if all_jobs:
        update_csv_with_job_data(all_jobs, 'job_data.csv')
    else:
        print(f"No jobs found for the date {target_date}")
