from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Tema


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Tema válido',
            value={
                'id': 1,
                'nome': 'Tecnologia'
            },
            description='Exemplo de um tema válido'
        ),
        OpenApiExample(
            'Criação de tema',
            value={
                'nome': 'Novo Tema'
            },
            description='Exemplo para criação de um novo tema'
        ),
    ]
)
class TemaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Tema.
    
    Expõe os campos id e nome para operações CRUD.
    """
    
    class Meta:
        model = Tema
        fields = ['id', 'nome']
        read_only_fields = ['id'] 