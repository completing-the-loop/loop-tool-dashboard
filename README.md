# cloop Project
* [Overview](#overview)
 * [Purpose](#purpose)
 * [Tech Stack](#tech-stack)
* [Architecture](#architecture)
* [Development](#development)
 * [Staging](#staging)
* [Deployment](#deployment)



## Overview

### Purpose

A web application to provide insights and visualisations on the use of a Learning Management System by students.

Key functionality
* Import resource and usage data for courses from an LMS (currently only Blackboard is supported)
* Allow the definition of various events throughout a course
* Display summaries and visualisations of the usage and event data


### Tech Stack
* Ubuntu 14 LTS
* nginx + gunicorn
* Python 3.5
* Django 1.11
* MySQL 5.6
* node 6 (dev only)
* Bootstrap
* RabbitMQ (http://www.rabbitmq.com/) - for Celery broker


## Architecture

* Standard django app with Vue instances on many pages
* Course data is accessible only to assigned course owners
* Admin is accessible only to system administrators
  * `django-stronghold` means login required by default
* Celery (with RAbbitMQ broker) used to process the LMS export data
  

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
brew install rabbitmq
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
cd requirements && pip install -r dev.txt
```

### Configuration
* Add your hostname to `_dev_hosts` in `django-root/django_site/settings/__init__.py` (if you're not sure what to add, wait until you run the django server later and it will tell you what hostname it detected)
* (mysql only) Add database username/password to `django-root/django_site/settings/dev.py` (will read from `~/.my.cnf` if not specified)

### Create Data Directories
* Unless you've changed the default directories in `django-root/django_site/settings/`, create the following directories in the top-level project folder:

```
mkdir log data data_imports import_errors
```

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
./manage.py runserver_plus
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

### Install system packages
* nginx
* mysql-server
* rabbitmq-server
* python3-devel
* libmysqlclient-dev
* virtualenv

### Configure Nginx
* Reverse proxies for Gunicorn
* Serves static content

#### Sample Configuration
* eg. `/etc/nginx/sites-anabled/loop`
* You may need to change path for `proxy_path`
~~~~
server {
	listen 80 ;
	listen [::]:80 ;

	root /home/loop/website;

	server_name circle.its.unimelb.edu.au;

	location /static/ { }
	location /media/ { }

	location / {
		proxy_set_header Host               $http_host;
		proxy_set_header X-Real-IP          $remote_addr;
		proxy_set_header X-Forwarded-For    $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto  $scheme;
		proxy_set_header Upgrade            $http_upgrade;
		proxy_set_header Connection         "upgrade";
		proxy_pass http://unix:/home/loop/run/gunicorn.socket;
		#proxy_ignore_client_abort   off;
		#proxy_intercept_errors      off;
		#proxy_redirect              off;

		## max client upload size
		client_max_body_size        24m;
		#
		## buffer size before using a temp file for client upload
		#client_body_buffer_size 128k;
		#
		## tcp connection timeout
		#proxy_connect_timeout       10;
		#
		## timeout between 2 write operations once connected
		#proxy_send_timeout          120;
		#
		## timeout between 2 read operations once connected
		#proxy_read_timeout          120;
		#
		#proxy_buffers               8   16k;
		#proxy_buffer_size           32k;
	}
}
~~~~

### Configure mysql
* Create database (eg `loop_django`)
* Create user (eg `loop`)

### Configure RabbitMQ
* Create rabbitmq user and vhost
  * `rabbitmqctl add_vhost loop`
  * `rabbitmqctl add_user loop agoodpassword`
  * `rabbitmqctl set_permissions -p loop loop ".*" ".*" ".*"`

### Deploy & configure application
* Switch to application user (loop)
* Create virtual environment
  * `mkdir ~/.venv`
  * `virtualenv -p python3 ~/.venv/melbuni-cloop`
* Activate virtualenv
  * `source ~/.venv/melbuni-cloop/bin/activate`
* Checkout application
  * `git clone ... loop.git`
* In app directory (`loop.git`)
  * `pip install -r requirements.txt`
* Create content symlinks
  * `ln -s loop.git ~/website`
  * `ln -s assets ~/website/static`
* Create place for runtime files to live
  * `mkdir ~/run`
* Create application configuration file (`~/.env`)
  * Example:

~~~~
DJANGO_SETTINGS_MODULE=django_site.settings.production_prod
SECRET_KEY=SECRET_KEY_HERE

DB_HOST=localhost
DB_NAME=loop_django
DB_USER=loop
DB_PASSWORD=MYSQL_PASSWORD_HERE

RABBITMQ_HOSTNAME=localhost
RABBITMQ_PORT=5672
RABBITMQ_VHOST=loop
RABBITMQ_USER=loop
RABBITMQ_PASSWORD=RABBITMQ_PASSWORD_HERE

DATA_IMPORT_DIR=/home/loop/import
DATA_PROCESSING_DIR=/home/loop/processing
DATA_ERROR_LOGS_DIR=/home/loop/import_errors

CLOOP_IMPORT_ADMINS=ADMIN_EMAIL_ADDRESS1,ADMIN_EMAIL_ADDRESS2,...
ADMINS=ADMIN_EMAIL_ADDRESS1,ADMIN_EMAIL_ADDRESS2,...
~~~~
* Ensure the existence of the folders created for,
  * `DATA_IMPORT_DIR`
  * `DATA_PROCESSING_DIR`
  * `DATA_ERROR_LOGS_DIR`
* Initialize Django
  * `cd ~/website/django-root`
  * `./manage.py migrate`
  * `./manage.py createsuperuser`
  * `./manage.py collectstatic`

### Configure application services
* 3 services need to be running for Loop:
  * gunicorn (webserver)
  * celery worker (background data processing)
  * celery beat (task scheduler)
* This documentation assumes you are using `circus` to run these services.
* You also need to ensure `circusd` starts on boot with the below config file & the variables from the `.env` file loaded.
* This would normally be done via `systemd`
  * But is currently done via crontab or manually since we don't have the ability to create a service definition
  * See `~/start.sh`
* `mkdir ~/conf`
* Example circus.conf (`~/conf/circus.conf`)

~~~~
[circus]
endpoint=ipc:///home/loop/run/circus.sock

[watcher:gunicorn]
cmd=/home/loop/.venv/unimelb-cloop/bin/gunicorn --workers 4 -b unix:/home/loop/run/gunicorn.socket wsgi:application
working_dir=/home/loop/website/django-root
copy_env=true

[watcher:celeryd]
cmd = /home/loop/.venv/unimelb-cloop/bin/celery worker -A django_site -b  amqp://$(CIRCUS.ENV.RABBITMQ_USER):$(CIRCUS.ENV.RABBITMQ_PASSWORD)@$(CIRCUS.ENV.RABBITMQ_HOSTNAME)/$(CIRCUS.ENV.RABBITMQ_VHOST)
working_dir=/home/loop/website/django-root
copy_env=true

[watcher:celerybeat]
cmd = /home/loop/.venv/unimelb-cloop/bin/celery beat -A django_site -b  amqp://$(CIRCUS.ENV.RABBITMQ_USER):$(CIRCUS.ENV.RABBITMQ_PASSWORD)@$(CIRCUS.ENV.RABBITMQ_HOSTNAME)/$(CIRCUS.ENV.RABBITMQ_VHOST)
working_dir=/home/loop/website/django-root
copy_env=true
~~~~

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

* Tag and push the release: `git tag sendlive/YYYY/MMDD-hhmm && git push`
* SSH to the server
* Create a DB backup
 * `~/bin/dbdump.sh`
* Verify that there are no uncommitted changes on the server: `cd ~/livesite && git status`
* Enable maintenance mode
 * ???
* Update code

```bash
cd ~/loop.git
git fetch
git checkout sendlive/YYYY/MMDD-hhmm
cd django-root
./manage.py migrate
./manage.py collectstatic
#service loop reload
~/bin/start.sh
```

* If something goes wrong, restore database and checkout previous sendlive tag
* Disable maintenance mode

### Create data import files

The following files need to be zipped and deposited in the data-import directory (fieldnames and example entries included below):

* activity.txt
 * request data (in Blackboard, from the activity accumulator)
 * used for incremental data
```
user_key|content_key|forum_key|timestamp
12345|1234567||2018-05-07T09:29:01.000000+11:00
```

* all_resources.txt
 * all resources used in the subject at any time
```
content_key|parent_content_key|title|resource_type
12345|1234567|Week 1 Readings|resource/x-bb-folder
```

* all_user.txt
 * all users who have existing in the course
```
user_key|username|firstname|lastname|email
122222|studenta|John|Smithson|john.smithson@example.edu.au
```

*  assessments.txt
 * tests and assignments
 * used in incremental loads
```
user_key|content_key|user_grade|timestamp
122222|1234567|22|2018-05-09T20:53:02.000000+11:00
```

*  forums.txt
 * discussion boards, threads and posts
 * used in incremental loads
```
forum_key|user_key|thread|post|timestamp
123456|122222|Week 1 Discussion|Re: Introductions|2016-05-08T11:15:04+11:00
```

* resources.txt
 * folders and content items in a course
 * used in incremental loads
```
content_key|parent_content_key|title|resource_type
12345|1234567|Week 2 Readings|resource/x-bb-folder
```

* user.txt
 * users in the course
 * used in incremental loads
```
user_key|username|firstname|lastname|email
122222|studenta|John|Smithson|john.smithson@example.edu.au
```
