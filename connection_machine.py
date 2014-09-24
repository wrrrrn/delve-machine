from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from data_models import models

Nietzsche = """
    There are various eyes.
    Even the Sphinx has eyes: and as a result there are various truths,
    and as a result there is no truth."""

app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/document')
def document():
    url = 'http://www.guardian.co.uk/politics/2012/apr/20/cameron-family-tax-havens'
    article = g.extract(url=url)
    mentions = {'type': 'name', 'name': u'Parliament'}
    return render_template(
        'article.html',
        title=article.title,
        content=format_content(article.cleaned_text),
        mentions=mentions,
        description=article.meta_description,
        domain=article.domain
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
    g.db = connect_db()
