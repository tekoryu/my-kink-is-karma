# Análise da API da Câmara dos Deputados

## Informações Gerais

- **URL Base**: `https://dadosabertos.camara.leg.br/api/v2/`
- **Autenticação**: Não requer autenticação (API pública)
- **Rate Limiting**: Não especificado um limite por segundo, mas listagens retornam 15 itens por padrão e o limite por requisição é de 100 itens.
- **Formatos Suportados**: JSON, XML

## Endpoints Relevantes para Processos Legislativos

### 1. Detalhes de Proposição por ID
- **Endpoint**: `/proposicoes/{id}`
- **Método**: GET
- **Descrição**: Informações detalhadas sobre uma proposição específica.
- **Parâmetros**:
  - `id` (path, obrigatório): ID da proposição.
- **Exemplo de Requisição (JSON)**:
  `GET https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id}`
  `Accept: application/json`

### 2. Autores de Proposição por ID
- **Endpoint**: `/proposicoes/{id}/autores`
- **Método**: GET
- **Descrição**: Lista pessoas e/ou entidades autoras de uma proposição.
- **Parâmetros**:
  - `id` (path, obrigatório): ID da proposição.
- **Exemplo de Requisição (JSON)**:
  `GET https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id}/autores`
  `Accept: application/json`

## Mapeamento de Campos de Dados (Câmara)

Para os campos solicitados, espera-se que os dados estejam na seguinte estrutura:

- **Autor do processo**: Provavelmente disponível no endpoint `/proposicoes/{id}/autores` ou dentro da resposta de `/proposicoes/{id}` (campo `nome` ou similar).
- **Data de apresentação**: Espera-se que esteja disponível nos detalhes da proposição (`/proposicoes/{id}`) (campo `dataApresentacao` ou similar).
- **Identificador único do processo**: O próprio `id` usado na requisição.

## Próximos Passos

1. Realizar um teste prático dos endpoints `/proposicoes/{id}` e `/proposicoes/{id}/autores` usando um ambiente de execução de código (Python com `requests`, por exemplo) para confirmar a estrutura da resposta e o mapeamento dos campos.
2. Consolidar todas as informações no documento de resumo final.

