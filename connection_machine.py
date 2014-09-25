from flask import Flask, url_for, render_template
from web.controllers import documents
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
    url = 'http://chrishanretty.co.uk/blog/index.php/2014/09/13/what-can-deutsche-bank-possibly-mean/'
    doc = documents.DocumentController(url)
    properties = doc.get_properties()
    if properties:
        return render_template(
            'article.html',
            title=properties["title"],
            content=format_content(properties["content"]),
            mentions=properties["mentions"],
            domain=properties["domain"]
        )


def format_content(string):
    old_content = string.split("\n\n")
    new_content = ""
    for para in old_content:
        new_content += "<p>%s</p>" % para
    return new_content


@app.route('/<search_type>/<search_term>')
def show_entries(search_type, search_term):
    if search_type == 'name':
        entity = new_models.NamedEntity(search_term, db=g.db)
        if not entity.exists:
            abort(404)
    elif search_type == 'term':
        entity = new_models.UniqueTerm(search_term, db=g.db)
        if not entity.exists:
            abort(404)
    elif search_type == 'article':
        entity = new_models.Article(search_term, db=g.db)
        if not entity.exists:
            abort(404)
        else:
            return render_template(
                'article.html',
                title=entity.title,
                content=entity.content,
                mentions=entity.mentions(),
                description=Nietzsche,
                domain="www.next-hype.co.uk"
            )
    return render_template('show_entries.html', entity=entity)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
    app.run()

