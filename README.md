# flask-boilerplate
Boilerplate of flask for medium-large application

## Configuration
### Edit .env file.
Create .env.XXXX file under .env.d/ directory, like .env.d/.env.development.

Here is a list of environment variables.
* FLASK_TEMPLATE_DIR : Absolute/Relative path to a entry point (usually directory containing index.html).
* FLASK_STATIC_DIR : Absolute/Relative path to a directory containing asset files(js files, image files, etc.)
* FLASK_SECRET_KEY : Used to identify the process. Practically, if you change this value, tokens given to users before the change would get invalid.
* JWT_SECRET_KEY : Used with FLASK_SECRET_KEY. If you change this value or FLASK_SECRET_KEY, tokens given to users before the change would get invalid.
* POSTGRES_USER : Not necessary. Username of postgres. Can be used in config.py described later.
* POSTGRES_PASSWORD : Not necessary. Password of postgres. Can be used in config.py described later.
* POSTGRES_HOST : Not necessary. IP address or hostname of postgres. Can be used in config.py described later.
* POSTGRES_NAME : Not necessary. DB name of postgres. Can be used in config.py described later.
* BLACKLIST_STORAGE_TYPE : Take one of memory(not recommended), redis, or database. Memory means that it stores revoked token by python set() data(therefore revoked tokens are all gone once the server is down). If set to database, database configured by SQLALCHEMY_DATABASE_URI in config.py is used to store the data.
* REDIS_HOST : Not necessary. IP address or hostname of redis. Can be used in config.py described later.
* REDIS_PASSWORD : Not necessary. Password of redis. Can be used in config.py described later.
* REDIS_PORT : Not necessary. Port of redis. Can be used in config.py described later.
* REDIS_DB_INDEX : Not necessary. DB index of redis. Can be used in config.py described later.

### Edit config.py.
Create config.py from config.py.default.

Majorly you may edit the follows (or more).
* JWT_ACCESS_TOKEN_EXPIRES : Expiration period of access token in seconds.
* JWT_REFRESH_TOKEN_EXPIRES : Expiration period of refresh token in seconds.
* config\['app'\]\['default'\]\['REDIS_XXXX'\] : If redis is not used for blacklist, you should delete these.
* config\['app'\]\['XXXX'\]\['SQLALCHEMY_DATABASE_URI'\] : Depending on database, you can configure here.

### Example of SQLALCHEMY_DATABASE_URI
* MySQL : mysql://username:password@hostname/database
* Postgres : postgresql://username:password@hostname/database
* SQLite : sqlite:////absolute/path/to/database

### Blacklist
Blacklist, which is used to revoke tokens, can be implemented with memory(not recommended), 
Redis, or SQLite by default.

If Redis is used, you can delete app/models/revoked_token.py and delete the following line
in app/models/__init__.py.
```
from .revoked_token import RevokedToken
```
Also, remove the the following line and class DatabaseStorage in app/auth/blacklist.py
```
from app.models.revoked_token import RevokedToken
```

## Usage
### DB initialization/migration
```
$ FLASK_ENV=<mode> FLASK_APP=app flask db init
$ FLASK_ENV=<mode> flask db migrate -m "initial migration"
$ FLASK_ENV=<mode> flask db upgrade
```

### Insert default data into database.
```
$ FLASK_ENV=<mode> python insert_default_data.py
```

### Run with flask development server
At the root dir of the project, run the follow.
```
$ FLASK_ENV=<mode> FLASK_APP=app flask run
```

### With gunicorn (simply call gunicorn)
At the root dir of the project, run the follow.
```
$ FLASK_ENV=<mode> python gunicorn.py
```

### With gunicorn and docker-compose
1. Edit FLASK_TEMPLATE_DIR and FLASK_STATIC_DIR in .env.d/.env.XXXX file.
2. Edit volumes in docker-compose.yml. /root/vue-app/dist must correspond to the directory which containing index.html, that is, FLASK_TEMPLATE_DIR.
3. Do the follow.
```
$ docker-compose build
$ FLASK_ENV=<mode> docker-compose run -d --name flask-gunicorn-server flask-gunicorn
```

### With gunicorn and systemd
(Assuming Linux is used.)<br>
Create a symbolic link of XXXX.service file(eg. flask-gunicorn.service) and put it under /etc/systemd/system directory.
```
$ cd root/to/flask/application
$ sudo ln -s $(pwd)/flask-gunicorn.service /etc/systemd/system
```

Make sure the service uses correct .env file. See EnvironmentFile parameter under Service in service file.
```
[Service]
EnvironmentFile=absolute/path/to/.env.d/.env.<mode>

(Example)
[Service]
EnvironmentFile=/home/ubuntu/work/flask-app/.env.d/.env.production
```

Reload daemon and start gunicorn manually.
```
$ sudo systemctl daemon-reload
$ sudo systemctl start flask-gunicorn
```

Make sure if it's successfully running.
```
$ ps aux | grep flask-gunicorn
```

If no result is seen, see log.
```
$ journalctl -xe
```

To update gunicorn parameters while it's running as a daemon, firstly edit .env file(eg. GUNICORN_WORKERS=1 -> GUNICORN_WORKERS=4) or service file directly. And then call the follow.
```
$ sudo systemctl restart flask-gunirocn
```

### To kill gunicorn launched by systemd
As far as Restart=always is in service file, the service is re-launched even if the process is down. Firstly, comment out the line as below.
```
[Service]
...
# Restart=always
```
Then check process ids of gunicorn.
```
$ ps aux | grep flask-gunicorn
```
Send signal to shutdown the processes.
```
$ kill -9 <process ID(s)>
```
You'll see multiple processes even if the number of workers is 1. One of the process is a master process and if you shutdown it all other associated workers are also gone.

## Execute pytest
If you need to access database, make sure that DB migration is already done.<br>
And then install your project package as below.
```
$ pip install -e .
```
At the root dir of the project, run the follow. Default options of pytest are defined in pytest.ini file.
```
$ pytest
```
