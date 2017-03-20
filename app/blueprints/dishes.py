from flask import Blueprint, render_template, g, flash, redirect, url_for
from app.validation import validate
from app.models import Caterer, Dishes

blueprint = Blueprint('dishes', __name__)

@blueprint.before_request
def adminCheck():
    if not g.User.isAdmin:
        flash("You are not allow to access that", "error")
        return redirect(url_for('main.index'))



@blueprint.route('/admin/dishes')
def index():
    return render_template('admin/dishes/index.html')


@blueprint.route('/admin/dishes/create')
def create():
    return render_template('admin/dishes/create.html')


@blueprint.route('/admin/dishes/create', methods=['POST'])
@validate()
def processCreate():
    return redirect(url_for('dishes.index'))


@blueprint.route('/admin/dishes/<int:id>')
def edit(id):
    return render_template('admin/dishes/edit.html')


@blueprint.route('/admin/dishes/<int:id>', methods=['POST'])
@validate()
def processEdit(id):
    return redirect(url_for('dishes.index'))


@blueprint.route('/admin/dishes/<int:id>/delete', methods=['POST'])
def delete(id):
    return redirect(url_for('dishes.index'))
