import pandas as pd
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import json
import time
import numpy as np

def get_links_announcement(browser, page_number, dict_links_announcement):
    ls_links = browser.find_elements(By.XPATH, '//*[@id="site-content"]/div/div[2]/div/div/div/div/div[1]/div/div/div[2]/div/div/div/div/a')
    ls_links = list(map(lambda element : element.get_attribute('href') , ls_links))
    dict_links_announcement[page_number] = ls_links
    return dict_links_announcement

def get_links_pages(browser, dict_links_pages):
    element_pages = browser.find_element(By.XPATH, '//*[@id="site-content"]/div/div[3]/div/div/div/nav/div')
    ls_element_pages = element_pages.find_elements(By.TAG_NAME, 'a')
    for element in ls_element_pages:
        chave = element.text 
        valor = element.get_attribute('href')
        if chave != '':
            dict_links_pages[int(chave)] =  valor
    return dict_links_pages 

def get_pages_available(dict_links_pages):
    ls_pages = list(dict_links_pages.keys())
    ls_pages = list(map(lambda element : element, ls_pages))
    ls_pages.sort()
    return ls_pages

def get_last_page_sequencial(ls_pages):
    for index in range(1, len(ls_pages)):
        element_list = ls_pages[index]
        if index > 1:
            last_index = index - 1
            element_list_before = ls_pages[last_index]
            if (element_list - 1) == element_list_before:
                last_page_link = element_list
    return last_page_link

def change_page(browser, url):
    browser.get(url)
    wait = WebDriverWait(browser, 20) 
    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="site-content"]/div/div[2]/div/div/div/div/div[1]/div/div/div[2]/div/div/div/div/a')))
    time.sleep(5)

def pop_up_translation(browser, pop_up_state):
    try:
        wait = WebDriverWait(browser, 5)
        wait.until(EC.presence_of_element_located((By.XPATH, '//h1[contains(text(), "Tradu")]/../..')))
        browser.find_element(By.XPATH, '//h1[contains(text(), "Tradu")]/../..')
        print('encontrou pop up')
        try:
            # click_exit = browser.find_element(By.XPATH, '/html/body/div[9]/div/div/section/div/div/div[2]/div/div[1]/button')
            # click_exit.click()
            webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
            print('clicou no botao sair')
            pop_up_state = False
            return pop_up_state
        except:
            print('Nao foi Possivel clicar')
            return pop_up_state
    except:
        print('Nao encontrado pop up tradução ativa')
        return pop_up_state
        
def find_element_safe(browser, by, xpath, default="Não encontrado"):
    try:
        element = browser.find_element(by, xpath).text
    except NoSuchElementException:
        element = default
    return element

def scrap_page(browser, wait_fields, fields_yaml, pop_up_state):
    #global pop_up_state
    if pop_up_state:
        pop_up_translation(browser, pop_up_state)
    for element in wait_fields:
        try:
            element_xpath = fields_yaml[element]
            wait = WebDriverWait(browser, 20)
            wait.until(EC.presence_of_element_located((By.XPATH, element_xpath)))
        except:
            print(f"Timeout on no campo de Espera: {element}")

    time.sleep(5)
    dict_scrap = {}
    for key, value in fields_yaml.items():
        text_element = find_element_safe(browser, By.XPATH, value)
        text_element = text_element.split('\n')[-1]
        dict_scrap[key] = text_element
    return [dict_scrap, pop_up_state]

def find_amenities(browser, session_xpath):
    try:
        wait = WebDriverWait(browser, 7)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, session_xpath)))
    except:
        print('Nao foi possicel encontrar a sessão')
        return {}
    time.sleep(5)
    xpath_amenities = session_xpath
    session_amenities = browser.find_element(By.XPATH, xpath_amenities)

    ls_titles = session_amenities.find_elements(By.TAG_NAME, 'h3')
    ls_titles = list(map( lambda element: element.text, ls_titles)) 

    ls_ul_amenities = session_amenities.find_elements(By.TAG_NAME, 'ul')
    ls_ul_amenities = list(map( lambda element : element.find_elements(By.TAG_NAME, 'li'), ls_ul_amenities))
    ls_sub_itens = []
    for element in ls_ul_amenities:
        element = list(map( lambda ele: ele.text.split('\n')[0], element))
        ls_sub_itens.append(element)

    dict_amenities = {}
    for index in range(len(ls_titles)):
        title = ls_titles[index]
        sub_itens = ls_sub_itens[index]
        dict_amenities[title] = sub_itens

    dict_amenities = {
        "Titulo" : list(map(lambda element: element, dict_amenities.keys())),
        "Sub-item" : list(map(lambda element: element, dict_amenities.values()))
    }
    return dict_amenities

def click_button_amenities(browser):
    try:
        wait = WebDriverWait(browser, 20)
        wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Mostrar todas as")]')))
        button = browser.find_element(By.XPATH, '//button[contains(text(), "Mostrar todas as")]')
        browser.execute_script("arguments[0].scrollIntoView(true);", button)
        browser.implicitly_wait(3)
        browser.execute_script("window.scrollBy(0, -200);")
        browser.implicitly_wait(3)
        button.click()
    except:
        print('Nao foi possivel clicar no botao')

def generate_id_announcement(page, announcement_number, location):
    string_concatenated = f"{str(page)}{str(announcement_number)}{location}{str(datetime.today())}"
    index = hash(string_concatenated)
    return index

def generate_dataframe_announcement(ls_dicts_announcement, location, date_start, date_end, adults, children, infants, pets, schema_json ):
    dataframe = pd.DataFrame(ls_dicts_announcement)

    dataframe = dataframe.replace('Não encontrado', None)
    def treat_note(df):
        try:
            note1 = float(str(df['nota_local1']).replace(',','.'))
            return note1
        except:
            try:
                note2 = float(str(df['nota_local2']).replace(',','.'))
                return note2
            except:
                return None 
            
    dataframe['nota'] = dataframe.apply(treat_note, axis=1)
    def treat_commentary(df):
        try:
            comment1 = int(str(df['qtde_comentarios_local1']).replace('comentários','').replace('comentário',''))
            return comment1
        except:
            try:
                comment2 = int(str(df['qtde_comentarios_local2']).replace('comentários','').replace('comentário',''))
                return comment2
            except:
                return None 

    dataframe['comentario'] = dataframe.apply(treat_commentary, axis=1)
    dataframe.drop(columns=['nota_local1', 'nota_local2', 'qtde_comentarios_local1', 'qtde_comentarios_local2'], inplace=True)

    #Resolvendo as taxas, calculando o valor por noite 
    columns_values = ['taxa_servico', 'desconto', 'taxa_limpeza', 'total']
    for column in columns_values:
        dataframe[column] = dataframe[column].apply(lambda linha : str(linha).replace('R$', '').replace('-', '').replace('None', '0').replace('.','').replace('.',''))
        dataframe[column] = dataframe[column].replace('',  np.nan).astype('float64')
        dataframe[column] = dataframe[column].apply(lambda linha : float(str(linha).replace('R$', '').replace('-', '').replace('None', '0').replace('.','').replace('.','')))

    dataframe['location'] = location
    dataframe['date_start'] = date_start
    dataframe['date_end'] = date_end
    dataframe['adults'] = adults
    dataframe['children'] = children
    dataframe['infants'] = infants
    dataframe['pets'] = pets

    def calculate_daily(dataframe):
        total = dataframe['total']
        date_start = datetime.strptime(dataframe['date_start'], "%Y-%m-%d")
        date_end = datetime.strptime(dataframe['date_end'], "%Y-%m-%d")
        daily = (date_end - date_start).days -1
        daily_rate = total/daily
        return daily_rate

    dataframe['diaria'] = dataframe.apply(calculate_daily, axis=1)

    dataframe = dataframe.astype(schema_json)
    return dataframe

def generate_df_amenities(ls_dicts_amenities):
    df_amenities = pd.DataFrame(ls_dicts_amenities)
    df_amenities = df_amenities.explode(['Titulo', 'Sub-item'])
    df_amenities = df_amenities.explode('Sub-item')
    return df_amenities

def column_first_index(dataframe):
    ls_colunas = list(dataframe.columns.copy())
    ls_colunas.remove('id_anuncio')
    ls_colunas.insert(0,'id_anuncio')
    return dataframe[ls_colunas]