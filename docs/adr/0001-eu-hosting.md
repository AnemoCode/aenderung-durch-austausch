# ADR 0001: Hosting in der EU

Status: Entwurf, Angaben mit TODO bitte ergänzen

## Kontext

ÄdA speichert personenbezogene Daten: E-Mail-Adressen und Namen der Accounts, Kommentare und bald auch Newsletter-Anmeldungen. Viele Nutzer:innen sprechen über politisch heikle Erfahrungen. Wir wollen deshalb, dass alle Daten in der EU liegen und wir für jeden Dienstleister einen Auftragsverarbeitungsvertrag (AVV) haben.

## Entscheidung

Server, Datenbank und Backups laufen bei einem Anbieter mit Rechenzentrum in der EU.

| | |
|---|---|
| Anbieter | TODO (z. B. Hetzner) |
| Standort / Region | TODO (z. B. Falkenstein, DE) |
| AVV abgeschlossen | TODO (Datum, wo abgelegt) |
| Reverse-Proxy | TODO bestätigen. Laut Kommentar in `aenderung_durch_austausch/urls.py` Traefik über Dokploy. |
| Offsite-Backups | TODO (z. B. Hetzner Storage Box, siehe `docs/operations/backup-restore.md`) |

## Datenflüsse zu Dritten

| Dienst | Was fließt dorthin | Stand |
|---|---|---|
| Sentry | Fehlermeldungen und Stacktraces, ohne IP und ohne Cookies (`send_default_pii=False`) | EU-Region nutzen (`*.de.sentry.io`), AVV mit Sentry nötig |
| SMTP-Anbieter | E-Mail-Adressen und Inhalte der Newsletter (#97) | Anbieter mit EU-Region wählen |
| YouTube, Vimeo, SoundCloud, Spotify | Erst nach Klick auf ein eingebettetes Medium (#94) | Zwei-Klick-Lösung geplant |
| Google Fonts (`fonts.googleapis.com`) | IP-Adresse jeder Besucher:in bei jedem Seitenaufruf | **Offen**, siehe unten |
| `cdn.jsdelivr.net`, `unpkg.com`, `cdn.quilljs.com` | IP-Adresse beim Laden von Alpine.js, Lucide und Quill | **Offen**, siehe unten |

## Offene Punkte

Alle Seiten laden die Schriften direkt von Google. Das LG München I hat 2022 entschieden, dass das ohne Einwilligung gegen die DSGVO verstößt (Az. 3 O 17493/20). Ich würde vorschlagen, dass wir die Schriften selbst ausliefern, über `static/fonts/`. Das ist wenig Aufwand und nimmt das Risiko komplett raus. Dasselbe gilt für die JavaScript-Bibliotheken von den CDNs, nur ist das Risiko dort geringer. Das gehört in ein eigenes Issue.
