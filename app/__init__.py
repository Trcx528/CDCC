import os
from datetime import datetime
from flask import Flask, send_from_directory, g, session, redirect, url_for, request
from flask_script import Manager
from werkzeug import find_modules, import_string
from playhouse.db_url import connect
from config import prod
from flask_pw import Peewee
import app.helpers as helpers
from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__)
app.jinja_env.globals.update(html=helpers)
app.config.update(prod)
if app.debug is None:
    from config import dev
    app.config.update(dev)
    app.debug = True
db = Peewee(app)
if db:
    import app.models as models
toolbar = DebugToolbarExtension(app)
manager = Manager(app)
manager.add_command('db', db.manager)


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
        g.User = models.User.select().where(models.User.id == session["user"]).get()
        g.loggedIn = True
    else:
        if not request.path.startswith('/static') and request.path != url_for('main.login') and request.path != url_for('main.register'):
            return redirect(url_for('main.login'))


@app.teardown_request
def teardown_request(exception):
    pass
