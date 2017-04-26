""" This file contains all basic views and logic such as login/out and the homepage """

from datetime import datetime
from flask import Blueprint, render_template, request, g, flash, redirect, url_for, session
from app.validation import validate
from app.models import *
from app.logic import *


blueprint = Blueprint('main', __name__)


@blueprint.route('/')
def index():
    """Displays the homepage"""
    return render_template('main/index.html')


@blueprint.route('/register')
def register():
    """Gathers information for a new User"""
    return render_template('main/register.html')


@blueprint.route('/register', methods=['POST'])
@validate(FirstName="str|required", LastName="str|required", EmailAddress="userEmail|required",
          Password="str|required|minlength=8", ConfirmPassword="str|required|matches=Password")
def processRegister(firstName, lastName, emailAddress, password):
    """Creates a new User based on POST data"""
    newUser = User(firstName=firstName, lastName=lastName, emailAddress=emailAddress)
    newUser.setPassword(password)
    # temporary until we're in prod
    newUser.isAdmin = True
    newUser.save()
    flash("User Registered Sucessfully", 'success')
    return redirect(url_for('users.index'))


@blueprint.route('/login', methods=['POST', 'GET'])
@validate(LoginEmail="str", LoginPassword="str")
def login(loginEmail=None, loginPassword=None):
    """Presents and process the login form"""
    if request.method == 'GET':
        return render_template('main/login.html')
    loginUser = User.select().where(User.emailAddress == loginEmail).count()
    if loginUser > 0:
        loginUser = User.select().where(User.emailAddress == loginEmail).get()
        if loginUser.checkPassword(loginPassword):
            loginUser.lastLogin = datetime.now()
            loginUser.save()
            g.loggedIn = True
            session["user"] = loginUser.id
        else:
            flash("Invalid Email Address Or Password", "error")
    else:
        flash("Invalid Email Address Or Password", "error")
    return redirect(url_for('main.index'))


@blueprint.route('/logout', methods=['POST'])
def logout():
    """Logs a user off"""
    session.pop("user", None)
    flash("Logged Out!", "success")
    return redirect(request.referrer)

@blueprint.route('/admin/restore')
def deletedItems():
    """Displays the recyclbin of all deleted items"""
    if not g.User.isAdmin:
        flash("You are not allow to access that", "error")
        return redirect(url_for('main.index'))
    items = DeletedItem.getAll()
    return render_template('admin/restore.html', items=items)
