from datetime import date, timedelta
from app.validation import validate
from flask import Blueprint, render_template
from app.models import Booking, BookingRoom, Room, Order, Dish, Caterer, Contact, Organization, User
from peewee import prefetch

blueprint = Blueprint('reports', __name__)


@blueprint.route('/reports/canceledEvents')
@validate(Start='date', End='date', methods=['GET'], csrf_protection=False)
def canceled(start=None, end=None):
    if start is None:
        start = date.today() - timedelta(days=30)
    if end is None:
        end = date.today()
    b = Booking.select().where((Booking.startTime > start) & (Booking.startTime < end) & (Booking.isCanceled == True))
    bookings = prefetch(b, BookingRoom, Room)
    return render_template('reports/canceled.html', bookings=bookings, start=start, end=end)


@blueprint.route('/reports/topOrganizations')
@validate(Start='date', End='date', methods=['GET'], csrf_protection=False)
def toporganizations(start=None, end=None):
    if start is None:
        start = date.today() - timedelta(days=30)
    if end is None:
        end = date.today()
    b = Booking.select().where((Booking.startTime > start) & (Booking.startTime < end) & (Booking.isCanceled == True))
    bookings = prefetch(b, BookingRoom, Room)
    return render_template('reports/toporganizations.html', bookings=bookings, start=start, end=end)


@blueprint.route('/reports/topContacts')
@validate(Start='date', End='date', methods=['GET'], csrf_protection=False)
def topcontacts(start=None, end=None):
    if start is None:
        start = date.today() - timedelta(days=30)
    if end is None:
        end = date.today()
    b = Booking.select().where((Booking.startTime > start) & (Booking.startTime < end) & (Booking.isCanceled == True))
    bookings = prefetch(b, BookingRoom, Room)
    return render_template('reports/topcontacts.html', bookings=bookings, start=start, end=end)
