""" This file contains the CRUD for Rooms """

from flask import Blueprint, render_template, flash, redirect, url_for
from app.validation import validate
from app.models import Room

blueprint = Blueprint('rooms', __name__)


@blueprint.route('/admin/rooms/create')
def create():
    """Gather information for a new room"""
    return render_template('admin/room/create.html',
                           rooms=Room.select().where(Room.isDeleted == False).order_by(Room.name))


@blueprint.route('/admin/rooms/create', methods=['POST'])
@validate(Name="str|required", Capacity="int|required|min=1", Rate="currency|required|min=0",
          AdjacentRooms="multiselect", Dimensions="dimensions|required")
def processCreate(name, capacity, rate, adjacentRooms, dimensions):
    """Create a new room based on POST data"""
    newRoom = Room(name=name, capacity=capacity, price=rate, dimensions=dimensions)
    newRoom.save()
    for id in adjacentRooms:
        newRoom.addAdjacentRoom(id)
    flash("Created room %s!" % name, "success")
    return redirect(url_for('rooms.index'))

@blueprint.route('/admin/rooms/<int:id>')
def edit(id):
    """Display a room details"""
    return render_template('admin/room/edit.html', room=Room.select().where(Room.id == id).get(),
                           rooms=Room.select().where(Room.id != id, Room.isDeleted == False).order_by(Room.name))


@blueprint.route('/admin/rooms/<int:id>', methods=['POST'])
@validate(Name="str|required", Capacity="int|required|min=1", Rate="currency|required|min=0",
          AdjacentRooms="multiselect", Dimensions="dimensions|required")
def processEdit(id, name, capacity, rate, adjacentRooms, dimensions):
    """Updates a room details"""
    room = Room.select().where(Room.id == id).get()
    room.name = name
    room.capacity = capacity
    room.price = rate
    room.dimensions = dimensions
    room.setAdjacentRooms(adjacentRooms)
    room.save()
    flash("Modified room %s" % name, "success")
    return redirect(url_for('rooms.index'))


@blueprint.route('/admin/rooms')
def index():
    """List all rooms"""
    return render_template('admin/room/index.html',
                           rooms=Room.select().where(Room.isDeleted == False).order_by(Room.name))


@blueprint.route('/admin/rooms/<int:id>/delete', methods=['POST'])
def delete(id):
    """soft delete a room"""
    room = Room.select().where(Room.id == id).get()
    rooms = room.adjacentRooms()
    for r in rooms:
        r.removeAdjacentRoom(id)
    Room.update(isDeleted=True).where(Room.id == id).execute()
    flash("Room %s deleted" % room.name, "success")
    return redirect(url_for('rooms.index'))


@blueprint.route('/admin/rooms/<int:id>/restore', methods=['POST'])
def restore(id):
    """Restore a soft deleted room"""
    room = Room.select().where(Room.id == id).get()
    room.isDeleted = False
    room.save()
    flash('Room %s restored' % room.name, "success")
    return redirect(url_for('rooms.edit', id=id))
