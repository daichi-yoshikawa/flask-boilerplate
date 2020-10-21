from flask import render_template
from . import index_blueprint as index


@index.route('/', methods=['GET'])
def index():
  return render_template('index.html')
