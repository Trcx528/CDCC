from flask import Blueprint, render_template, g, flash, redirect, url_for
from app.validation import validate
from app.models import Caterer, Dish

blueprint = Blueprint('dishes', __name__)

@blueprint.before_request
def adminCheck():
    if not g.User.isAdmin:
        flash("You are not allow to access that", "error")
        return redirect(url_for('main.index'))



@blueprint.route('/admin/dishes/create')
def create():
    return render_template('admin/dishes/create.html',
                           caterers=Caterer.select().where(Caterer.isDeleted == False))


@blueprint.route('/admin/dishes/create', methods=['POST'])
@validate(Name="str|required", Price="currency|required", Caterer="int|required")
def processCreate(name, price, caterer):
    Dish(name=name, price=price, caterer_id=caterer).save()
    flash("Created new dish %s" % name, 'success')
    return redirect(url_for('caterers.index'))


@blueprint.route('/admin/dishes/<int:id>')
def edit(id):
    dish = Dish.select().where(Dish.id == id).get()
    return render_template('admin/dishes/edit.html', dish=dish,
                           caterers=Caterer.select().where((Caterer.isDeleted == False) |
                                                           (Caterer.id == dish.caterer_id)))


@blueprint.route('/admin/dishes/<int:id>', methods=['POST'])
@validate(Name="str|required", Price="currency|required", Caterer="int|required")
def processEdit(id, name, price, caterer):
    Dish.update(name=name, price=price,
                caterer=Caterer.select().where(Caterer.id == caterer).get()).where(Dish.id == id).execute()
    flash("Dish updated", 'success')
    return redirect(url_for('caterers.index'))


@blueprint.route('/admin/dishes/<int:id>/delete', methods=['POST'])
def delete(id):
    Dish.update(isDeleted=True).where(Dish.id == id).execute()
    flash('Dish deleted', 'success')
    return redirect(url_for('caterers.index'))


@blueprint.route('/admin/dishes/<int:id>/restore', methods=['POST'])
def restore(id):
    Dish.update(isDeleted=False).where(Dish.id == id).execute()
    flash('Dish restored', 'success')
    return redirect(url_for('dishes.edit', id=id))
