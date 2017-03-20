from flask import Blueprint, render_template, g, flash, redirect, url_for
from app.validation import validate
from app.models import Room, Organization, Contact
from peewee import JOIN

blueprint = Blueprint('admin', __name__)

@blueprint.before_request
def adminCheck():
    if not g.User.isAdmin:
        flash("You are not allow to access that", "error")
        return redirect(url_for('main.index'))


@blueprint.route('/admin')
def index():
    return render_template('admin/index.html')

@blueprint.route('/admin/rooms/create')
def createRoom():
    rooms = {}
    for r in Room.select():
        rooms[r.id] = r.name
    return render_template('admin/room/create.html', rooms=rooms)

@blueprint.route('/admin/rooms/create', methods=['POST'])
@validate(Name="str|required", Capacity="int|required|min=1", Price="currency|required|min=0",
          AdjacentRooms="multiselect")
def processCreateRoom(name, capacity, price, adjacentRooms):
    newRoom = Room(name=name, capacity=capacity, price=price)
    newRoom.save()
    for id in adjacentRooms:
        newRoom.addAdjacentRoom(id)
    flash("Created room %s!" % name, "success")
    return redirect(url_for('admin.listRoom'))

@blueprint.route('/admin/rooms/<int:id>')
def editRoom(id):
    rooms = {}
    for r in Room.select().where(Room.id != id):
        rooms[r.id] = r.name
    return render_template('admin/room/edit.html', rooms=rooms, room=Room.select().where(Room.id == id).get())

@blueprint.route('/admin/rooms/<int:id>', methods=['POST'])
@validate(Name="str|required", Capacity="int|required|min=1", Price="currency|required|min=0",
          AdjacentRooms="multiselect")
def processEditRoom(id, name, capacity, price, adjacentRooms):
    room = Room.select().where(Room.id == id).get()
    room.name = name
    room.capacity = capacity
    room.price = price
    room.setAdjacentRooms(adjacentRooms)
    flash("Modified room %s" % name, "success")
    return redirect(url_for('admin.listRoom'))

@blueprint.route('/admin/rooms')
def listRoom():
    return render_template('admin/room/index.html', rooms=Room.select())


@blueprint.route('/admin/rooms/<int:id>/delete', methods=['POST'])
def deleteRoom(id):
    room = Room.select().where(Room.id == id).get()
    rooms = room.adjacentRooms()
    for r in rooms:
        r.removeAdjacentRoom(id)
    room.delete_instance()
    flash("Room %s deleted" % room.name, "success")
    return redirect(url_for('admin.listRoom'))

@blueprint.route('/admin/contacts')
def listContacts():
    return render_template('admin/contacts/index.html', organizations=Organization.select().join(Contact), contacts=Contact.select().where(Contact.organization == None))

@blueprint.route('/admin/organizations/create')
def createOrganization():
    return render_template('admin/organizations/create.html')
        