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
    booking = prefetch(b, Order, Dish, Caterer, Contact, Organization, BookingRoom, Room)
    dishes = prefetch(Dish.select(), Caterer)
    orgs = Organization.select()
    cons = Contact.select()
    json = {}
    for c in cons:
        oid = c.organization_id if c.organization_id is not None else 0
        if oid not in json:
            json[oid] = {}
        json[oid][c.id] = c.name
    openRooms = Room.findRooms(booking[0].startTime, booking[0].endTime, None, [booking[0].selectedRooms()])
    rooms = {}
    for rs in openRooms:
        val = []
        price = 0
        cap = 0
        for r in openRooms[rs]:
            cap += r.capacity
            price += r.price
            val.append(r.name)
        rooms[rs] = {'name': ", ".join(val), 'capacity': cap, 'rate': price}
        selectedRoomId = []
        for id in booking[0].selectedRoomIds():
            selectedRoomId.append(str(id))
        selectedRoomId = "_".join(selectedRoomId)
    return render_template('bookings/edit.html', booking=booking[0], dishes=dishes, orgs=orgs, contacts=cons,
                           json=json, rooms=rooms, selectedRoomId=selectedRoomId)


@blueprint.route('/bookings/<int:id>', methods=['POST'])
def processEdit(id):
    return redirect(url_for('bookings.index'))


@blueprint.route('/bookings/<int:id>/delete', methods=['POST'])
def delete(id):
    return redirect(url_for('bookings.index'))
