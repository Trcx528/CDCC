from flask import Blueprint, render_template, g, flash, redirect, url_for
from app.validation import validate
from app.models import Booking, BookingRoom, Room, Order, Dish, Caterer, Contact, Organization
from peewee import prefetch

blueprint = Blueprint('bookings', __name__)
# TODO add parameters to limit date/time range
@blueprint.route('/bookings')
def index():
    b = Booking.select().where(Booking.isCanceled == False)
    bookings = prefetch(b, BookingRoom, Room)
    return render_template('bookings/index.html', bookings=bookings)


@blueprint.route('/bookings/<int:id>')
def edit(id):
    b = Booking.select().where(Booking.id == id)
    booking = prefetch(b, Order, Dish, Caterer, Contact, Organization, BookingRoom, Room)[0]
    dishes = prefetch(Dish.select(), Caterer)
    orgs = Organization.select()
    cons = Contact.select()
    rooms = Room.openRooms(booking.startTime, booking.endTime, booking.id).execute()
    contactjson = {}
    for c in cons:
        oid = c.organization_id if c.organization_id is not None else 0
        if oid not in contactjson:
            contactjson[oid] = {}
        contactjson[oid][c.id] = c.name
    roomjson = {}
    for room in rooms:
        roomjson[room.id] = {'capacity': room.capacity, 'rate': float(room.price), 'adjacentRooms': room.adjacentRoomIds(), 'name': room.name}
    return render_template('bookings/edit.html', booking=booking, dishes=dishes, orgs=orgs, contacts=cons,
                           contactjson=contactjson, rooms=rooms, roomjson=roomjson)


@blueprint.route('/bookings/<int:id>', methods=['POST'])
def processEdit(id):
    return redirect(url_for('bookings.index'))


@blueprint.route('/bookings/<int:id>/delete', methods=['POST'])
def delete(id):
    return redirect(url_for('bookings.index'))
