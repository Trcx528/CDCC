from flask import Blueprint, render_template, g, flash, redirect, url_for
from app.validation import validate
from app.models import Caterer, Dishes

blueprint = Blueprint('caterers', __name__)

@blueprint.before_request
def adminCheck():
    if not g.User.isAdmin:
        flash("You are not allow to access that", "error")
        return redirect(url_for('main.index'))



@blueprint.route('/admin/caterers')
def index():
    return render_template('admin/caterers/index.html')


@blueprint.route('/admin/caterers/create')
def create():
    return render_template('admin/caterers/create.html')


@blueprint.route('/admin/caterers/create', methods=['POST'])
@validate()
def processCreate():
    return redirect(url_for('caterers.index'))


@blueprint.route('/admin/caterers/<int:id>')
def edit(id):
    return render_template('admin/caterers/edit.html')


@blueprint.route('/admin/caterers/<int:id>', methods=['POST'])
@validate()
def processEdit(id):
    return redirect(url_for('caterers.index'))


@blueprint.route('/admin/caterers/<int:id>/delete', methods=['POST'])
def delete(id):
    return redirect(url_for('caterers.index'))
