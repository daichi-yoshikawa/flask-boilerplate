# flask-boilerplate
Boilerplate of flask for medium-large application

## Configuration
You're supposed to configure 2 files mode-wise.
* dot.env.default -> .env.development/.env.production/.env.testing
* config.py.default -> config.py

The above files must be stored under root directory.

## Run
```
FLASK_ENV=<mode> FLASK_APP=app flask run
```

## DB migration
```
FLASK_ENV=<mode> FLASK_APP=app flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

## Execute pytest
```
pip install -e .
```
