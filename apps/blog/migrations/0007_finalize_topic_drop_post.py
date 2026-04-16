import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_migrate_posts_to_topics'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='like',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='comment',
            name='topic',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='comments',
                to='blog.topic',
            ),
        ),
        migrations.AlterField(
            model_name='like',
            name='topic',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='likes',
                to='blog.topic',
            ),
        ),
        migrations.RemoveField(
            model_name='comment',
            name='post',
        ),
        migrations.RemoveField(
            model_name='like',
            name='post',
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together={('topic', 'user')},
        ),
        migrations.DeleteModel(
            name='Post',
        ),
    ]
