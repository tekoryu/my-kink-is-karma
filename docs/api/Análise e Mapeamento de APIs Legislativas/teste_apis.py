#!/usr/bin/env python3
"""
Script para testar as APIs do Senado Federal e da Câmara dos Deputados
"""

import requests
import json
import time

def testar_api_senado(id_processo):
    """
    Testa a API do Senado Federal para um processo específico
    """
    print(f"=== Testando API do Senado Federal ===")
    print(f"ID do Processo: {id_processo}")
    
    # URL base da API do Senado
    url_base = "https://legis.senado.leg.br/dadosabertos"
    
    # Endpoint para detalhes do processo
    url = f"{url_base}/processo/{id_processo}"
    
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"Fazendo requisição para: {url}")
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers de resposta: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("=== Resposta JSON ===")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # Tentar mapear os campos necessários
                print("\n=== Mapeamento de Campos ===")
                mapear_campos_senado(data)
                
            except json.JSONDecodeError:
                print("Resposta não é JSON válido:")
                print(response.text[:1000])
        else:
            print(f"Erro na requisição: {response.status_code}")
            print(response.text[:500])
            
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")

def mapear_campos_senado(data):
    """
    Mapeia os campos necessários da resposta da API do Senado
    """
    print("Tentando mapear campos:")
    
    # Autor do processo
    autor = "Não encontrado"
    data_apresentacao = "Não encontrada"
    id_processo = "Não encontrado"
    
    # Aqui tentaremos diferentes caminhos possíveis baseados na estrutura comum
    # dos dados do Senado
    
    if isinstance(data, dict):
        # Possíveis caminhos para o autor
        if 'Autoria' in data:
            if isinstance(data['Autoria'], list) and len(data['Autoria']) > 0:
                primeiro_autor = data['Autoria'][0]
                if 'Autor' in primeiro_autor:
                    autor = primeiro_autor['Autor'].get('NomeParlamentar', 
                                                       primeiro_autor['Autor'].get('Nome', autor))
        
        # Possíveis caminhos para data de apresentação
        if 'DadosBasicos' in data:
            data_apresentacao = data['DadosBasicos'].get('DataApresentacao', data_apresentacao)
        elif 'DataApresentacao' in data:
            data_apresentacao = data['DataApresentacao']
            
        # ID do processo
        if 'Identificacao' in data:
            id_processo = data['Identificacao'].get('CodigoProcesso', 
                                                   data['Identificacao'].get('CodigoMateria', id_processo))
        elif 'CodigoProcesso' in data:
            id_processo = data['CodigoProcesso']
    
    print(f"- Autor: {autor}")
    print(f"- Data de Apresentação: {data_apresentacao}")
    print(f"- ID do Processo: {id_processo}")

def testar_api_camara(id_proposicao):
    """
    Testa a API da Câmara dos Deputados para uma proposição específica
    """
    print(f"\n=== Testando API da Câmara dos Deputados ===")
    print(f"ID da Proposição: {id_proposicao}")
    
    # URL base da API da Câmara
    url_base = "https://dadosabertos.camara.leg.br/api/v2"
    
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Testar endpoint de detalhes da proposição
    url_detalhes = f"{url_base}/proposicoes/{id_proposicao}"
    
    try:
        print(f"Fazendo requisição para: {url_detalhes}")
        response = requests.get(url_detalhes, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("=== Resposta JSON (Detalhes) ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Mapear campos
            print("\n=== Mapeamento de Campos (Detalhes) ===")
            mapear_campos_camara_detalhes(data)
            
        else:
            print(f"Erro na requisição de detalhes: {response.status_code}")
            print(response.text[:500])
            
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição de detalhes: {e}")
    
    # Testar endpoint de autores
    url_autores = f"{url_base}/proposicoes/{id_proposicao}/autores"
    
    try:
        print(f"\nFazendo requisição para: {url_autores}")
        response = requests.get(url_autores, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("=== Resposta JSON (Autores) ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Mapear campos
            print("\n=== Mapeamento de Campos (Autores) ===")
            mapear_campos_camara_autores(data)
            
        else:
            print(f"Erro na requisição de autores: {response.status_code}")
            print(response.text[:500])
            
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição de autores: {e}")

def mapear_campos_camara_detalhes(data):
    """
    Mapeia os campos necessários da resposta de detalhes da API da Câmara
    """
    print("Tentando mapear campos dos detalhes:")
    
    autor = "Não encontrado"
    data_apresentacao = "Não encontrada"
    id_proposicao = "Não encontrado"
    
    if isinstance(data, dict):
        # Dados básicos
        dados = data.get('dados', data)
        
        # ID da proposição
        id_proposicao = dados.get('id', id_proposicao)
        
        # Data de apresentação
        data_apresentacao = dados.get('dataApresentacao', data_apresentacao)
        
        # Autor (pode estar nos detalhes ou precisar do endpoint separado)
        if 'autor' in dados:
            autor = dados['autor']
        elif 'autores' in dados:
            if isinstance(dados['autores'], list) and len(dados['autores']) > 0:
                autor = dados['autores'][0].get('nome', autor)
    
    print(f"- Autor: {autor}")
    print(f"- Data de Apresentação: {data_apresentacao}")
    print(f"- ID da Proposição: {id_proposicao}")

def mapear_campos_camara_autores(data):
    """
    Mapeia os campos de autores da API da Câmara
    """
    print("Tentando mapear campos dos autores:")
    
    autores = []
    
    if isinstance(data, dict):
        dados = data.get('dados', data)
        
        if isinstance(dados, list):
            for autor in dados:
                nome = autor.get('nome', 'Nome não encontrado')
                autores.append(nome)
    
    print(f"- Autores: {', '.join(autores) if autores else 'Não encontrados'}")

if __name__ == "__main__":
    print("Script de teste das APIs Legislativas")
    print("=====================================")
    
    # IDs de exemplo (serão substituídos pelos IDs reais fornecidos)
    id_processo_senado = 1326805
    id_proposicao_camara = 2056568  # ID de exemplo da Câmara
    
    if id_processo_senado:
        testar_api_senado(id_processo_senado)
        time.sleep(2)  # Pausa entre requisições
    else:
        print("ID do processo do Senado não fornecido ainda.")
    
    print("\n" + "="*50)
    testar_api_camara(id_proposicao_camara)

