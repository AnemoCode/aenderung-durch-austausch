from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0002_definition_definitions_definition_term_ci_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='definition',
            name='references',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Literatur, Links und Quellenangaben zu dieser Definition.',
                verbose_name='Quellenangaben & Verweise',
            ),
        ),
    ]
