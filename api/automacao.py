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


class RegistroPallet(GvsSystem):
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
        self.pallet = {}

    def realizar_lancamento_pallet(self, pallet, imprimir_etiqueta=True):
        self.fazer_login()
        self.atualizar_campos(pallet)
        for a in range(self.pallet['quantidade_pallets']):
            self.cabecalho_pallet()
            self.save()
            for a_latada, a_q_caixas, observacao in zip(self.pallet['list_latadas'], self.pallet['list_q_caixas'], self.pallet['observacoes']):
                self.montagem_pallet(a_latada, a_q_caixas, observacao)
                self.save()
                sleep(3)

            # Esperando página carregar para encontrar o id
            self.pallet['id'] = self.driver.find_element(By.ID , "registroPalletID").get_attribute("value")
            self.lista_pallets_id.append(self.pallet['id'])

            if imprimir_etiqueta:
                self.imprimir_etiqueta(self.pallet['id'])

    def realizar_lancamento_pallets(self, pallets, imprimir_etiqueta=True):
        if isinstance(pallets, pd.DataFrame):
            pallets.dropna(inplace=True)
            for col in pallets.select_dtypes('number').columns:
                pallets[col] = pallets[col].astype('int')

            for index, pallet in pallets.iterrows():
                self.realizar_lancamento_pallet(pallet, imprimir_etiqueta)


    def atualizar_campos(self, pallet):
        self.pallet['t_embalagem'] = str(pallet["tipo_de_caixa"])
        self.pallet['des_prod'] = str(pallet["des_produto"])
        self.pallet['cliente'] = str(pallet["cliente"])
        self.pallet['etiqueta'] = str(pallet["tipo_de_etiqueta"])
        self.pallet['esteira'] = str(pallet["esteira"])
        self.pallet['list_latadas'] = str(pallet["latada"]).split("+")
        self.pallet['list_q_caixas'] = str(pallet["q_caixas"]).split("+")
        self.pallet['cor'] = str(pallet["cor"])
        self.pallet['calibre'] = str(pallet["calibre"])
        self.pallet['brix'] = str(pallet["brix"])
        self.pallet['quantidade_pallets'] = int(pallet["q_pallets"])
        self.pallet['processo_interno'] = str(pallet["processo_interno"])
        self.pallet['local_de_estoque'] = str(pallet["local_de_estoque"])
        self.pallet['observacoes'] = str(pallet['observacoes']).split("+")

    def selecionar_opcao_por_index(self, elemento, index):
        select = Select(elemento)
        select.select_by_index(index)


    def selecionar_opcao_por_value(self, elemento, value):
        select = Select(elemento)
        select.select_by_value(value)


    def cabecalho_pallet(self):
        # lancamento do pallet
        self.driver.get(self.url_registro_pallets)
        self.driver.find_element(By.XPATH , '//*[@id="mainHeaderRigth"]/div/button/i').click()

        # Tipo de Fruta padrão igual a UVA: 3
        tipo_de_fruta = self.driver.find_element(By.NAME , 'categoria_id')
        self.selecionar_opcao_por_index(tipo_de_fruta, 3)

        tipo_de_embalagem = self.driver.find_element(By.NAME , 'embalagem_id')
        self.selecionar_opcao_por_value(tipo_de_embalagem, self.pallet['t_embalagem'])

        local_de_estoque = self.driver.find_element(By.NAME , 'local_estoque_id')
        self.selecionar_opcao_por_value(local_de_estoque, self.pallet['local_de_estoque'])

        cliente_exp = self.driver.find_element(By.NAME , 'cliente_item_id')
        self.selecionar_opcao_por_value(cliente_exp, self.pallet['cliente'])

        descricao = self.driver.find_element(By.NAME , 'produto_id')
        self.selecionar_opcao_por_value(descricao, self.pallet['des_prod'])

        etiqueta = self.driver.find_element(By.NAME , 'etiqueta_id')
        self.selecionar_opcao_por_value(etiqueta, self.pallet['etiqueta'])

        processo_interno = self.driver.find_element(By.NAME , 'processo_interno')
        self.selecionar_opcao_por_value(processo_interno, self.pallet['processo_interno'])

        nome_do_pallet = self.driver.find_element(By.ID , 'registroPalletCodPallet').get_attribute('value')
        self.lista_pallets.append(nome_do_pallet)


    def montagem_pallet(self, a_latada, a_q_caixas, observacao):
        novo_item = self.driver.find_element(By.XPATH, '//*[@id="registroPalletManagementId"]/div[2]/div/div[3]/span/button[1]')
        try:
            # Role a página para que o elemento fique visível
            self.driver.execute_script("arguments[0].scrollIntoView();", novo_item)

            # Clique no elemento
            novo_item.click()

        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}")

        # montagem do pallet
        produtor = self.driver.find_element(By.NAME , 'produtor_id')
        self.selecionar_opcao_por_value(produtor, "255")
        sleep(2)

        esteira = self.driver.find_element(By.NAME , 'esteira_id')
        self.selecionar_opcao_por_value(esteira, self.pallet['esteira'])

        self.driver.find_element(By.XPATH , '//*[@id="select2-registroPalletItemLatada-container"]').click()

        try:
            latada = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/span/span/span[1]/input"))
            )
            # Faça algo com o elemento após ele ser localizado
            latada.send_keys(a_latada)
            latada.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}")


        q_caixas = self.driver.find_element(By.XPATH ,  '//*[@id="registroPalletItemQuantidade"]')
        q_caixas.send_keys(a_q_caixas)

        self.driver.find_element(By.XPATH , '//*[@id="select2-registroPalletItemColor-container"]').click()
        cor = self.driver.find_element(By.XPATH , '/html/body/span/span/span[1]/input')
        cor.send_keys(self.pallet['cor'])
        cor.send_keys(Keys.ENTER)

        self.driver.find_element(By.XPATH , '//*[@id="select2-registroPalletItemCalibre-container"]').click()
        calibre = self.driver.find_element(By.XPATH , '/html/body/span/span/span[1]/input')
        calibre.send_keys(self.pallet['calibre'])
        calibre.send_keys(Keys.ENTER)

        self.driver.find_element(By.XPATH , '//*[@id="select2-registroPalletItemBrix-container"]').click()
        brix = self.driver.find_element(By.XPATH , '/html/body/span/span/span[1]/input')
        brix.send_keys(self.pallet['brix'])
        brix.send_keys(Keys.ENTER)

        if observacao:
            observacoes = self.driver.find_element(By.NAME , "situacao_fruta_ajuda1")
            select = Select(observacoes)
            select.select_by_visible_text(observacao)


    def save(self):
        btn_salvar = self.driver.find_element(By.CSS_SELECTOR, '.actionSave')
        try:
            # Role a página para que o elemento fique visível
            self.driver.execute_script("arguments[0].scrollIntoView();", btn_salvar)

            # Clique no elemento
            btn_salvar.click()

        except Exception as e:
            print(f"Ocorreu um erro: {str(e)}")


    def criar_link(self, id):
        return self.url_base + f"/admin/registroPallet/printOut/{id}/1"


    def imprimir_etiqueta(self, id):
        self.driver.get(self.criar_link(id))
        for i in range(2):
            self.driver.execute_script("window.print();")
            sleep(2)
            keyboard.press_and_release("enter")
            sleep(2)


    def imprimir_etiquetas(self):
        for id in self.lista_pallets_id:
            self.imprimir_etiqueta(id)


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
