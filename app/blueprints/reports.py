""" This file contains the logic used to generate each report """

import app.helpers as helpers
from datetime import date, timedelta
from flask import Blueprint, render_template, make_response
from peewee import prefetch, fn, JOIN
from app.validation import validate
from app.models import Booking, BookingRoom, Room, Contact, Organization

blueprint = Blueprint('reports', __name__)

def csvFormat(value):
    """If a value contains a comma then it needs to be encapulated in quotes otherwise excel won't like it"""
    if ',' in value:
        return '"%s"' % value
    return value

@blueprint.route('/reports')
def index():
    return render_template('reports/index.html')

def canceledData(start, end):
    b = Booking.select().where((Booking.startTime > start) & (Booking.startTime < end) & (Booking.isCanceled == True))
    return prefetch(b, BookingRoom, Room)

@blueprint.route('/reports/canceledEvents')
@validate(Start='date', End='date', methods=['GET'], csrf_protection=False)
def canceled(start=None, end=None):
    """Displays the canceled event report"""
    if start is None:
        start = date.today() - timedelta(days=30)
    if end is None:
        end = date.today()
    bookings = canceledData(start, end)
    return render_template('reports/canceled.html', bookings=bookings, start=start, end=end)


@blueprint.route('/reports/canceledEventsCsv')
@validate(Start='date', End='date', methods=['GET'], csrf_protection=False)
def canceledCsv(start=None, end=None):
    """Presents the canceled event report as a CSV"""
    print(start, end)
    if start is None:
        start = date.today() - timedelta(days=30)
    if end is None:
        end = date.today()
    bookings = canceledData(start, end)
    csv = "Event Name,Start Time,End Time,Rooms,Total,Cancelation Reason\r\n"
    for booking in bookings:
        csv += "%s,%s,%s,%s,%s,%s\r\n" % (csvFormat(booking.eventName),
                                          csvFormat(helpers.format_datetime(booking.startTime)),
                                          csvFormat(helpers.format_datetime(booking.endTime)),
                                          csvFormat(booking.roomCombo.name),
                                          csvFormat(helpers.format_currency(booking.finalPrice)),
                                          csvFormat(booking.cancelationReason))
    res = make_response(csv)
    res.headers["Content-Disposition"] = "attachment; filename=Canceled.csv"
    res.mimetype = "text/csv"
    return res


def topOrgData(start, end):
    return (Organization
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

@blueprint.route('/reports/topOrganizations')
@validate(Start='date', End='date', methods=['GET'], csrf_protection=False)
def toporganizations(start=None, end=None):
    """Displays the top organizations by spending report"""
    if start is None:
        start = date.today() - timedelta(days=30)
    if end is None:
        end = date.today()
    return render_template('reports/toporganizations.html', start=start, end=end, orgs=topOrgData(start, end))

@blueprint.route('/reports/topOrganizationsCsv')
@validate(Start='date', End='date', methods=['GET'], csrf_protection=False)
def toporganizationsCsv(start=None, end=None):
    """Displays the top organizations by spending report"""
    if start is None:
        start = date.today() - timedelta(days=30)
    if end is None:
        end = date.today()
    orgs = topOrgData(start, end)
    csv = "Organization,Caterering Total,Room Total,Discount Total,Discount Percent,Grand Total\r\n"
    for org in orgs:
        csv += "%s,%s,%s,%s,%s,%s\r\n" % (csvFormat(org.name),
                                          csvFormat(helpers.format_currency(org.TotalCaterering)),
                                          csvFormat(helpers.format_currency(org.TotalRooms)),
                                          csvFormat(helpers.format_currency(org.TotalDiscounts)),
                                          csvFormat(str(round(org.TotalDiscounts * 100/org.TotalSpend, 2)) + "%"),
                                          csvFormat(helpers.format_currency(org.TotalSpend)))
    res = make_response(csv)
    res.headers["Content-Disposition"] = "attachment; filename=TopOrgs.csv"
    res.mimetype = "text/csv"
    return res

def topContactsData(start, end):
    return (Contact
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


@blueprint.route('/reports/topContacts')
@validate(Start='date', End='date', methods=['GET'], csrf_protection=False)
def topcontacts(start=None, end=None):
    """Displays the top contacts by spending report"""
    if start is None:
        start = date.today() - timedelta(days=30)
    if end is None:
        end = date.today()
    return render_template('reports/topcontacts.html', contacts=topContactsData(start, end), start=start, end=end)


@blueprint.route('/reports/topContactsCsv')
@validate(Start='date', End='date', methods=['GET'], csrf_protection=False)
def topcontactsCsv(start=None, end=None):
    """Presents the top contacts by spending in a CSV"""
    if start is None:
        start = date.today() - timedelta(days=30)
    if end is None:
        end = date.today()
    csv = 'Contact,Caterering Total,Room Total,Discount Total,Discount Percentage,GrandTotal\r\n'
    for contact in topContactsData(start, end):
        csv += '%s,%s,%s,%s,%s,%s\r\n' % (csvFormat(contact.name),
                                          csvFormat(helpers.format_currency(contact.TotalCaterering)),
                                          csvFormat(helpers.format_currency(contact.TotalRooms)),
                                          csvFormat(helpers.format_currency(contact.TotalDiscounts)),
                                          csvFormat(str(round(contact.TotalDiscounts * 100/contact.TotalSpend, 2)) + "%"),
                                          csvFormat(helpers.format_currency(contact.TotalSpend)))
    res = make_response(csv)
    res.headers["Content-Disposition"] = "attachment; filename=TopOrgs.csv"
    res.mimetype = "text/csv"
    return res

