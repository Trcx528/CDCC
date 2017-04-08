from flask import Blueprint, render_template, g, flash, redirect, url_for, request
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
        roomjson[room.id] = {'capacity': room.capacity, 'rate': float(room.price),
                             'adjacentRooms': room.adjacentRoomIds(), 'name': room.name, 'id': room.id}
    return render_template('bookings/edit.html', booking=booking, dishes=dishes, orgs=orgs, contacts=cons,
                           contactjson=contactjson, rooms=rooms, roomjson=roomjson)


@blueprint.route('/bookings/<int:id>', methods=['POST'])
@validate(EventName='str|required', DiscountPercent='percent|required|max=100|min=0', Rooms='multiselect',
          DiscountAmount='currency|required|min=0', Contact='int|required')
def processEdit(id, eventName, discountPercent, discountAmount, contact, rooms):
    b = Booking.select().where(Booking.id == id).get()
    food = {}
    for field in request.form:
        if field.startswith('dish_'):
            food[int(field.replace('dish_', ''))] = int(request.form[field])
    b.eventName = eventName
    b.discountPercent = discountPercent
    b.discountAmount = discountAmount
    b.contact_id = contact
    rooms = Room.select().where(Room.id << rooms).execute()
    if Room.areRoomsFree(rooms, b.startTime, b.endTime):
        BookingRoom.delete().where(BookingRoom.booking == b).execute()
        for room in rooms:
            br = BookingRoom(booking=b, room=room)
            br.save()
        Order.delete().where(Order.booking == b).execute()
        for f in food:
            if food[f] > 0:
                Order(dish=Dish.get(Dish.id == int(f)), booking=b, quantity=food[f]).save()
        b.calculateTotal()
        b.save()
    else:
        flash('A room that you selected is no longer available.  Please select a new room.', 'error')
        return redirect(request.referrer)
    flash('Booking Updated', 'success')
    return redirect(url_for('bookings.index'))


@blueprint.route('/bookings/<int:id>/delete', methods=['POST'])
def delete(id):
    return redirect(url_for('bookings.index'))
