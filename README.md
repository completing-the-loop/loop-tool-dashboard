# cloop Project
* [Overview](#overview)
 * [Purpose](#purpose)
 * [Tech Stack](#tech-stack)
* [Architecture](#architecture)
* [Development](#development)
 * [Staging](#staging)
* [Deployment](#deployment)

master: [![build status](https://gitlab.internal.alliancesoftware.com.au/melbuni/cloop/badges/master/build.svg)](https://gitlab.internal.alliancesoftware.com.au/melbuni/cloop/commits/master)

## Overview

### Purpose

A web app for generating widgets

Key functionality
* Do things


### Tech Stack
* Ubuntu 14 LTS
* nginx + gunicorn
* Python 3.4
* Django 1.11
* MySQL 5.6
* node 6 (dev only)
* Bootstrap


## Architecture

* Standard django app
 * Not a single page app (No React or Angular)
* Interesting things
* Javascript for the entire site is aggregated using `django-compress`
* Admin is accessible only to staff
  * `django-stronghold` means login required by default

## Development

### Install Dependencies

* Setup git hooks. This adds a pre-commit hook to validate imports are sorted.

```bash
cd .git
rm -rf hooks
ln -s ../git-hooks hooks
```

* Install OS packages

```bash
brew install nonstandard-package1
brew install nonstandard-package2
# (Don't need to list DB packages or core python here; they are assumed)
```

* Create & activate a python 3 virtualenv
```bash
# (use --system-site-packages so the pytz from os is inherited)
virtualenv --system-site-packages -p $(which python3) venv
source venv/bin/activate
```

* Activate node version (`nvm use`)
* Install package dependencies:

```bash
nvm use
cd frontend && yarn install
cd myproject/requirements && pip install -r dev.txt
```

### Configuration
* Add your hostname to `_dev_hosts` in `django-root/django_site/settings/__init__.py` (if you're not sure what to add, wait until you run the django server later and it will tell you what hostname it detected)
* (mysql only) Add database username/password to `django-root/django_site/settings/dev.py` (will read from `~/.my.cnf` if not specified)

### Database Setup

* Run `bin/resetdb.sh`
 * CAUTION: If you are using a `~/.my.cnf` settings file, make sure you have not pointed it at a previous database or you will overwrite it
* Or manually:

```bash
cd django-root
./manage.py migrate
./manage.py loaddata groups dev
```

### Dev Servers

* (webpack only) Webpack dev server

```bash
cd frontend
yarn run dev
```

* Django server

```bash
cd django-root
./mange.py runserver_plus
```

### Testing

```bash
cd django-root
./manage.py test --keepdb
```

### Staging
* Staging environment is located at tt:client=123#account_1234
 * You can also use TT links like tt:client=123 tt:staff=123 tt:wiki=Hello_World
* Staging database can be reset from live by running `~/bin/resetstaging.sh`

## Deployment

* Deployed on Rackspace
 * nginx frontend web server
 * gunicorn fastcgi wsgi behind nginx
* gunicorn configured as a system daemon called `myproject`
* Site settings are in `~/env`

### Production Build

* (webpack only) Build assets

```bash
cd frontend
yarn run build
```

* Commit changes and push to `master` branch

### Update Server

#### Staging

* Reset the staging DB from live DB (see [Staging](#staging) )
* Follow instructions for a live deployment with the following changes:
 * Don't create a `sendlive` tag; check out `master` instead
 * Can skip maintenance mode
 * Deployment directory is `~/stagingsite`
 * Service to reload is `myprojectstaging`

#### Live

* Tag and push the release: `git tag sendlive/YYYYMMDD-hhmm && git push`
* SSH to the server using details at tt:accountId=1234
* Create a DB backup
 * `~/bin/dbdump.sh`
* Verify that there are no uncommitted changes on the server: `cd ~/livesite && git status`
* Enable maintenance mode
 * ???
* Update code

```bash
cd ~/livesite
git fetch
git checkout sendlive/YYYYMMDD-hhmm
cd django-root
./manage.py migrate
./manage.py collectstatic
service myproject reload
```

* If something goes wrong, restore database and checkout previous sendlive tag
* Disable maintenance mode
