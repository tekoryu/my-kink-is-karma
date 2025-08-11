# Generated manually for Eixo model addition

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pauta', '0002_auto_20250806_1324'),
    ]

    operations = [
        migrations.CreateModel(
            name='Eixo',
            fields=[
                ('id', models.IntegerField(help_text='Identificador numérico do eixo', primary_key=True, serialize=False)),
                ('nome', models.CharField(help_text='Nome descritivo do eixo estratégico', max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Data e hora de criação do eixo')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Data e hora da última atualização do eixo')),
            ],
            options={
                'verbose_name': 'Eixo',
                'verbose_name_plural': 'Eixos',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='tema',
            name='eixo',
            field=models.ForeignKey(blank=True, help_text='Eixo ao qual este tema pertence', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='temas', to='pauta.eixo'),
        ),
        migrations.AlterModelOptions(
            name='tema',
            options={'ordering': ['eixo__id', 'nome'], 'verbose_name': 'Tema', 'verbose_name_plural': 'Temas'},
        ),
    ]
