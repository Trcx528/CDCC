from flask import Blueprint, render_template, request, g, flash, redirect, url_for, session
from app.validation import validate
from app.models import User

blueprint = Blueprint('main', __name__)


@blueprint.route('/')
def index():
    return render_template('main/index.html')


@blueprint.route('/register')
def register():
    return render_template('main/form.html')


@blueprint.route('/register', methods=['POST'])
@validate(FirstName="str|required", LastName="str|required", EmailAddress="email|required|dbunique",
          Password="str|required|minlength=8", ConfirmPassword="str|required|matches=Password")
def processRegister():
    newUser = User(FirstName=g.data["FirstName"], LastName=g.data["LastName"], EmailAddress=g.data["EmailAddress"])
    newUser.setPassword(g.data["Password"])
    newUser.save()
    flash("User Registered Sucessfully", 'success')
    return redirect(url_for('main.index'))


@blueprint.route('/login', methods=['POST'])
# just validate that they are both there, we'll check the rest in our below function
@validate(LoginEmail="str|required", LoginPassword="str|required")
def login():
    loginUser = User.select().where(User.EmailAddress == g.data["LoginEmail"]).get()
    if loginUser:
        if loginUser.checkPassword(g.data["LoginPassword"]):
            g.loggedIn = True
            session["user"] = loginUser.id
            flash("Logged In Successfully", "success")
        else:
            flash("Invalid Email Address Or Password", "error")
    else:
        flash("Invalid Email Address Or Password", "error")
    return redirect(request.referrer)


@blueprint.route('/logout', methods=['POST'])
def logout():
    session.pop("user", None)
    flash("Logged Out!", "success")
    return redirect(request.referrer)
