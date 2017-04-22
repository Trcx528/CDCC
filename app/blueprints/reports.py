from datetime import date, timedelta
from app.validation import validate
from flask import Blueprint, render_template
from app.models import Booking, BookingRoom, Room, Order, Dish, Caterer, Contact, Organization, User
from peewee import prefetch, fn, JOIN

blueprint = Blueprint('reports', __name__)


@blueprint.route('/reports')
def index():
    return render_template('reports/index.html')

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
    results = (Organization
               .select(Organization,
                       fn.Sum(Booking.finalPrice).alias('TotalSpend'),
                       fn.Sum(Booking.catereringTotal).alias('TotalCaterering'),
                       fn.Sum(Booking.roomTotal).alias('TotalRooms'),
                       fn.Sum(Booking.discountTotal).alias('TotalDiscounts'))
               .join(Contact, on=Contact.organization_id == Organization.id, join_type=JOIN.LEFT_OUTER)
               .join(Booking, on=Booking.contact_id == Contact.id, join_type=JOIN.LEFT_OUTER)
               .where((Booking.startTime >= start) & (Booking.startTime <= end))
               .group_by(Organization)
               .order_by(fn.Sum(Booking.finalPrice).desc())
               .limit(10))
    return render_template('reports/toporganizations.html', start=start, end=end, orgs=results)


@blueprint.route('/reports/topContacts')
@validate(Start='date', End='date', methods=['GET'], csrf_protection=False)
def topcontacts(start=None, end=None):
    if start is None:
        start = date.today() - timedelta(days=30)
    if end is None:
        end = date.today()
    results = (Contact
               .select(Contact,
                       fn.Sum(Booking.finalPrice).alias('TotalSpend'),
                       fn.Sum(Booking.catereringTotal).alias('TotalCaterering'),
                       fn.Sum(Booking.roomTotal).alias('TotalRooms'),
                       fn.Sum(Booking.discountTotal).alias('TotalDiscounts'))
               .join(Booking, on=Booking.contact_id == Contact.id, join_type=JOIN.LEFT_OUTER)
               .where((Booking.startTime >= start) & (Booking.startTime <= end))
               .group_by(Contact)
               .order_by(fn.Sum(Booking.finalPrice).desc())
               .limit(10))
    return render_template('reports/topcontacts.html', contacts=results, start=start, end=end)
