"""URL configuration for aenderung-durch-austausch project."""
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.static import serve

from apps.blog.views import TagDetailView
# Placeholder pillars — pages that are under development.
# `active_nav` highlights the current pillar in the shared header.
# `pillar_numeral` / `pillar_title` / `pillar_tagline` / `pillar_points` render the placeholder body.
PILLAR_PAGES = [
    {
        "slug": "argumentationsweisen",
        "name": "argumentation",
        "active_nav": "argumentation",
        "numeral": "02",
        "title": "Argumentationsweisen & Gegenargumente",
        "tagline": "Rechte Argumentationsmuster erkennen – und fundiert widerlegen.",
        "points": [
            "Kausale Herleitungen und Ursprünge rechter Argumentationsweisen.",
            "Innere Widersprüche, die sich aufzeigen lassen.",
            "Positionen zu Geschlecht, Freiheit, Sexualität und Demokratie.",
            "Jedes Argument und Gegenargument – in einfacher und formaler Sprache.",
        ],
    },
    {
        "slug": "kommunikationstechniken",
        "name": "kommunikation",
        "active_nav": "kommunikation",
        "numeral": "04",
        "title": "Kommunikationstechniken",
        "tagline": "Rhetorik und Gesprächstechniken für schwierige Diskurse.",
        "points": [
            "Rhetorische Stilmittel, die im Diskurs mit rechtem Gedankengut helfen.",
            "Wie überzeugt man Menschen – oder bringt sie zumindest zum Hinterfragen?",
            "Gesprächstechniken für emotional aufgeladene Situationen.",
            "Konkrete Beispiele aus dem Alltag – zum Üben und Anwenden.",
        ],
    },
]

pillar_urls = [
    path(
        f"{p['slug']}/",
        TemplateView.as_view(
            template_name="pillars/placeholder.html",
            extra_context={
                "active_nav": p["active_nav"],
                "pillar_numeral": p["numeral"],
                "pillar_title": p["title"],
                "pillar_tagline": p["tagline"],
                "pillar_points": p["points"],
            },
        ),
        name=p["name"],
    )
    for p in PILLAR_PAGES
]

urlpatterns = [
    path("health/", lambda request: HttpResponse("ok"), name="health"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/", admin.site.urls),
    re_path(r"^tag/(?P<slug>[-\w]+)/$", TagDetailView.as_view(), name="tag_detail"),
    path("", TemplateView.as_view(template_name="landing.html"), name="landing"),
    path("", include("apps.accounts.urls", namespace="accounts")),
    path("blog/", include("apps.blog.urls", namespace="blog")),
    path("definitionen/", include("apps.definitions.urls", namespace="definitions")),
    path(
        "medienkompetenz/",
        include("apps.medienkompetenz.urls", namespace="medienkompetenz"),
    ),
    *pillar_urls,
]

# Serve user-uploaded media (MEDIA_ROOT) through Django in every environment.
# WhiteNoise only handles collected static files, not runtime uploads, and the
# Dokploy/Traefik deployment has no separate web server bound to /media/, so
# without this route media 404s whenever DEBUG=False (i.e. in production).
# The files live on the mounted media volume; Django just needs a route to them.
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
