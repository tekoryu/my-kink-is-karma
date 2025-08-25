# Análise da API do Senado Federal

## Informações Gerais

- **URL Base**: `https://legis.senado.leg.br/dadosabertos/` (inferido do contexto e do schema)
- **Autenticação**: Não requer autenticação (API pública)
- **Rate Limiting**: Máximo de 10 requisições por segundo (HTTP 429 se excedido)
- **Formatos Suportados**: JSON, XML, CSV (conforme `Accept` header ou sufixo na URL)

## Endpoints Relevantes para Processos Legislativos

### 1. Detalhes de Processo por ID
- **Endpoint**: `/dadosabertos/processo/{id}`
- **Método**: GET
- **Descrição**: Obtém detalhes completos de um processo legislativo, como identificação, ementa, autoria, data de apresentação, etc.
- **Parâmetros**:
  - `id` (path, obrigatório): ID do Processo (tipo: `integer`, formato: `int64`, exemplo: `1449240`)
  - `v` (query, opcional): Versão do serviço (tipo: `integer`, formato: `int32`, padrão: `1`, exemplo: `1`)
- **Exemplo de Requisição (JSON)**:
  `GET https://legis.senado.leg.br/dadosabertos/processo/1449240.json`
  `Accept: application/json`

## Mapeamento de Campos de Dados (Senado)

Para o endpoint `/dadosabertos/processo/{id}`, espera-se que os dados estejam na seguinte estrutura (baseado no `$ref: schemas/processo.yml#/components/schemas/Processo`):

- **Autor do processo**: `Processo.Autoria.Autor.NomeParlamentar` (ou similar, dependendo da estrutura exata do `Processo` schema)
- **Data de apresentação**: `Processo.DadosBasicos.DataApresentacao` (ou similar)
- **Identificador único do processo**: `Processo.Identificacao.CodigoProcesso` (ou o próprio `id` da URL)

## Limitações Identificadas

1. **Rate Limiting**: 10 requisições/segundo.
2. **Serviços Deprecated**: Alguns endpoints estão marcados como depreciados, indicando que devem ser substituídos por outros serviços.
3. **Acesso Direto**: Tentativas de acesso direto via `curl` falharam, o que pode indicar restrições de CORS ou outras políticas de segurança que não são evidentes apenas pelo schema. Será necessário um teste prático com uma ferramenta que simule um navegador ou um ambiente de execução de código mais completo.

## Próximos Passos

1. Realizar um teste prático do endpoint `/dadosabertos/processo/{id}` usando um ambiente de execução de código (Python com `requests`, por exemplo) para confirmar a estrutura da resposta e o mapeamento dos campos.
2. Analisar a documentação da API da Câmara dos Deputados e extrair as informações relevantes.
3. Realizar testes práticos para a API da Câmara.
4. Consolidar todas as informações no documento de resumo final.

