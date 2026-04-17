from django.conf import settings
from django.db import migrations, models


def backfill_topicpart_author(apps, schema_editor):
    TopicPart = apps.get_model('blog', 'TopicPart')
    for part in TopicPart.objects.select_related('topic').all():
        part.author_id = part.topic.author_id
        part.save(update_fields=['author'])


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_finalize_topic_drop_post'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='topicpart',
            name='author',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.CASCADE,
                related_name='topic_parts',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Autor',
            ),
        ),
        migrations.RunPython(backfill_topicpart_author, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='topicpart',
            name='author',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='topic_parts',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Autor',
            ),
        ),
    ]
