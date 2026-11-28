# ADR 0002: Schutz vor DDoS und Angriffen auf die Anwendung

Status: Vorschlag, Entscheidung durch das Team offen

## Kontext

Eine Seite über rechte Argumentationsmuster und Verschwörungserzählungen zieht eher Angriffe an als ein normales Blog. Realistisch sind vor allem zwei Dinge: Überlastung durch viele Anfragen (DDoS) und automatisierte Angriffe auf Login und Kommentarformular, also Brute Force und Spam.

Heute steht vor gunicorn nur der Reverse-Proxy auf unserem Server. Er macht TLS und leitet HTTP auf HTTPS um. Gegen einen größeren DDoS hilft er nicht, denn dann ist die Leitung zum Server voll, bevor der Proxy überhaupt etwas filtern kann.

## Optionen

1. **Cloudflare (Free) als Proxy vor dem Server.** Die DNS-Einträge zeigen auf Cloudflare, Cloudflare leitet an unseren Server weiter. Das bringt DDoS-Schutz, Bot-Erkennung und Rate-Limits ohne Kosten. Der Haken: Cloudflare ist ein US-Unternehmen und sieht den gesamten Verkehr im Klartext, auch Logins. Cloudflare ist unter dem EU-US Data Privacy Framework zertifiziert und bietet einen AVV an. Für manche in unserer Zielgruppe kann es trotzdem ein Vertrauensthema sein.
2. **DDoS-Schutz des Hosters.** Hetzner filtert zum Beispiel volumetrische Angriffe automatisch und kostenlos, und die Daten bleiben in der EU. Gegen gezielte Angriffe auf die Anwendung (viele Login-Versuche) hilft das nicht.
3. **Eine eigene WAF im Proxy**, etwa ModSecurity oder Coraza mit dem OWASP Core Rule Set. Das braucht Pflege, und falsche Treffer blockieren echte Nutzer:innen. Für unsere Größe ist das zu viel Aufwand.

## Vorschlag

Ich würde Option 2 als Grundlage nehmen und die Anwendung selbst absichern: Rate-Limits für Login, Registrierung und Kommentare (#96) und die Sicherheits-Header aus #91. Damit bleibt alles in der EU und wir haben keinen weiteren Dienstleister.

Cloudflare würde ich bereithalten und erst einschalten, wenn wir tatsächlich angegriffen werden. Das geht innerhalb einer Stunde: Domain bei Cloudflare anlegen, Nameserver umstellen, SSL-Modus „Full (strict)“ wählen. Danach muss der Proxy die echte Client-IP aus `CF-Connecting-IP` übernehmen, sonst zählen die Rate-Limits alle Anfragen als eine IP.

Was meint ihr? TODO: Entscheidung und Datum eintragen.
