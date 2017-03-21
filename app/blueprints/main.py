from flask import Blueprint, render_template, request, g, flash, redirect, url_for, session
from app.validation import validate
from app.models import User

blueprint = Blueprint('main', __name__)


@blueprint.route('/')
def index():
    return render_template('main/index.html')


@blueprint.route('/register')
def register():
    return render_template('main/register.html')


@blueprint.route('/register', methods=['POST'])
@validate(FirstName="str|required", LastName="str|required", EmailAddress="email|required|dbunique",
          Password="str|required|minlength=8", ConfirmPassword="str|required|matches=Password")
def processRegister(firstName, lastName, emailAddress, password):
    newUser = User(firstName=firstName, lastName=lastName, emailAddress=emailAddress)
    newUser.setPassword(password)
    # temporary until we're in prod
    newUser.isAdmin = True
    newUser.save()
    flash("User Registered Sucessfully", 'success')
    return redirect(url_for('main.index'))


@blueprint.route('/login', methods=['POST', 'GET'])
@validate(LoginEmail="str", LoginPassword="str")
def login(loginEmail=None, loginPassword=None):
    if request.method == 'GET':
        return render_template('main/login.html')
    loginUser = User.select().where(User.emailAddress == loginEmail).count()
    if loginUser > 0:
        loginUser = User.select().where(User.emailAddress == loginEmail).get()
        if loginUser.checkPassword(loginPassword):
            g.loggedIn = True
            session["user"] = loginUser.id
        else:
            flash("Invalid Email Address Or Password", "error")
    else:
        flash("Invalid Email Address Or Password", "error")
    return redirect(url_for('main.index'))


@blueprint.route('/logout', methods=['POST'])
def logout():
    session.pop("user", None)
    flash("Logged Out!", "success")
    return redirect(request.referrer)
