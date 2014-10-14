from flask import Flask, url_for, render_template, abort
from web.controllers import documents
from web.controllers import mps
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


@app.route('/mps')
def show_mps():
    aggregate = mps.MpAggregateController()
    return render_template('show_mps.html', entity=aggregate)


@app.route('/document')
def document():
    doc_id = '54234698e226df11893507ec'
    entity = documents.DocumentController(doc_id)
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

