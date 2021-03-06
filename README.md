# 2019-SocialMeetScheduler
Assignment for the 2019 edition of the "Web Development and the Semantic Web" course, by Ádler Oliveira Silva Neves.

The tutorial below assumes you are already inside folder `implementation/` from this repository.

## How to run

First, install `python3`, `automake`, `gdal`, `geos`, `libspartialite` and `python-virtualenv` from your distro's repository.

Or, if you prefer PostgreSQL instead of SQLite + SpartiaLite, also install `postgis` from your distro's repository (assuming that PostgreSQL is already installed).

Then run `sudo make depends` to download required python modules from PyPI repository into your system.

Then run `make all` to make migrations to the database and download extra data for the plug-ins.

Finally run `make serve`. You may now be able to access the application through the port 19843.

#### Development server:

Instead of running `make serve`, run `make devserver` and check `http://localhost:8000`.

## Translations

The software comes preloaded with two translations: Brazilian Portuguese and American English.

### Adding a language

Run `LANG=ll_CC make addlang`, where `ll_CC` is your locale name according [DJango's documentation](https://docs.djangoproject.com/en/1.11/topics/i18n/).

### Editing language strings

- Visit the `/rosetta` endpoint in your browser
- Click a language
- Start translating

PS: This is how you edit the content of the pages “Help”, “Privacy” and “Terms”.

### Syncing with whole project

After you edit a template, it'll be required that you re-sync language strings from templates

- Run `make updatelangs`
- Visit the `/rosetta` endpoint in your browser
- Translate new strings

## Server

The recommended configuration is NGINX reverse-proxying a uWSGI server powered by Python 3, this last one kept alive by systemd.

### Easy deployment

Run `make deploy` and wait it install itself. Further configuration might be necessary; run `systemctl restart meet-webapp.service` to reload the configurations.

### Domain

Edit `server_secrets/SITE.tld` (will be autogenerated if absent) [default absolute path: `/var/www/meet/server_secrets/SITE.tld`] and replace the content (default: `domain.tld`) to match your domain.

You might get a generic `Error 500` page if you deploy without configuring this properly.

### Persistence

There are two pesistence choices: (1) SQLite + SpartiaLite and (2) PostgreSQL + PostGIS.

#### SQLite + SpartiaLite

The default configuration; zero configuration needed.

#### PostgreSQL + PostGIS

Create a database and enable PostGIS on it. You can do that from the psql shell with commands like the one below:

```sql
create user dbuser with password 'dbpass';
-- CREATE ROLE
create database dbname with owner dbuser;
-- CREATE DATABASE
\c dbname
-- You are now connected to database "dbname" as user "postgre".
CREATE EXTENSION postgis;
-- CREATE EXTENSION
\q
```

Edit `server_secrets/extraconfig.py` (will be autogenerated (as an empty file) if absent) [default absolute path: `/var/www/meet/server_secrets/extraconfig.py`] and add the following lines, replacing by your database credentials where appropiate:

```py
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'dbname',
        'USER': 'dbuser',
        'PASSWORD': 'dbpass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Email

Edit `server_secrets/extraconfig.py` (will be autogenerated (as an empty file) if absent) [default absolute path: `/var/www/meet/server_secrets/extraconfig.py`] and add the following lines, replacing by your mail server credentials where appropiate:

```py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = 'mailuser'
EMAIL_HOST_PASSWORD = 'mailpass'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

#### GMail

Some people might want to use a GMail account to send email for the site, which would be configured somewhat like this:

```py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'mailuser@gmail.com'
EMAIL_HOST_PASSWORD = 'mailpass'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'mailuser@gmail.com'
REGISTRATION_DEFAULT_FROM_EMAIL = 'mailuser@gmail.com'
```

This somewhat easier approach (than setting an email server up), however, [has several limitations](https://support.google.com/a/answer/166852).

### Crontab setup

Edit your crontab (with `crontab -e`) and add these lines:

```sh
 * * * * * cronic make sendstaremails -C /var/www/meet
```

```sh
 0 * * * * cronic systemctl restart meet-sparql.service
```

### Docker

If you choose to run inside Docker, there are 3 helpers:

- `make builddocker`
- `make rundocker`
- `make stopdocker`

Tested on a Ubuntu 18.04 virtual machine; it doesn't trigger cron-dependent features.

This Docker approach will only run the python server, still requiring a reverse proxy to be deployed (such as NGINX).

### SystemD

Just copy the file `server_deploy_config/meet-webapp.service` into `/etc/systemd/system` and adapt it to suit your needs.

Points worth your attention:
- platform absolute path (default: `/var/www/meet`)

### GUnicorn

Just run `make serve` and the web server will be available in the port `19843`. Check how to automate this command at server startup in the topic immediately above.

### NGINX

Just copy the file `server_deploy_config/domain-tld-http.conf` into `/etc/nginx/sites-available`, rename, adapt it to suit your needs and symlink to `/etc/nginx/sites-enabled`.

Points worth your attention:
- ACME snippet for successfully acquiring X.509 certificates from CertBot (default: `/etc/nginx/snippets/acme.conf`)
- TLS and GZIP snippet (default: `/etc/nginx/snippets/tlsgzip.conf`)
- Proxied server location (default: `127.0.0.1:19843`)
- Static files location (default: `/var/www/meet/static`)
- Media files location (default: `/var/www/meet/media`)
- Server name (default: `domain.tld`)

(and don't forget to reload NGINX configuration)

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
