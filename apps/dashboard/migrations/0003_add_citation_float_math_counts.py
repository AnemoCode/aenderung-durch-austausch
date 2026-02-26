from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0002_add_clone_error_and_snapshot"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="citation_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="project",
            name="float_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="project",
            name="math_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="projectsnapshot",
            name="citation_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="projectsnapshot",
            name="float_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="projectsnapshot",
            name="math_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
