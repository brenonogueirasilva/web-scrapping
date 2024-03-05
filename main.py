from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import os 
import yaml 
import tempfile
import argparse
import json

from src.cloud_storage import CloudStorage
import src.functions as fc 

def main():

    local = os.getenv('LOCAL')
    path_fields = './src/fields.yaml'
    path_schema = './src/schema.json'

    if local == 'True':
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] =  './gcp_account.json'

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())

    browser = webdriver.Chrome( options=chrome_options)
    cloud_storage = CloudStorage()
    temp_dir = tempfile.TemporaryDirectory()

    parser = argparse.ArgumentParser()
    parser.add_argument('location', type=str)
    parser.add_argument('date_start', type=str)
    parser.add_argument('date_end', type=str)
    parser.add_argument('adults', type=int)
    parser.add_argument('children', type=int)
    parser.add_argument('infants', type=int)
    parser.add_argument('pets', type=int)

    args = parser.parse_args()
    location = args.location 
    date_start = args.date_start
    date_end = args.date_end
    adults = args.adults
    children = args.children
    infants = args.infants
    pets = args.pets

    bucket_name = "web_scrap_airbnb" 
    today_date = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    pop_up_state = True
    url_airbnb = f"https://www.airbnb.com.br/s/{location}/homes?$&checkin={date_start}&checkout={date_end}&adults={adults}&children={children}&infants={infants}&pets={pets}"

    with open( path_fields, 'r') as arquivo:
        fields_yaml_complete = yaml.safe_load(arquivo)

    with open(path_schema, 'r') as arquivo_json:
        schema_json = json.load(arquivo_json)

    print('Beginning Web Scrapping')
    wait_fields = fields_yaml_complete['wait_fields']
    fields_yaml = fields_yaml_complete
    session_xpath = fields_yaml['session_amenities']
    del fields_yaml['wait_fields']
    del fields_yaml['session_amenities']


    fc.change_page(browser, url_airbnb)

    dict_links_announcement = {}
    dict_links_pages = {}

    page_number = 1
    dict_links_announcement = fc.get_links_announcement(browser, page_number, dict_links_announcement)
    dict_links_pages[page_number] = url_airbnb
    dict_links_pages = fc.get_links_pages(browser, dict_links_pages)
    ls_pages = fc.get_pages_available(dict_links_pages)

    last_page = ls_pages[-1]
    last_sequencial_page = fc.get_last_page_sequencial(ls_pages)

    while page_number < last_page:
        print(f"Scrapping page: {page_number}")
        page_number +=1 
        if page_number == last_sequencial_page:
            link = dict_links_pages[page_number]
            fc.change_page(browser, link)
            dict_links_announcement = fc.get_links_announcement(browser, page_number, dict_links_announcement)
            dict_links_pages = fc.get_links_pages(browser, dict_links_pages)
            ls_pages = fc.get_pages_available(dict_links_pages)
            last_sequencial_page = fc.get_last_page_sequencial(ls_pages)
        else:
            link = dict_links_pages[page_number]
            fc.change_page(browser, link)
            dict_links_announcement = fc.get_links_announcement(browser, page_number, dict_links_announcement)

    ls_dicts_announcement = []
    ls_dicts_amenities = []
    for page in ls_pages:
        announcement_number = 1
        for anuncio in dict_links_announcement[page][0:2]:
            browser.get(anuncio)
            id_anuncio = fc.generate_id_announcement(page, announcement_number, location)

            ls_return = fc.scrap_page(browser, wait_fields, fields_yaml, pop_up_state)
            dict_scrap = ls_return[0]
            pop_up_state = ls_return[1]
            dict_scrap['link'] = link
            dict_scrap['id_anuncio'] = id_anuncio 
            ls_dicts_announcement.append(dict_scrap)
            
            fc.click_button_amenities(browser)
            dict_acomodidade = fc.find_amenities(browser, session_xpath)
            dict_acomodidade['id_anuncio'] = id_anuncio
            ls_dicts_amenities.append(dict_acomodidade)
            
            announcement_number += 1

    df_announcement = fc.generate_dataframe_announcement(ls_dicts_announcement, location, date_start, date_end, adults, children, infants, pets, schema_json)
    df_announcement = fc.column_first_index(df_announcement)
    df_announcement['create_date'] = today_date
    df_amenities = fc.generate_df_amenities(ls_dicts_amenities)
    df_amenities = fc.column_first_index(df_amenities)
    df_amenities['create_date'] = today_date

    anuncio_file_name = f"anuncio_location({location})_date_start({date_start})_date_end({date_end})_{today_date}.parquet"
    anuncio_file_temp_path = f"{temp_dir.name}/anuncio.parquet"
    acomodidades_file_name = f"comodidades_location({location})_date_start({date_start})_date_end({date_end})_{today_date}.parquet"
    acomodidades_file_temp_path = f"{temp_dir.name}/acomodidades.parquet"

    df_announcement.to_parquet(anuncio_file_temp_path, index=False)
    df_amenities.to_parquet(acomodidades_file_temp_path, index=False)

    cloud_storage.upload_object(bucket_name , anuncio_file_name, anuncio_file_temp_path, 'anuncios')
    cloud_storage.upload_object(bucket_name , acomodidades_file_name, acomodidades_file_temp_path, 'acomodidades')

    print('Webscraping executed with Sucess')

if __name__ == "__main__":
    main()