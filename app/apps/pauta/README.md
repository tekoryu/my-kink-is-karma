# Aplicativo Pauta

Este aplicativo Django gerencia temas e proposições legislativas para monitoramento automático através de APIs públicas.

## Modelos

### Tema

O modelo `Tema` representa categorias de interesse para organização das proposições legislativas.

**Campos:**
- `nome` (CharField, max_length=100): Nome único do tema (ex: "Educação", "Segurança Pública")
- `created_at` (DateTimeField): Data e hora de criação
- `updated_at` (DateTimeField): Data e hora da última atualização

**Constraints:**
- O campo `nome` é único e não pode ser nulo ou vazio

**Exemplo de uso:**
```python
from apps.pauta.models import Tema

# Criar um novo tema
tema = Tema.objects.create(nome="Educação")

# Buscar temas
temas = Tema.objects.all()
tema_educacao = Tema.objects.get(nome="Educação")
```

### Proposicao

O modelo `Proposicao` representa proposições legislativas específicas que serão monitoradas.

**Campos:**
- `tema` (ForeignKey): Referência ao tema ao qual a proposição pertence
- `tipo` (CharField, max_length=10): Tipo da proposição (ex: "PL", "PEC", "MPV")
- `numero` (IntegerField): Número da proposição
- `ano` (IntegerField): Ano da proposição
- `created_at` (DateTimeField): Data e hora de criação no sistema
- `updated_at` (DateTimeField): Data e hora da última atualização

**Constraints:**
- `unique_together` nos campos `tipo`, `numero` e `ano` (garante que a mesma proposição não seja cadastrada mais de uma vez globalmente)
- Relacionamento com `Tema` usando `on_delete=models.CASCADE`

**Propriedades:**
- `identificador_completo`: Retorna o identificador no formato "TIPO NUMERO/ANO"

**Exemplo de uso:**
```python
from apps.pauta.models import Tema, Proposicao

# Criar uma proposição
tema = Tema.objects.create(nome="Educação")
proposicao = Proposicao.objects.create(
    tema=tema,
    tipo="PL",
    numero=1234,
    ano=2023
)

# Acessar propriedades
print(proposicao.identificador_completo)  # "PL 1234/2023"
print(str(proposicao))  # "PL 1234/2023"

# Buscar proposições por tema
proposicoes_educacao = tema.proposicoes.all()
```

## Relacionamentos

- Um `Tema` pode ter múltiplas `Proposicao`s
- Uma `Proposicao` pertence a um único `Tema`
- Ao deletar um `Tema`, todas as suas `Proposicao`s são deletadas automaticamente (CASCADE)

## Histórias de Usuário Atendidas

### USH_01 - Criar um novo tema para organização
- ✅ Modelo `Tema` com campo `nome` único
- ✅ Validação para evitar nomes duplicados
- ✅ Campo não pode ser nulo ou vazio

### USH_02 - Adicionar uma proposição para monitoramento
- ✅ Modelo `Proposicao` com campos `tipo`, `numero` e `ano`
- ✅ Relacionamento com `Tema` via ForeignKey
- ✅ Constraint `unique_together` para evitar duplicação global
- ✅ Validação para evitar proposições duplicadas

## Testes

Execute os testes do aplicativo com:

```bash
python manage.py test apps.pauta.tests
```

Os testes cobrem:
- Criação de temas e proposições válidas
- Validação de constraints (nome único, unique_together)
- Relacionamentos entre modelos
- Propriedades e métodos dos modelos

## Admin Django

Os modelos estão registrados no admin do Django com configurações otimizadas:

- **TemaAdmin**: Lista por nome, filtros por data, busca por nome
- **ProposicaoAdmin**: Lista por identificador completo, filtros por tema/tipo/ano, busca por tipo/número/tema

## Migrações

Para aplicar as migrações:

```bash
python manage.py migrate
```

Para criar novas migrações após alterações nos modelos:

```bash
python manage.py makemigrations pauta
``` 