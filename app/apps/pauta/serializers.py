from rest_framework import serializers
from .models import Tema


class TemaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Tema.
    
    Expõe os campos id e nome para operações CRUD.
    """
    
    class Meta:
        model = Tema
        fields = ['id', 'nome']
        read_only_fields = ['id'] 