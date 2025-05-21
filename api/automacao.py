from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import joblib
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import keyboard
import json
from api.service.config_service import obter_configuracao_texto
from typing import Optional
from api.schemas.pallet_schema import *
from typing import Dict, Any

class GvsSystem:
    def __init__(
        self,
        usuario: Optional[str] = None,
        senha: Optional[str] = None,
        url_base: Optional[str] = None,
        path_cookies: str = 'sessao.pkl',
        server: Optional[str] = None
    ):
        # Carrega as configurações do banco apenas se não forem passadas
        self.url_base = url_base or obter_configuracao_texto("url_base") or "http://192.168.1.114"
        self.usuario = usuario or obter_configuracao_texto("usuario")
        self.senha = senha or obter_configuracao_texto("senha")

        self.url_login = self.url_base + "/admin/login"
        self.cookies = []
        self.caminho_cookies = self.obter_caminho_cookies(path_cookies)    
        self.driver = None
        self.server = server

    def __del__(self):
        self.fechar_driver()
    

    def iniciar_driver(self):
        if not self.driver:
            options = webdriver.ChromeOptions()
            
            if self.server:
                preferencias_do_chrome = {
                    'printing.print_preview_sticky_settings.appState': json.dumps({
                        "recentDestinations": [{"id": "ZEBRA 2", "origin": "local"}],
                        "selectedDestinationId": "ZEBRA 2",
                        "version": 2,
                        "scalingType": 3,
                        "scaling": "93"  # Escalonamento específico para servidor remoto
                    }),
                    'savefile.default_directory': 'C:\\WebDriver\\impressoes'
                }
            else:
                preferencias_do_chrome = {
                    'printing.print_preview_sticky_settings.appState': json.dumps({
                        "recentDestinations": [{"id": "ZEBRA 2", "origin": "local"}],
                        # "recentDestinations": [{"id": "PALLETS", "origin": "local"}],
                        "selectedDestinationId": "PALLETS",
                        "version": 2,
                        "scalingType": 3,
                        "scaling": "93"  # Escalonamento específico para execução local
                    }),
                    'savefile.default_directory': '/path/to/save'
                }

            options.add_experimental_option('prefs', preferencias_do_chrome)
            options.add_argument('--kiosk-printing')
            
            if self.server:
                self.driver = webdriver.Remote(
                    command_executor=self.server, 
                    options=options
                )
            else:
                self.driver = webdriver.Chrome(options=options)

            self.driver.implicitly_wait(10)


    def fechar_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def fazer_login(self):
        self.iniciar_driver()
        if os.path.exists(self.caminho_cookies):
            self.driver.get(self.url_login)
            self.carregar_cookies()
            self.driver.refresh()
        else:
            self.realizar_login()


    def realizar_login(self):
            self.driver.get(self.url_login)
            self.driver.find_element(By.ID,'username').send_keys(self.usuario)
            self.driver.find_element(By.ID,'password').send_keys(self.senha)
            self.driver.find_element(By.XPATH ,'//*[@id="formulario_login"]/button').click()
            self.cookies = self.driver.get_cookies()
            self.salvar_cookies()


    def carregar_cookies(self):
        cookies = joblib.load(self.caminho_cookies)

        # Verifica se todos os cookies estão válidos
        cookies_validos = all(cookies[0]['expiry'] > datetime.now().timestamp() for cookie in cookies)

        if cookies_validos:
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.cookies = cookies
        else:
            self.realizar_login()


    def salvar_cookies(self):
        joblib.dump(self.cookies, self.caminho_cookies)


    def obter_caminho_cookies(self, path_cookies):
        # Obtendo o diretório de trabalho atual
        pasta_raiz = os.getcwd()
        return os.path.join(pasta_raiz, path_cookies)


    def preencher_input_xpath_com_texto(self, xpath, texto):
        sleep(1)
        try:
            input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            # Faça algo com o elemento após ele ser localizado
            input.clear()
            input.send_keys(texto)
            if texto =="White Seedless":
                input.send_keys(Keys.DOWN)
                
            input.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}")


class RegistroPalletManager(GvsSystem):
    def __init__(
        self,
        usuario: Optional[str] = None,
        senha: Optional[str] = None,
        url_base: Optional[str] = None,
        path_cookies: str = 'sessao.pkl',
        server: Optional[str] = None
    ):
        super().__init__(usuario, senha, url_base, path_cookies, server)

        self.url_registro_pallets = self.url_base + '/admin/registroPallet'
        self.lista_pallets = []
        self.lista_pallets_id = []
        self.pallet: Optional[RegistroPallet] = None

    def realizar_lancamento_pallet(self, registro: RegistroPallet, imprimir_etiqueta=True):
        self.fazer_login()
        self.pallet = registro

        self.cabecalho_pallet()
        self.save()
        for item in registro.itens:
            self.montagem_pallet(item)
            self.save()
            sleep(3)

            pallet_id = self.driver.find_element(By.ID, "registroPalletID").get_attribute("value")
            self.lista_pallets_id.append(pallet_id)

            if imprimir_etiqueta:
                self.imprimir_etiqueta(pallet_id)

    def realizar_lancamento_pallets(self, dados: List[dict], imprimir_etiqueta=True):
        for data in dados:
            registro = self.criar_registro_pallet(data)
            self.realizar_lancamento_pallet(registro, imprimir_etiqueta)

    @staticmethod
    def criar_registro_pallet(data: Dict[str, Any]) -> RegistroPallet:
        cabecalho = CabecalhoPallet(**data["cabecalho"])
        itens = [ItemPallet(**item) for item in data["itens"]]
        return RegistroPallet(cabecalho=cabecalho, itens=itens)

    def selecionar_opcao_por_index(self, elemento, index):
        Select(elemento).select_by_index(index)

    def selecionar_opcao_por_value(self, elemento, value):
        Select(elemento).select_by_value(str(value))

    def cabecalho_pallet(self):
        cab = self.pallet.cabecalho

        self.driver.get(self.url_registro_pallets)
        self.driver.find_element(By.XPATH, '//*[@id="mainHeaderRigth"]/div/button/i').click()

        self.selecionar_opcao_por_index(self.driver.find_element(By.NAME, 'categoria_id'), 3)
        self.selecionar_opcao_por_value(self.driver.find_element(By.NAME, 'embalagem_id'), cab.tipo_de_caixa)
        self.selecionar_opcao_por_value(self.driver.find_element(By.NAME, 'local_estoque_id'), cab.local_de_estoque)
        self.selecionar_opcao_por_value(self.driver.find_element(By.NAME, 'cliente_item_id'), cab.cliente)
        self.selecionar_opcao_por_value(self.driver.find_element(By.NAME, 'produto_id'), cab.des_produto)
        self.selecionar_opcao_por_value(self.driver.find_element(By.NAME, 'etiqueta_id'), cab.tipo_de_etiqueta)
        self.selecionar_opcao_por_value(self.driver.find_element(By.NAME, 'processo_interno'), cab.processo_interno)

        nome_do_pallet = self.driver.find_element(By.ID, 'registroPalletCodPallet').get_attribute('value')
        self.lista_pallets.append(nome_do_pallet)

    def montagem_pallet(self, item: ItemPallet):
        novo_item_btn = self.driver.find_element(By.XPATH, '//*[@id="registroPalletManagementId"]/div[2]/div/div[3]/span/button[1]')
        self.driver.execute_script("arguments[0].scrollIntoView();", novo_item_btn)
        novo_item_btn.click()

        sleep(1)
        self.selecionar_opcao_por_value(self.driver.find_element(By.NAME, 'produtor_id'), "255")
        sleep(2)
        self.selecionar_opcao_por_value(self.driver.find_element(By.NAME, 'esteira_id'), item.esteira)

        self.driver.find_element(By.ID, 'select2-registroPalletItemLatada-container').click()
        latada_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/span/span/span[1]/input"))
        )
        latada_input.send_keys(item.latada)
        latada_input.send_keys(Keys.ENTER)

        self.driver.find_element(By.ID, 'registroPalletItemQuantidade').send_keys(str(item.q_caixas))

        self.driver.find_element(By.ID, 'select2-registroPalletItemColor-container').click()
        cor_input = self.driver.find_element(By.XPATH, '/html/body/span/span/span[1]/input')
        cor_input.send_keys(item.cor)
        cor_input.send_keys(Keys.ENTER)

        self.driver.find_element(By.ID, 'select2-registroPalletItemCalibre-container').click()
        calibre_input = self.driver.find_element(By.XPATH, '/html/body/span/span/span[1]/input')
        calibre_input.send_keys(str(item.calibre))
        calibre_input.send_keys(Keys.ENTER)

        self.driver.find_element(By.ID, 'select2-registroPalletItemBrix-container').click()
        brix_input = self.driver.find_element(By.XPATH, '/html/body/span/span/span[1]/input')
        brix_input.send_keys(str(item.brix))
        brix_input.send_keys(Keys.ENTER)

        if item.observacoes:
            observacoes = self.driver.find_element(By.NAME, "situacao_fruta_ajuda1")
            Select(observacoes).select_by_visible_text(item.observacoes)


class Cabines(GvsSystem):
    def __init__(self, usuario, senha, servidor_remoto=None):
        super().__init__(usuario, senha, path_cookies='sessao.pkl', server=servidor_remoto)
        self.url_etiqueta_rendimento = self.url_base + "/admin/etiquetaRendimentoPacking"

    def preencher(self, data):
        self.fazer_login()
        self.driver.get(self.url_etiqueta_rendimento)
        self.preencher_input_xpath_com_texto('//*[@id="vs1__combobox"]/div[1]/input', data.variedades)
        self.preencher_input_xpath_com_texto('//*[@id="vs2__combobox"]/div[1]/input', data.classificacao)
        self.preencher_input_xpath_com_texto('//*[@id="vs3__combobox"]/div[1]/input', data.peso)
        self.preencher_input_xpath_com_texto('//*[@id="app"]/div/div[2]/form/div[4]/input', data.totalEtiquetas)
        self.preencher_input_xpath_com_texto('//*[@id="vs4__combobox"]/div[1]/input', data.modeloEtiquetas)
        self.select_options_cabines(data.cabines)
        self.save()
    
    def select_options_cabines(self, options):
        # Localize o campo de busca
        search_input = self.driver.find_element(By.CSS_SELECTOR, '.msl-search-list-input')
        
        for option in options:
            # Limpe o campo de busca
            search_input.clear()
            
            # Digite o nome da opção
            search_input.send_keys(option)
            sleep(0.5)  # Espere um pouco para garantir que a lista seja atualizada
            
            # Selecione a opção da lista de resultados
            option_element = self.driver.find_element(By.XPATH, f"//div[contains(text(), '{option}')]")
            option_element.click()
            sleep(0.2)

    def save(self):
        btn_salvar = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/form/div[7]/span/button')
        try:
            # Role a página para que o elemento fique visível
            self.driver.execute_script("arguments[0].scrollIntoView();", btn_salvar)

            # Clique no elemento
            btn_salvar.click()
            link = self.criar_link()
            self.imprimir_codigo_cabine(link)
            
        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}")


    def criar_link(self):
        return self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[2]/iframe').get_attribute("src")
    

    def imprimir_codigo_cabine(self, link):
        self.driver.get(link)
        sleel(10)
        self.driver.execute_script("window.print();")
        sleep(5)
