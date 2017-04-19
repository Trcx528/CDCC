from datetime import datetime, timedelta, date
from flask import Blueprint, render_template, flash, redirect, url_for, request, g
from app.validation import validate
from app.models import Booking, BookingRoom, Room, Order, Dish, Caterer, Contact, Organization, User
from peewee import prefetch

blueprint = Blueprint('bookings', __name__)


@blueprint.route('/bookings')
@validate(Start='date', End='date', methods=['GET'], csrf_protection=False)
def index(start=None, end=None):
    if start is None:
        start = date.today()
    if end is None:
        end = date.today() + timedelta(days=30)
    print(start, end, type(end))
    b = Booking.select().where((Booking.startTime > start) & (Booking.startTime < end) & (Booking.isCanceled == False))
    bookings = prefetch(b, BookingRoom, Room)
    return render_template('bookings/index.html', bookings=bookings, start=start, end=end)

@blueprint.route('/bookings/view/<int:id>')
def view(id):
    b = Booking.select().where(Booking.id == id)
    booking = prefetch(b, Order, Dish, Caterer, Contact, Organization, BookingRoom, Room, User)[0]
    return render_template('bookings/view.html', booking=booking)


@blueprint.route('/bookings/<int:id>')
def edit(id):
    b = Booking.select().where(Booking.id == id)
    booking = prefetch(b, Order, Dish, Caterer, Contact, Organization, BookingRoom, Room, User)[0]
    dishes = prefetch(Dish.select().where(Dish.isDeleted == False), Caterer.select().where(Caterer.isDeleted == False))
    orgs = Organization.select().where((Organization.isDeleted == False) |
                                       (Organization.id == booking.contact.organization_id))
    cons = Contact.select().where((Contact.isDeleted == False) | (Contact.id == booking.contact_id))
    print(booking.startTime, booking.endTime, type(booking.endTime))
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

@blueprint.route('/bookings/<int:id>/cancel')
def cancel(id):
    booking = Booking.select().where(Booking.id == id).get()
    return render_template('bookings/cancel.html', booking=booking)

@blueprint.route('/bookings/<int:id>/cancel', methods=['POST'])
@validate(Reason='str|required')
def processCancel(id, reason):
    Booking.update(isCanceled=True, canceler=g.User.id, cancelationReason=reason).where(Booking.id == id).execute()
    booking = Booking.select().where(Booking.id == id).get()
    BookingRoom.delete().where(BookingRoom.booking == booking).execute()
    flash('Booking Canceled', 'success')
    return redirect(url_for('bookings.index'))


@blueprint.route('/bookings/<int:id>/restore', methods=['POST'])
def restore(id):
    Booking.update(isCanceled=False).where(Booking.id == id).execute()
    flash('Booking Restored, please select valid rooms for this event.', 'success')
    return redirect(url_for('bookings.edit', id=id))


