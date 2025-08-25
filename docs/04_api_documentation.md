# API Documentation

Este projeto utiliza **drf-spectacular** para gerar documentação automática da API seguindo o padrão OpenAPI 3.0.

## Endpoints de Documentação

Após iniciar o servidor, você pode acessar a documentação através dos seguintes endpoints:

### Swagger UI
- **URL**: `/api/docs/`
- **Descrição**: Interface interativa para testar a API
- **Recursos**: 
  - Teste endpoints diretamente no navegador
  - Visualize schemas de request/response
  - Execute requisições com autenticação

### ReDoc
- **URL**: `/api/redoc/`
- **Descrição**: Documentação em formato mais legível
- **Recursos**:
  - Layout mais limpo e organizado
  - Melhor para leitura e referência
  - Exemplos de código incluídos

### Schema OpenAPI
- **URL**: `/api/schema/`
- **Descrição**: Schema JSON da API no formato OpenAPI 3.0
- **Uso**: Para integração com ferramentas externas

## Como Usar

1. **Inicie o servidor**:
   ```bash
   docker compose --rm app sh -c "python manage.py runserver 0.0.0.0:8000"
   ```

2. **Acesse a documentação**:
   - Swagger UI: http://localhost:8000/api/docs/
   - ReDoc: http://localhost:8000/api/redoc/

## Endpoints Disponíveis

### Temas (`/api/temas/`)
- `GET /api/temas/` - Listar todos os temas
- `POST /api/temas/` - Criar novo tema
- `GET /api/temas/{id}/` - Obter tema específico
- `PUT /api/temas/{id}/` - Atualizar tema
- `PATCH /api/temas/{id}/` - Atualizar tema parcialmente
- `DELETE /api/temas/{id}/` - Excluir tema

### Autenticação (`/api/auth/`)
- `POST /api/auth/login/` - Autenticar usuário

## Adicionando Documentação a Novos Endpoints

### Para ViewSets:
```python
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        summary="Listar itens",
        description="Retorna uma lista de itens",
        tags=["minha-app"],
        responses={200: MeuSerializer(many=True)},
    ),
    create=extend_schema(
        summary="Criar item",
        description="Cria um novo item",
        tags=["minha-app"],
        request=MeuSerializer,
        responses={201: MeuSerializer},
    ),
)
class MeuViewSet(viewsets.ModelViewSet):
    # ... implementação
```

### Para Views Simples:
```python
from drf_spectacular.utils import extend_schema, OpenApiExample

@extend_schema(
    summary="Meu endpoint",
    description="Descrição do endpoint",
    tags=["minha-app"],
    request=MeuRequestSerializer,
    responses={200: MeuResponseSerializer},
    examples=[
        OpenApiExample(
            'Exemplo válido',
            value={'campo': 'valor'},
            description='Descrição do exemplo'
        ),
    ]
)
@api_view(['POST'])
def minha_view(request):
    # ... implementação
```

### Para Serializers:
```python
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Exemplo válido',
            value={'id': 1, 'nome': 'Exemplo'},
            description='Descrição do exemplo'
        ),
    ]
)
class MeuSerializer(serializers.ModelSerializer):
    # ... implementação
```

## Configurações

As configurações do drf-spectacular estão em `config/settings.py`:

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'My Kink is Karma API',
    'DESCRIPTION': 'API para gerenciamento de pautas e temas',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'TAGS': [
        {'name': 'temas', 'description': 'Operações relacionadas aos temas'},
        {'name': 'authentication', 'description': 'Operações de autenticação'},
    ],
}
```

## Benefícios

- **Documentação Automática**: Atualiza automaticamente com mudanças no código
- **Padrão OpenAPI**: Compatível com ferramentas de terceiros
- **Interface Interativa**: Teste endpoints diretamente no navegador
- **Exemplos Incluídos**: Documentação com exemplos práticos
- **Validação**: Schemas validam requests/responses automaticamente 