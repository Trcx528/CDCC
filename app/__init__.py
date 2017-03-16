import os
from datetime import datetime
from flask import Flask, send_from_directory, g, session, redirect, url_for, request
from flask_script import Manager, Server
from werkzeug import find_modules, import_string
from playhouse.db_url import connect
from config import *
from flask_pw import Peewee
import app.helpers as helpers
from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__)
app.jinja_env.globals.update(html=helpers)
app.config.update(prod)
if prod['DEBUG'] is True or prod['DEBUG'] is None:
    app.config.update(dev)
    app.debug = True
db = Peewee(app)
if db:
    import app.models as models
toolbar = DebugToolbarExtension(app)
manager = Manager(app)
manager.add_command('db', db.manager)

extra_dirs = ['templates',]
extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in os.walk(extra_dir):
        for filename in files:
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                extra_files.append(filename)
manager.add_command("runserver", Server(extra_files=extra_files))


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
        if not request.path.startswith('/static') and \
        request.path != url_for('main.login') and request.path != url_for('main.register'):
            return redirect(url_for('main.login'))


@app.teardown_request
def teardown_request(exception):
    pass
