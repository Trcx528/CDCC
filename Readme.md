## Flask Template ##

This repository has a sample flask template to be used as a base for larger flask projects.  It uses [bootstrap](http://getbootstrap.com/) and [jquery](http://jquery.com/) for the front end and [peewee](http://docs.peewee-orm.com/en/latest/index.html) and [flask](http://flask.pocoo.org/) for the backend.  Peewee supports many different databases including but not limited to mysql, postgres and sqlite.  This project uses [flask-pw](https://github.com/klen/flask-pw) for peewee flask integration and takes advantage of the migrations offered through this package.  Additionally [flask-debugtoolbar](https://github.com/mgood/flask-debugtoolbar) is used to ease development and debugging.  Finally [flask-script](http://flask-script.readthedocs.io/en/latest/) enables command line interaction with flask and an easy way to start up a dev environment.

#### Getting Started ####

```shell
git clone http://git.jdp.tech/Trcx/FlaskTemplate
cd FlaskTemplate
vi config.py
# (Optional) setup virtalenv to keep the host system clean
virtualenv env
env/bin/activate
# install the dependencies
pip install flask-pw flask-script flask-debugtoolbar
# Create the database by running the migrations
python run.py db migrate
# start the app without debugging
python run.py runserver
# start the app with debugging, automatic reloads and multithreading
python run.py runserver -d -r --threaded
```

#### Validation ####
Validation is done by tagging each function with the `@validate` decorator from `app/validation.py` and passing in all the form parameters and their expected type.  
```python
@blueprint.route('/login', methods=['POST'])
# just validate that they are both there, we'll check the rest in our below function
@validate(LoginEmail="email|required", LoginPassword="str|required")
def login():
    pass
```
The above example will ensure that the user entered string values for both `LoginEmail` and `LoginPassword` and will ensure that `LoginEmail` is in the correct format.  Validators can also transform the values that are passed to them.  We could create our own custom validator to convert `LoginEmail` to a `User` object from the database.  The transformed values are exposed in the `g.data` dictionary.

```python
# in validation.py
from app.models import User
def valUser(value, fieldName=None, exists=False, **commonArgs):
    value, errors = valEmail(value, fieldName, **commonArgs)
    u = User.select().where(User.EmailAddress == value).get()
    if not u:
        errors.append("User Does Not Exist")
    return u, errors
registerValidator("user", valUser)
...
@validate(LoginEmail="user|required|exists", LoginPassword="str|required")
```

If validation fails it redirects to the previous page and, if properly using the helpers, will indicate which fields failed validation and why.  Finally be sure to call the `html.csrf_token()` helper within each form otherwise the validation will fail and return a 400.  This prevents cross site request forgery.  This behavior can be disabled by passing `csrf_protection=False` to  the `validate` decorator.


#### Helpers ####
 `app/helpers.py` introduces various functions to generate html in templates.  Some of the included functions interact with the validation layer to automatically display errors below the invalid fields and highlight the field.  These helpers are exposed to templates in the html namespace.  See `app/templates/main/form.html` for an example of building a simple form with these functions.  Any functions added to `helpers.py` will automatically be made available under this html namespace.  


#### Blueprints ####
This framework makes use of the built in flask blueprint system for adding additional endpoints and for organizational purposes.  Blueprints should be stored in the `app/blueprints` folder and should name the blueprint `blueprint`.  This allows the app to automatically load and register the blueprint without needing any additional code. An example blueprint can be seen in `app/blueprints.main.py`.


#### Database Migrations ####
Flask-pw supports automatically generating migrations.  To create a new migration make the changes to your models, then run `python run.py db create -a $name` replacing `$name` with a name for this migration.  This will cause Flask-pw to compare the models with the database and generate a migration script that will add and remove fields to the database such that the two definitions match.  You can then run this migration by running `python run.py db migrate`.


#### Authentication ####
Finally this template has a basic auth system.  One can register for an account and then login to it.  This is all done in the `app/blueprints/main.py` blueprint.  When the user id is stored into `session['user']`, and the full user object is loaded by this id at each page load into `g.User`.  Additionally `g.loggedIn` is loaded to make it easy for templates to detect if the user is logged in.  An example of this is `app/templates/layout.html` replacing the login form with a logout button depending on the user's login status.
