# Resumo da Análise e Mapeamento de APIs Legislativas

Este documento apresenta a análise e o mapeamento dos endpoints e estruturas de dados das APIs do Senado Federal e da Câmara dos Deputados, com foco na extração de informações sobre processos legislativos, baseando-se exclusivamente na documentação fornecida e presumindo a correta funcionalidade dos endpoints.

## API 1 - Senado Federal

### Informações Gerais

- **URL Base**: `https://legis.senado.leg.br/dadosabertos/`
- **Autenticação**: Não requer autenticação (API pública).
- **Rate Limiting**: Máximo de 10 requisições por segundo (retorna HTTP 429 se excedido).
- **Formatos Suportados**: JSON, XML, CSV (conforme `Accept` header ou sufixo na URL).

### Endpoint de Busca de Processo Legislativo por ID

- **URL do Endpoint**: `https://legis.senado.leg.br/dadosabertos/processo/{id}`
- **Método HTTP**: `GET`
- **Exemplo de Requisição Completa (JSON)**:

  ```
  GET https://legis.senado.leg.br/dadosabertos/processo/1326805.json
  Accept: application/json
  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
  ```

### Mapeamento dos Campos de Dados

Com base no schema fornecido (`schema.json`), os campos necessários para um processo legislativo podem ser mapeados da seguinte forma:

- **Autor do processo**: `Processo.Autoria.Autor.NomeParlamentar` (ou `Processo.Autoria.Autor.Nome`)
- **Data de apresentação**: `Processo.DadosBasicos.DataApresentacao`
- **Identificador único do processo**: `Processo.Identificacao.CodigoProcesso`

## API 2 - Câmara dos Deputados

### Informações Gerais

- **URL Base**: `https://dadosabertos.camara.leg.br/api/v2/`
- **Autenticação**: Não requer autenticação (API pública).
- **Rate Limiting**: Não especificado um limite por segundo, mas listagens retornam 15 itens por padrão e o limite por requisição é de 100 itens.
- **Formatos Suportados**: JSON, XML.

### Endpoint de Busca de Proposição por ID

- **URL do Endpoint**: `https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id}`
- **Método HTTP**: `GET`
- **Exemplo de Requisição Completa (JSON)**:

  ```
  GET https://dadosabertos.camara.leg.br/api/v2/proposicoes/2056568
  Accept: application/json
  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
  ```

### Endpoint de Autores de Proposição por ID

- **URL do Endpoint**: `https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id}/autores`
- **Método HTTP**: `GET`
- **Exemplo de Requisição Completa (JSON)**:

  ```
  GET https://dadosabertos.camara.leg.br/api/v2/proposicoes/2056568/autores
  Accept: application/json
  User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
  ```

### Mapeamento dos Campos de Dados

Com base na documentação fornecida, os campos necessários podem ser mapeados da seguinte forma:

- **Autor do processo**: Para obter o nome do autor, o endpoint `/proposicoes/{id}/autores` deve ser consultado. O nome do autor estará em `dados[].nome`.
  - Caminho: `dados[].nome` (do endpoint `/proposicoes/{id}/autores`)
- **Data de apresentação**: Espera-se que esteja disponível nos detalhes da proposição (`/proposicoes/{id}`).
  - Caminho: `dados.dataApresentacao` (do endpoint `/proposicoes/{id}`)
- **Identificador único do processo**: O próprio `id` da proposição.
  - Caminho: `dados.id` (do endpoint `/proposicoes/{id}`)

## Conclusão

Com base na documentação das APIs, ambas as plataformas fornecem os dados necessários para a extração de informações sobre processos legislativos. O mapeamento dos campos foi realizado presumindo a correta funcionalidade dos endpoints conforme descrito em suas respectivas documentações.

