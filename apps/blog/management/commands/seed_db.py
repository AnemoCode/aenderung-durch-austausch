import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.blog.models import Comment, Like, Topic, TopicPart
from apps.blog.staging_data import SEED_USERS

User = get_user_model()

SEED_TOPICS = [
    {
        "title": "Klimawandel und städtische Mobilität",
        "tags": ["Klima", "Mobilität", "Stadt"],
        "is_published": True,
        "parts": [
            {
                "heading": "Aktuelle Herausforderungen",
                "body": (
                    "Der Klimawandel stellt Städte weltweit vor enorme Herausforderungen. "
                    "Besonders der städtische Verkehr trägt erheblich zu CO₂-Emissionen bei. "
                    "Laut aktuellen Studien ist der Transportsektor für etwa 24 % der globalen "
                    "Treibhausgasemissionen verantwortlich."
                ),
                "order": 0,
            },
            {
                "heading": "Lösungsansätze und Alternativen",
                "body": (
                    "Städte wie Amsterdam und Kopenhagen zeigen, wie eine konsequente Fahrradinfrastruktur "
                    "den Autoverkehr deutlich reduzieren kann. Ergänzend bieten gut ausgebaute "
                    "öffentliche Verkehrsmittel eine klimafreundliche Alternative für weitere Strecken."
                ),
                "order": 1,
            },
        ],
        "comments": [
            {"author_email": "alice@staging.local", "body": "Sehr guter Beitrag! Ich fahre selbst täglich Fahrrad und kann die Vorteile bestätigen."},
            {"author_email": "bob@staging.local", "body": "Interessante Perspektive. Aber wie sieht es mit ländlichen Gebieten aus?"},
        ],
        "likes": ["alice@staging.local", "bob@staging.local"],
    },
    {
        "title": "Digitale Bildung in Schulen",
        "tags": ["Bildung", "Digitalisierung", "Schule"],
        "is_published": True,
        "parts": [
            {
                "heading": "Stand der Digitalisierung",
                "body": (
                    "Die Digitalisierung des Bildungswesens schreitet voran, jedoch mit großen regionalen "
                    "Unterschieden. Während einige Schulen bereits vollständig auf digitale Lernmittel "
                    "setzen, fehlt es andernorts noch an grundlegender Infrastruktur wie stabiles WLAN."
                ),
                "order": 0,
            },
            {
                "heading": "Chancen und Risiken",
                "body": (
                    "Digitale Werkzeuge können individualisiertes Lernen fördern und Schülerinnen und "
                    "Schülern ermöglichen, ihrem eigenen Tempo zu folgen. Gleichzeitig müssen Medienkompetenz "
                    "und der verantwortungsvolle Umgang mit digitalen Inhalten aktiv gelehrt werden."
                ),
                "order": 1,
            },
        ],
        "comments": [
            {"author_email": "bob@staging.local", "body": "Als Lehrer sehe ich täglich, wie unterschiedlich die Voraussetzungen sind."},
        ],
        "likes": ["alice@staging.local"],
    },
    {
        "title": "Zukunft der Arbeit: Remote-Work-Modelle",
        "tags": ["Arbeit", "Remote", "Zukunft"],
        "is_published": True,
        "parts": [
            {
                "heading": "Wandel durch die Pandemie",
                "body": (
                    "Die COVID-19-Pandemie hat das Homeoffice in vielen Unternehmen von einer Ausnahme "
                    "zur Normalität gemacht. Viele Arbeitnehmerinnen und Arbeitnehmer schätzen die "
                    "gewonnene Flexibilität und möchten nicht mehr vollständig in Büros zurückkehren."
                ),
                "order": 0,
            },
            {
                "heading": "Hybride Arbeitsmodelle als Kompromiss",
                "body": (
                    "Hybride Modelle, bei denen Beschäftigte einen Teil der Woche im Büro und den Rest "
                    "remote arbeiten, scheinen sich als bevorzugtes Format herauszukristallisieren. "
                    "Sie verbinden die Vorteile beider Welten: persönlicher Austausch und flexible Zeiteinteilung."
                ),
                "order": 1,
            },
        ],
        "comments": [
            {"author_email": "alice@staging.local", "body": "Remote Work hat meine Work-Life-Balance deutlich verbessert."},
            {"author_email": "bob@staging.local", "body": "Ich vermisse den persönlichen Kontakt zu Kollegen. Hybrid ist wirklich der beste Kompromiss."},
        ],
        "likes": ["bob@staging.local"],
    },
]


class Command(BaseCommand):
    help = "Seed the database with staging data (users, topics, comments, likes)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Flush all app data before seeding.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing data...")
            Like.objects.all().delete()
            Comment.objects.all().delete()
            TopicPart.objects.all().delete()
            Topic.objects.all().delete()
            User.objects.all().delete()
            self.stdout.write(self.style.WARNING("All data flushed."))

        self._seed_users()
        self._seed_moderator()
        self._seed_topics()
        self.stdout.write(self.style.SUCCESS("Database seeding complete."))

    def _seed_users(self):
        for data in SEED_USERS:
            email = data["email"]
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": data["name"],
                    "is_staff": data.get("is_staff", False),
                    "is_superuser": data.get("is_superuser", False),
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
                self.stdout.write(f"  Created user: {email}")
            else:
                self.stdout.write(f"  User already exists: {email}")

    def _seed_moderator(self):
        from django.contrib.auth.models import Group

        try:
            moderator_group = Group.objects.get(name='Moderator')
        except Group.DoesNotExist:
            self.stdout.write(self.style.WARNING("  Moderator group not found – skipping."))
            return
        alice = User.objects.filter(email="alice@staging.local").first()
        if alice:
            alice.groups.add(moderator_group)
            self.stdout.write("  Assigned alice@staging.local to Moderator group.")

    def _seed_topics(self):
        admin_user = User.objects.get(email="admin@staging.local")
        users_by_email = {u.email: u for u in User.objects.all()}

        for topic_data in SEED_TOPICS:
            topic, created = Topic.objects.get_or_create(
                title=topic_data["title"],
                defaults={
                    "author": admin_user,
                    "is_published": topic_data.get("is_published", False),
                },
            )
            if created:
                topic.tags.set(topic_data.get("tags", []))
                self.stdout.write(f"  Created topic: {topic.title}")
            else:
                self.stdout.write(f"  Topic already exists: {topic.title}")

            for part_data in topic_data.get("parts", []):
                TopicPart.objects.get_or_create(
                    topic=topic,
                    heading=part_data["heading"],
                    defaults={
                        "author": admin_user,
                        "body": part_data["body"],
                        "order": part_data["order"],
                    },
                )

            for comment_data in topic_data.get("comments", []):
                author = users_by_email.get(comment_data["author_email"])
                if author:
                    Comment.objects.get_or_create(
                        topic=topic,
                        author=author,
                        body=comment_data["body"],
                    )

            for liker_email in topic_data.get("likes", []):
                liker = users_by_email.get(liker_email)
                if liker:
                    Like.objects.get_or_create(topic=topic, user=liker)
