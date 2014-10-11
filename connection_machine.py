from flask import Flask, url_for, render_template, abort
from web.controllers import documents
from web.controllers import named_entities
from web.controllers import unique_terms
import os

template_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'web/templates'
)
static_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'web/static'
)
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(__name__)


@app.route('/document')
def document():
    url = 'http://owni.eu/2012/09/06/13-of-the-newest-political-and-civic-tools/'
    entity = documents.DocumentController(url)
    if entity.exists:
        return render_template('show_document.html', entity=entity)
    else:
        abort(404)


@app.route('/<search_type>/<search_term>')
def show_entries(search_type, search_term):
    if search_type == 'name':
        entity = named_entities.NamedEntityController(search_term)
        if entity.exists:
            return render_template('show_names.html', entity=entity)
    elif search_type == 'term':
        entity = unique_terms.UniqueTermsController(search_term)
        if entity.exists:
            return render_template('show_terms.html', entity=entity)
    elif search_type == 'document':
        entity = documents.DocumentController(search_term)
        if entity.exists:
            return render_template('show_document.html', entity=entity)
    else:
        abort(404)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
    app.run()

