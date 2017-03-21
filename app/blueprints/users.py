from flask import Blueprint, render_template, g, flash, redirect, url_for, request
from app.validation import validate
from app.models import User

blueprint = Blueprint('users', __name__)


@blueprint.route('/admin/users')
def index():
    if g.User.isAdmin:
        return render_template('admin/users/index.html', users=User.select())
    else:
        flash("You don't have access to that", 'error')
        return redirect(request.referrer)


@blueprint.route('/user/<int:id>')
def edit(id):
    user = User.select().where(User.id == id).get()
    return render_template('admin/users/edit.html', user=user)


@blueprint.route('/user/<int:id>', methods=['POST'])
@validate(FirstName="str|required", LastName="str|required", NewPassword="str",
          ConfirmPassword="str|matches=NewPassword", EmailAddress="userEmail|required|userid=<id>",
          Password="userPassword|required|userid=<id>|admin", Admin="check")
def processEdit(id, firstname, lastname, emailAddress, newPassword, admin):
    user = User.select().where(User.id == id).get()
    if newPassword is not None and newPassword is not "":
        user.setPassword(newPassword)
    user.firstName = firstname
    user.lastName = lastname
    user.emailAddress = emailAddress
    if g.User.isAdmin:
        user.isAdmin = admin
    user.save()
    flash("User updated", 'success')
    if g.User.isAdmin:
        return redirect(url_for('users.index'))
    return redirect(url_for('main.index'))


@blueprint.route('/admin/users/<int:id>/delete', methods=['POST'])
def delete(id):
    if g.User.isAdmin:
        User.delete().where(User.id == id).execute()
        flash("User deleted", 'success')
        return redirect(url_for('users.index'))
    else:
        flash("You don't have access to that", 'error')
        return redirect(request.referrer)
    