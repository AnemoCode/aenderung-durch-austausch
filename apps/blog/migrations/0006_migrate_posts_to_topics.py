from django.db import migrations
from django.utils.text import slugify


def _unique_slug(Topic, base_slug):
    slug = base_slug or 'thema'
    counter = 1
    while Topic.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1
    return slug


def migrate_posts_to_topics(apps, schema_editor):
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
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
        TopicPart.objects.create(
            topic=topic,
            heading=post.subtitle or post.title,
            body=post.description,
            order=0,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
        Comment.objects.filter(post_id=post.id).update(topic_id=topic.id)
        Like.objects.filter(post_id=post.id).update(topic_id=topic.id)


def reverse_noop(apps, schema_editor):
    raise RuntimeError(
        'Migration 0006_migrate_posts_to_topics is irreversible: '
        'Post records have been merged into Topic+TopicPart and the source data is lost.'
    )


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('blog', '0005_comment_like_topic_field'),
    ]

    operations = [
        migrations.RunPython(migrate_posts_to_topics, reverse_noop),
    ]
