import django.db.models.deletion
import taggit.managers
from django.conf import settings
from django.db import migrations, models
from django.utils.text import slugify


def _unique_slug(Topic, base_slug):
    base = base_slug or 'thema'
    slug = base
    counter = 1
    while Topic.objects.filter(slug=slug).exists():
        slug = f'{base}-{counter}'
        counter += 1
    return slug


def migrate_data(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    Topic = apps.get_model('blog', 'Topic')
    TopicPart = apps.get_model('blog', 'TopicPart')
    Comment = apps.get_model('blog', 'Comment')
    Like = apps.get_model('blog', 'Like')

    for post in Post.objects.all().order_by('id'):
        base_slug = slugify(post.title, allow_unicode=False)
        topic = Topic.objects.create(
            title=post.title,
            slug=_unique_slug(Topic, base_slug),
            author_id=post.author_id,
            is_published=post.is_published,
            legacy_post_id=post.id,
        )
        Topic.objects.filter(pk=topic.pk).update(
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
        part = TopicPart.objects.create(
            topic=topic,
            heading=post.subtitle or post.title,
            body=post.description,
            order=0,
            author_id=post.author_id,
        )
        TopicPart.objects.filter(pk=part.pk).update(
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
        Comment.objects.filter(post_id=post.id).update(topic_id=topic.id)
        Like.objects.filter(post_id=post.id).update(topic_id=topic.id)


def reverse_noop(apps, schema_editor):
    raise RuntimeError(
        'This data migration is irreversible: '
        'Post records have been merged into Topic+TopicPart and the source data is lost.'
    )


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('blog', '0001_initial'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Titel')),
                ('slug', models.SlugField(blank=True, max_length=220, unique=True, verbose_name='URL-Kürzel')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_published', models.BooleanField(default=False, verbose_name='Veröffentlicht')),
                ('legacy_post_id', models.PositiveIntegerField(
                    blank=True,
                    editable=False,
                    help_text='PK des migrierten MVP-Posts (für Redirect-Backwards-Compat).',
                    null=True,
                    unique=True,
                )),
                ('author', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='topics',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Autor',
                )),
                ('tags', taggit.managers.TaggableManager(
                    blank=True,
                    help_text='A comma-separated list of tags.',
                    through='taggit.TaggedItem',
                    to='taggit.Tag',
                    verbose_name='Tags',
                )),
            ],
            options={
                'verbose_name': 'Thema',
                'verbose_name_plural': 'Themen',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TopicPart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(max_length=300, verbose_name='Unterüberschrift')),
                ('body', models.TextField(verbose_name='Inhalt')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Reihenfolge')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(
                    null=True,
                    blank=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='topic_parts',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Autor',
                )),
                ('tags', taggit.managers.TaggableManager(
                    blank=True,
                    help_text='A comma-separated list of tags.',
                    through='taggit.TaggedItem',
                    to='taggit.Tag',
                    verbose_name='Tags',
                )),
                ('topic', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='parts',
                    to='blog.topic',
                    verbose_name='Thema',
                )),
            ],
            options={
                'verbose_name': 'Thementeil',
                'verbose_name_plural': 'Thementeile',
                'ordering': ['order', 'created_at'],
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='topic',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='comments',
                to='blog.topic',
            ),
        ),
        migrations.AddField(
            model_name='like',
            name='topic',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='likes',
                to='blog.topic',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together=set(),
        ),
        migrations.RunPython(migrate_data, reverse_noop),
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
        migrations.AlterField(
            model_name='topicpart',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='topic_parts',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Autor',
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
