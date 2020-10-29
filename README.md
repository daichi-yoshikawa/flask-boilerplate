# flask-boilerplate
Boilerplate of flask for medium-large application

## Configuration
You're supposed to configure 2 files mode-wise.
* dot.env.default -> ./.env.d/.env.development or .env.production or .env.testing
* config.py.default -> config.py

## Run with development server
At the root dir of the project, run the follow.
```
$ FLASK_ENV=<mode> FLASK_APP=app flask run
```

## Run with gunicorn
At the root dir of the project, run the follow.
```
$ FLASK_ENV=<mode> python gunicorn.py
```

## DB migration
```
$ FLASK_ENV=<mode> FLASK_APP=app flask db init
$ flask db migrate -m "initial migration"
$ flask db upgrade
```

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
