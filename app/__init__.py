import os
from datetime import datetime
from flask import Flask, send_from_directory, g, session, redirect, url_for, request
from werkzeug import find_modules, import_string
from playhouse.db_url import connect
from config import *
from flask_pw import Peewee
from flask_debugtoolbar import DebugToolbarExtension
import app.helpers as helpers

app = Flask(__name__)
app.jinja_env.globals.update(html=helpers)
app.jinja_env.filters['currency'] = helpers.format_currency
app.jinja_env.filters['date'] = helpers.format_date
app.jinja_env.filters['time'] = helpers.format_time
app.jinja_env.filters['datetime'] = helpers.format_datetime


app.config.update(prod)
if prod['DEBUG'] is True or prod['DEBUG'] is None:
    app.config.update(dev)
    app.debug = True
db = Peewee(app)
toobar = DebugToolbarExtension(app)
if db:
    import app.models as models
app.cli.add_command(db.cli, 'db')

for name in find_modules('app.blueprints'):
    mod = import_string(name)
    if hasattr(mod, 'blueprint'):
        app.register_blueprint(mod.blueprint)


@app.before_request
def before_request():
    g.startTime = datetime.now()
    g.errors = session.pop("validationErrors", [])
    g.hasErrors = len(g.errors) > 0
    g.data = session.pop("validationData", {})
    g.loggedIn = False
    if "user" in session:
        try:
            g.User = models.User.select().where(models.User.id == session["user"]).get()
            if g.User.isDeleted: # force a logout if the user's account has been deleted
                session.pop("user", None)
            g.loggedIn = True
        except:
            session.pop('user')
            return redirect(url_for('main.login'))
    else:
        if not request.path.startswith('/static') and \
        request.path != url_for('main.login') and request.path != url_for('main.register'):
            return redirect(url_for('main.login'))


@app.teardown_request
def teardown_request(exception):
    pass

if __name__ == '__main__':
    with app.app_context():
        app.cli()