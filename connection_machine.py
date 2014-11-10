from flask import Flask, url_for, render_template, abort
from flask.ext.restful import Api, Resource, reqparse
from web.controllers import documents
from web.controllers import mps
from web.controllers import named_entities
from web.controllers import unique_terms
from web.api import mps_api
import os

template_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'web/templates'
)
static_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'web/static'
)
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(__name__)
api = Api(app)


@app.route('/mps')
def show_mps():
    aggregate = mps.MpAggregateController()
    return render_template('show_mps.html', entity=aggregate)

@app.route('/test')
def show_test():
    return render_template('show_mps_api.html', entity=None)


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


class MpsList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('type', type=str)
        super(MpsList, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        mps = mps_api.MpsApi()
        if args["type"] == "government":
            all = mps.get_government()
        if args["type"] == "opposition":
            all = mps.get_opposition()
        else:
            all = mps.get_all()
        return all

api.add_resource(MpsList, '/api/v0.1/mps', endpoint='mps')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
    app.run()

