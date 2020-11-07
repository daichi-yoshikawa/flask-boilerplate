from flask import render_template
from . import index_blueprint as index


@index.route('/', defaults={'path': ''})
@index.route('/<path:path>')
def catch_all(path):
  try:
    return render_template('index.html')
  except TemplateNotFound:
    abort(404)


