from flask import Blueprint, render_template, g, flash, redirect, url_for
from app.validation import validate
from app.models import Room

blueprint = Blueprint('admin', __name__)

@blueprint.before_request
def adminCheck():
    if not g.User.isAdmin:
        flash("You are not allow to access that", "error")
        return redirect(url_for('main.index'))


@blueprint.route('/admin')
def index():
    return render_template('admin/index.html')


@blueprint.route('/admin/room/create')
def createRoom():
    rooms = {}
    for r in Room.select():
        rooms[r.id] = r.name
    return render_template('admin/room/create.html', rooms=rooms)


@blueprint.route('/admin/room/create', methods=['POST'])
@validate(Name="str|required", Capacity="int|required|min=1", Price="currency|required|min=0")
def processCreateRoom(name, capacity, price):
    newRoom = Room(name=name, capacity=capacity, price=price)
    newRoom.save()
    flash("Created room %s!" % name, "success")
    return redirect(url_for('admin.listRoom'))


@blueprint.route('/admin/room')
def listRoom():
    return render_template('admin/room/index.html', rooms=Room.select())
