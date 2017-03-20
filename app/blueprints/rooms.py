from flask import Blueprint, render_template, g, flash, redirect, url_for
from app.validation import validate
from app.models import Room

blueprint = Blueprint('rooms', __name__)

@blueprint.before_request
def adminCheck():
    if not g.User.isAdmin:
        flash("You are not allow to access that", "error")
        return redirect(url_for('main.index'))


@blueprint.route('/admin/rooms/create')
def create():
    return render_template('admin/room/create.html', rooms=Room.select())

@blueprint.route('/admin/rooms/create', methods=['POST'])
@validate(Name="str|required", Capacity="int|required|min=1", Price="currency|required|min=0",
          AdjacentRooms="multiselect")
def processCreate(name, capacity, price, adjacentRooms):
    newRoom = Room(name=name, capacity=capacity, price=price)
    newRoom.save()
    for id in adjacentRooms:
        newRoom.addAdjacentRoom(id)
    flash("Created room %s!" % name, "success")
    return redirect(url_for('rooms.index'))

@blueprint.route('/admin/rooms/<int:id>')
def edit(id):
    return render_template('admin/room/edit.html', rooms=Room.select().where(Room.id != id),
                           room=Room.select().where(Room.id == id).get())

@blueprint.route('/admin/rooms/<int:id>', methods=['POST'])
@validate(Name="str|required", Capacity="int|required|min=1", Price="currency|required|min=0",
          AdjacentRooms="multiselect")
def processEdit(id, name, capacity, price, adjacentRooms):
    room = Room.select().where(Room.id == id).get()
    room.name = name
    room.capacity = capacity
    room.price = price
    room.setAdjacentRooms(adjacentRooms)
    flash("Modified room %s" % name, "success")
    return redirect(url_for('rooms.index'))

@blueprint.route('/admin/rooms')
def index():
    return render_template('admin/room/index.html', rooms=Room.select())


@blueprint.route('/admin/rooms/<int:id>/delete', methods=['POST'])
def delete(id):
    room = Room.select().where(Room.id == id).get()
    rooms = room.adjacentRooms()
    for r in rooms:
        r.removeAdjacentRoom(id)
    room.delete_instance()
    flash("Room %s deleted" % room.name, "success")
    return redirect(url_for('rooms.index'))

