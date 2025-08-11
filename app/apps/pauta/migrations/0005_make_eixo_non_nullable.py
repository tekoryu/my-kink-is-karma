# Generated manually to make eixo field non-nullable

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pauta', '0004_load_agenda_data_with_eixos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tema',
            name='eixo',
            field=models.ForeignKey(help_text='Eixo ao qual este tema pertence', on_delete=django.db.models.deletion.CASCADE, related_name='temas', to='pauta.eixo'),
        ),
    ]
