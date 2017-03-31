from flask import Blueprint, render_template, g, flash, redirect, url_for
from app.validation import validate
from app.models import Booking, BookingRoom, Room
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
    return render_template('bookings/edit.html')


@blueprint.route('/bookings/<int:id>', methods=['POST'])
def processEdit(id):
    return redirect(url_for('bookings.index'))


@blueprint.route('/bookings/<int:id>/delete', methods=['POST'])
def delete(id):
    return redirect(url_for('bookings.index'))
