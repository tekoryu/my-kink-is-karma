# Generated manually for loading agenda data with eixos structure

import json
import os
from datetime import datetime
from django.db import migrations
from django.conf import settings


def load_agenda_data_with_eixos(apps, schema_editor):
    # Skip data loading during test runs to keep test database deterministic
    from django.conf import settings as django_settings
    if getattr(django_settings, 'TESTING', False):
        return
    """
    Load agenda data from JSON file into the database with the new eixos structure.
    Creates Eixo, Tema and Proposicao objects based on the agenda_2025.json file.
    """
    Eixo = apps.get_model('pauta', 'Eixo')
    Tema = apps.get_model('pauta', 'Tema')
    Proposicao = apps.get_model('pauta', 'Proposicao')
    
    # Path to the JSON file relative to the project root
    json_file_path = os.path.join(settings.BASE_DIR, '..', 'data', 'processed', 'agenda_2025.json')
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Create a mapping of tema names to Tema objects
        tema_mapping = {}
        
        # First, create all eixos
        for eixo_data in data.get('eixos', []):
            eixo_id = eixo_data['id']
            eixo_nome = eixo_data['nome']
            
            if not Eixo.objects.filter(id=eixo_id).exists():
                eixo = Eixo.objects.create(
                    id=eixo_id,
                    nome=eixo_nome
                )
            else:
                eixo = Eixo.objects.get(id=eixo_id)
            
            # Create temas for this eixo
            for tema_data in eixo_data.get('temas', []):
                nome = tema_data['nome'].strip()
                if nome and not Tema.objects.filter(nome=nome).exists():
                    # Parse datetime strings
                    created_at = datetime.fromisoformat(tema_data['created_at'].replace('Z', '+00:00'))
                    updated_at = datetime.fromisoformat(tema_data['updated_at'].replace('Z', '+00:00'))
                    
                    tema = Tema.objects.create(
                        eixo=eixo,
                        nome=nome,
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    tema_mapping[nome] = tema
        
        # Then create all proposicoes
        for proposicao_data in data.get('proposicoes', []):
            tema_nome = proposicao_data['tema'].strip()
            tema = tema_mapping.get(tema_nome)
            
            if tema:
                # Check if proposicao already exists
                if not Proposicao.objects.filter(
                    tipo=proposicao_data['tipo'],
                    numero=proposicao_data['numero'],
                    ano=proposicao_data['ano']
                ).exists():
                    # Parse datetime strings
                    created_at = datetime.fromisoformat(proposicao_data['created_at'].replace('Z', '+00:00'))
                    updated_at = datetime.fromisoformat(proposicao_data['updated_at'].replace('Z', '+00:00'))
                    
                    Proposicao.objects.create(
                        tema=tema,
                        tipo=proposicao_data['tipo'],
                        numero=proposicao_data['numero'],
                        ano=proposicao_data['ano'],
                        created_at=created_at,
                        updated_at=updated_at
                    )
    
    except FileNotFoundError:
        print(f"Warning: Could not find agenda file at {json_file_path}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
    except Exception as e:
        print(f"Error loading agenda data: {e}")


def reverse_load_agenda_data_with_eixos(apps, schema_editor):
    """
    Reverse migration: remove all data loaded from agenda_2025.json
    """
    Eixo = apps.get_model('pauta', 'Eixo')
    Tema = apps.get_model('pauta', 'Tema')
    Proposicao = apps.get_model('pauta', 'Proposicao')
    
    # Remove all proposicoes, temas and eixos (CASCADE will handle the relationships)
    Proposicao.objects.all().delete()
    Tema.objects.all().delete()
    Eixo.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pauta', '0003_add_eixo_model'),
    ]

    operations = [
        migrations.RunPython(
            load_agenda_data_with_eixos,
            reverse_code=reverse_load_agenda_data_with_eixos
        ),
    ]
