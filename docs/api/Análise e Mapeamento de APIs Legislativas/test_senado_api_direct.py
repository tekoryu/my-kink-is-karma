import requests
import json

id_processo_senado = 1326805

# Tentativa com a URL base original
url_base_original = "https://legis.senado.leg.br/dadosabertos"
url_original = f"{url_base_original}/processo/{id_processo_senado}"

# Tentativa com a URL alternativa mencionada na documentação
url_base_alternativa = "https://www12.senado.leg.br/dadosabertos"
url_alternativa = f"{url_base_alternativa}/processo/{id_processo_senado}"

headers = {
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def make_request(url, name):
    print(f"\n=== Tentando {name} ===")
    print(f"URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print("Resposta JSON (primeiras 500 caracteres):")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
            except json.JSONDecodeError:
                print("Resposta não é JSON válido:")
                print(response.text[:500])
        else:
            print("Resposta não-200:")
            print(response.text[:500])
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")

make_request(url_original, "URL Base Original")
make_request(url_alternativa, "URL Base Alternativa")


