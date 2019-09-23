# 2019-SocialMeetScheduler
Assignment for the 2019 edition of the "Web Development and the Semantic Web" course, by Ádler Oliveira Silva Neves.

## How to run

First, install `python3`, `automake`, `libspartialite` and `python-virtualenv` from your distro's repository.

Then run `sudo make depends` to download required python modules from PyPI repository into your system.

Then run `make all` to make migrations to the database and download extra data for the plug-ins.

Finally run `make serve`. You may now be able to access the application through the port 19843.

#### Development server:

Instead of running `make serve`, run `make devserver` and check `http://localhost:8000`.

## Translations

The software comes preloaded with two translations: Brazilian Portuguese and American English.

### Adding a language

Run `python3 manage.py makemessages -l LL_CC`, where `LL_CC` is your locale name according [DJango's documentation](https://docs.djangoproject.com/en/1.11/topics/i18n/).

### Editing language strings

- Visit the `/rosetta` endpoint in your browser
- Click a language
- Start translating

PS: This is how you edit the content of the pages “Help”, “Privacy” and “Terms”.

### Syncing with whole project

After you edit a template, it'll be required that you re-sync language strings from templates

- Run `python3 manage.py makemessages -a`
- Visit the `/rosetta` endpoint in your browser
- Translate new strings

## Server

The recommended configuration is NGINX reverse-proxying a uWSGI server powered by Python 3, this last one kept alive by systemd.

### SystemD

Just copy the file `server_deploy_config/meet-webapp.service` into `/etc/systemd/system` and adapt it to suit your needs.

Points worth your attention:
- platform absolute path (default: `/var/www/meet`)

### GUnicorn

Just run `make serve` and the web server will be available in the port `19843`. Check how to automate this command at server startup in the topic immediately above.

### NGINX

Just copy the file `server_deploy_config/domain-tld-http.conf` into `/etc/nginx/sites-available` and adapt it to suit your needs.

Points worth your attention:
- ACME snippet for successfully acquiring X.509 certificates from CertBot (default: `/etc/nginx/snippets/acme.conf`)
- TLS and GZIP snippet (default: `/etc/nginx/snippets/tlsgzip.conf`)
- Proxied server location (default: `127.0.0.1:19843`)
- Static files location (default: `/var/www/meet/static`)
- Media files location (default: `/var/www/meet/media`)
- Server name (default: `domain.tld`)

### Apache

It's known that Apache Web Server (2.4.18) with mod-wsgi-py3 (4.3.0) on its default configuration only handles ASCII. There's a fix in [DJango's documentation](https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/modwsgi/) ("Fixing UnicodeEncodeError for file uploads"), but we chose GUnicorn because it works out of the box without any additional configuration.

The server configuration is up to you.

### Python 2.x

TL;DR: Won't run.

Python 2 wasn't targeted during the development. This is because Python 3 series is said to be the present and future of the Python language by its [official wiki](https://wiki.python.org/moin/Python2orPython3).

## Some actions

### Changing site name

Edit file at `secrets/SITE.txt` and restart the WSGI server
<br>
Default: `Meet`

### Changing site domain

Edit file at `secrets/SITE.tld` and restart the WSGI server
<br>
Default: `domain.tld`

### Logging everyone out

Delete file `secrets/SECRET_KEY.bin` and restart the WSGI server

### Deleting all users and all associated data

Delete file `db.sqlite3`, run `make init` and then restart the WSGI server
