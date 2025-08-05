# Plano de Gerenciamento do Projeto (Simplificado)

**Versão:** 1.0
**Data:** 03 de Agosto de 2025

## 1. Roadmap do Produto (Priorização das Entregas)

A entrega das funcionalidades seguirá uma abordagem faseada para agregar valor de forma incremental.

### Primeira Entrega (Fundação do Sistema)
* **Histórias:** USH_01 (Criação de Tema) e USH_02 (Adicionar Proposição).
* **Objetivo:** Construir a base do sistema, permitindo o cadastro e organização das pautas. Foco no desenvolvimento da API de backend (Django/DRF) e na estruturação do banco de dados (PostgreSQL).

### Segunda Entrega (Implementação da Automação)
* **História:** USH_03 (Visualizar Atualizações de Proposições).
* **Objetivo:** Desenvolver a funcionalidade central de monitoramento automático. Implementar o job diário e conectar a base de dados ao Power BI para a visualização dos dados atualizados.

### Terceira Entrega (Refinamento e Proatividade)
* **História:** USH_04 (Receber Notificações de Mudanças).
* **Objetivo:** Adicionar a camada de conveniência e proatividade ao sistema através do serviço de notificações push.

## 2. Gerenciamento de Riscos

* **Risco 1 (Técnico):** Instabilidade, mudança de formato ou descontinuidade das APIs públicas do governo.
    * **Mitigação:** Uso de um banco de dados local para diminuir a dependência contínua e garantir a consulta histórica. O código de acesso à API será modularizado para facilitar a manutenção em caso de mudanças.
* **Risco 2 (De Escopo):** Solicitações de funcionalidades adicionais não previstas ("Scope Creep") que podem atrasar a entrega do essencial.
    * **Mitigação:** Aderência estrita ao "Documento de Visão e Escopo". Novas ideias serão registradas em um backlog futuro e não incorporadas nas entregas atuais sem uma análise de impacto formal.

## 3. Definição de "Pronto" (Definition of Done)

* O código do backend (API em Django/DRF) para a funcionalidade foi desenvolvido.
* Testes automatizados para a API (testes de unidade e integração) foram criados e estão passando com sucesso.
* O esquema do banco de dados (PostgreSQL) foi atualizado e reflete corretamente as novas funcionalidades.
* A visualização no Power BI foi criada ou atualizada para atender a todos os Critérios de Aceite da história.
* A documentação essencial do código (ex: docstrings no Python) foi escrita e está clara.