""" This file contains the CRUD for caterers and their dishes"""

from flask import Blueprint, render_template, flash, redirect, url_for
from app.validation import validate
from app.models import Caterer, Dish
from peewee import prefetch

blueprint = Blueprint('caterers', __name__)

@blueprint.route('/admin/caterers')
def index():
    """List all caterers and their dishes"""
    caterer = Caterer.select().where(Caterer.isDeleted == False)
    dishes = Dish.select().where(Dish.isDeleted == False)
    caterers = prefetch(caterer, dishes)
    return render_template('admin/caterers/index.html', caterers=caterers)


@blueprint.route('/admin/caterers/create')
def create():
    """View to create a new caterer"""
    return render_template('admin/caterers/create.html')


@blueprint.route('/admin/caterers/create', methods=['POST'])
@validate(Name="str|required", Phone="phone|required")
def processCreate(name, phone):
    """Create a caterer with the POST data"""
    Caterer(name=name, phone=phone).save()
    flash("Created %s" % name, "success")
    return redirect(url_for('caterers.index'))


@blueprint.route('/admin/caterers/<int:id>')
def edit(id):
    """View to show the caterer data"""
    caterer = Caterer.select().where(Caterer.id == id).get()
    return render_template('admin/caterers/edit.html', caterer=caterer)


@blueprint.route('/admin/caterers/<int:id>', methods=['POST'])
@validate(Name="str|required", Phone="phone|required")
def processEdit(id, name, phone):
    """Update a caterer based on POST data"""
    Caterer.update(name=name, phone=phone).where(Caterer.id == id).execute()
    flash("Updated %s" % name, 'success')
    return redirect(url_for('caterers.index'))


@blueprint.route('/admin/caterers/<int:id>/delete', methods=['POST'])
def delete(id):
    """Soft delete a caterer"""
    Caterer.update(isDeleted=True).where(Caterer.id == id).execute()
    flash('Caterer Deleted', 'success')
    return redirect(url_for('caterers.index'))


@blueprint.route('/admin/caterers/<int:id>/restore', methods=['POST'])
def restore(id):
    """Restores a softdeleted caterer"""
    Caterer.update(isDeleted=False).where(Caterer.id == id).execute()
    flash('Caterer Restored', 'success')
    return redirect(url_for('caterers.edit', id=id))
