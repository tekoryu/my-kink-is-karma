# Generated manually to fix DataError for activity history fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pauta', '0013_proposicao_selected'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camaraactivityhistory',
            name='descricao_tramitacao',
            field=models.CharField(help_text="Descrição do tipo de tramitação", max_length=500),
        ),
        migrations.AlterField(
            model_name='camaraactivityhistory',
            name='descricao_situacao',
            field=models.CharField(blank=True, help_text="Descrição da situação", max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='camaraactivityhistory',
            name='apreciacao',
            field=models.CharField(blank=True, help_text="Tipo de apreciação", max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='senadoactivityhistory',
            name='colegiado_nome',
            field=models.CharField(blank=True, help_text="Nome do colegiado", max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='senadoactivityhistory',
            name='ente_administrativo_nome',
            field=models.CharField(blank=True, help_text="Nome do ente administrativo", max_length=500, null=True),
        ),
    ]
