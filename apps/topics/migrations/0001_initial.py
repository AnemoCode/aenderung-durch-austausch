from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Titel')),
                ('description', models.TextField(blank=True, verbose_name='Beschreibung')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Thema',
                'verbose_name_plural': 'Themen',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='TopicPart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Titel')),
                ('body', models.TextField(verbose_name='Inhalt')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='Reihenfolge')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('topic', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='parts',
                    to='topics.topic',
                )),
            ],
            options={
                'verbose_name': 'Themanteil',
                'verbose_name_plural': 'Thementeile',
                'ordering': ['order', 'created_at'],
            },
        ),
    ]
