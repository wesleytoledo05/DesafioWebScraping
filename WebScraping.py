from bs4 import BeautifulSoup

import json
import requests
import re

# 1. Fazer uma requisição HTTP GET para o site do produto;
url = "https://infosimples.com/vagas/desafio/commercia/product.html"
response = requests.get(url)

# 2. Parsear o body HTML da resposta;
respostaFinal = {}
parseHtml = BeautifulSoup(response.content, "html.parser")

# 3. Extrair os dados necessários da página;

respostaFinal['titulo'] = parseHtml.select_one('h2#product_title').get_text()

respostaFinal['Marca'] = parseHtml.select_one('.brand').get_text()

categoriaProd = parseHtml.select('nav a')
categorias = []
for categoriaElemento in categoriaProd:
    categoria = categoriaElemento.get_text()
    categorias.append(categoria)
respostaFinal['categorias'] = categorias

descricao = ''
for pp in parseHtml.select('.proddet > p'):
    descricao += pp.text + '----------'
respostaFinal['Descricao'] = descricao

skusProd = parseHtml.select('.skus-area .card')
skus = []
for skuElemento in parseHtml.select('.skus-area .card'):
    sku = {}

    sku['nomeVariacao'] = skuElemento.find(class_='prod-nome').get_text()

    precoAtual = skuElemento.find(class_='prod-pnow')
    sku['precoAtual'] = float(precoAtual.get_text().replace(
        'R$', '').replace(',', '.')) if precoAtual else None

    precoAntigo = skuElemento.find(class_='prod-pold')
    sku['precoAntigo'] = float(precoAntigo.get_text().replace(
        'R$', '').replace(',', '.')) if precoAntigo else None

    sku['disponivel'] = 'not-avaliable' not in skuElemento.get('class', [])

    skus.append(sku)

respostaFinal['SKUS'] = skus


table = parseHtml.find('table')
propriedades = {}
for linha in table.find_all('tr'):
    campo = linha.find_all('td')
    if len(campo) == 2:
        nomeProp = campo[0].get_text().strip()
        textoProp = campo[1].get_text().strip()
        propriedades[nomeProp] = textoProp

respostaFinal['propriedades'] = propriedades


todasAvaliacoes = parseHtml.select('#comments .analisebox')
avaliacoes = []


todasAvaliacoes = parseHtml.select('#comments .analisebox')
avaliacoes = []
for avaliacaoElem in todasAvaliacoes:
    avaliacao = {}

    avaliacao['nomePessoa'] = avaliacaoElem.find(
        class_='analiseusername').get_text()

    avaliacao['dataAvaliacao'] = avaliacaoElem.find(
        class_='analisedate').get_text()

    estrelas = avaliacaoElem.find(class_='analisestars')
    avaliacao['estrelas'] = len(estrelas.find_all('svg'))

    avaliacao['textoAvaliacao'] = avaliacaoElem.find('p').get_text()

    avaliacoes.append(avaliacao)
respostaFinal['avaliacoes'] = avaliacoes


textoAvaliacao = parseHtml.select_one('#comments h4').get_text()
numDecimais = re.findall(r'\d+\.\d+', textoAvaliacao)
mediaAvaliacao = float(numDecimais[0]) if numDecimais else None
respostaFinal['mediaAvaliacoes'] = mediaAvaliacao

respostaFinal['urlProduto'] = url

# 4. Salvar os dados num arquivo produto.json.
jsonRespostaFinal = json.dumps(respostaFinal, ensure_ascii=False)
with open('produto.json', 'w', encoding='utf-8') as arquivoJson:
    arquivoJson.write(jsonRespostaFinal)
