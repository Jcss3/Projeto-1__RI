#!/usr/bin/env python
# coding: utf-8

# # Bibliotecas

# In[ ]:


import pandas as pd
import numpy as np
import scipy as scp
from bs4 import BeautifulSoup
import requests as rq
import re
from requests.exceptions import HTTPError
import urllib
from selenium import webdriver
from reppy.robots import Robots
from urllib.parse import urlparse
import time


# # Crawler

# In[12]:


Dominio = ['https://www.capefeargames.com/','https://www.mtgotraders.com/',
           'https://www.wizardscupboard.com/','https://abugames.com/',
           'https://www.cardkingdom.com/','http://www.starcitygames.com/',
           'https://www.tcgplayer.com/','https://scryfall.com/']

#paginasVisitadas = []
Dados = []


# In[13]:


# Função para marcar a page como visitada.
def Visitou (url):
    if url not in paginasVisitadas:
        return False
    else:
        return True


# In[14]:


# Função para verificar se a requisição sofreu algum problema.
def verificarRequest(url):
    try:
        response = rq.head(url)
        # O response retornou alguma conexao valida.
        response.raise_for_status()

    except HTTPError as http_err:
        #print(f'HTTP error occurred: {http_err}')
        return False
    except Exception as err:
        #print(f'Other error occurred: {err}')
        return False
    return True


# In[15]:


def CrawlerDinâmico(url):
    #C:\\Users\\Usuário\\Downloads\\chromedriver76\\chromedriver.exe 
    driver = webdriver.Chrome("C:\\Users\\Usuário\\Downloads\\chromedriver76\\chromedriver.exe")
    driver.get(url)
    res = driver.execute_script("return document.documentElement.outerHTML")
    driver.quit
    return res


# In[16]:


#Função para Verificar se podemos baixar a page ou não
def verificarRobotTxt(url):
    robots = Robots.fetch(url + '/robots.txt')
    return robots.allowed(url, '*')


# In[17]:


verificarRobotTxt(Dominio[0])


# In[18]:


# Criar uma Tabela com as informações sobre links.
def Tabela(count,url,site):
    Dados.append(dict(zip(['Número','Link','Site'],[count,url,site])))


# ## * Baseline

# In[19]:


def CardsCrawler(url):
    print('Dominio: ' + url.geturl())
    count = 0
    paginas = [url]
    paginasVisitadas = []
    robots = Robots.fetch(url.geturl() + '/robots.txt')
    while count < 1000 and len(paginas) > 0:
        count = count + 1
        primeiraPagina = paginas.pop(0)
        print(count,'-',primeiraPagina.geturl(),' Qtd Paginas=', len(paginas))
       
        # Verifica se a pagina foi visitada.Se foi, procuro o proximo link da lista que não foi visitado.
        # Verifico se o hostname de cada pagina é igual ao do dominio, se não, rocuro o proximo link da lista (navegar apenas dentro do site)
        # Verifico se hostname existe , se não , procuro o proximo link que tenha.
        # Verifico se é possivel crawlear a pagina de acordo com as regras do robot.txt , se não , procuro o proximo link.
        while Visitou(primeiraPagina) == True or primeiraPagina.hostname != url.hostname or primeiraPagina.hostname == None or robots.allowed(primeiraPagina.geturl(), '*') == False:
            if len(paginas) == 0:
                print('lascou@!')
                return
            primeiraPagina = paginas.pop(0)
        
        # verificar se a requisição funciana.
        if verificarRequest(primeiraPagina.geturl()) == True:

            # Verficar se o site é dinamico.
            if (Dominio[3] in url.geturl()) or (Dominio[6] in url.geturl()):
                texto = CrawlerDinâmico(primeiraPagina.geturl())
            else:
                #request - usando o content type
                codigo_fonte = rq.get(primeiraPagina.geturl(),headers={'content-type': 'text/html'})
                # texto do codigo_fonte.
                texto = codigo_fonte.text
            soup = BeautifulSoup(texto,'html.parser')

            # Encontrar todos os links da pagina(url). # attrs={'href': re.compile("^http://")}
            for link in soup.findAll('a'):
                href = link.get('href')
                # Correção de href relativos para absolutos.
                href = urllib.parse.urljoin(url.geturl(),href)
                paginas.append(urlparse(href))

            # Marco como visitada a urlparse    
            paginasVisitadas.append(primeiraPagina)
            #esperar 300 milisegundos para visitar o prox link.
            time.sleep(.300)

        else:
            print('Requisição falhou!')
        
        Tabela(count,primeiraPagina.geturl(),url.hostname)


# In[ ]:


from multiprocessing import Pool
def Potencia(numero):
    print(numero*numero)
    
n = [1,2,3,4,5,6]
p = Pool()
result = p.map(Potencia,n)
print(result)
p.close()
p.join()


# In[ ]:


for url in Dominio:
    inicio = time.time()
    CardsCrawler(urlparse(url))
    fim = time.time()
    print('Tempo do Site: ',fim - inicio, 'Site: ', url)


# ### Tabela com informações do Crawler Baseline

# In[ ]:


data = pd.DataFrame(Dados,columns=['Número','Link','Site'])
data


# In[ ]:





# ## * Heurística
