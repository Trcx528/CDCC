from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, g, flash, redirect, url_for, session
from app.validation import validate, datetimeFormat
from app.models import *
from peewee import JOIN

blueprint = Blueprint('event', __name__)


@blueprint.route('/event/plan')
def plan():
    start = datetime.fromordinal(date.today().toordinal()) + timedelta(days=1, hours=8)
    finish = datetime.fromordinal(date.today().toordinal()) + timedelta(days=1, hours=22)
    return render_template('event/search.html', capacity=25, start=start.strftime(datetimeFormat),
                           finish=finish.strftime(datetimeFormat))

@blueprint.route('/event/plan', methods=['POST'])
@validate(Capacity="int|required", Start="datetime|required|before=Finish", Finish="datetime|required")
def processPlan(capacity, start, finish):
    session['Capacity'] = capacity
    session['Start'] = start
    session['Finish'] = finish
    return redirect(url_for('event.selectRoom'))


@blueprint.route('/event/room')
def selectRoom():
    start = session.pop('Start', datetime.fromordinal(date.today().toordinal()) + timedelta(days=1, hours=8))
    finish = session.pop('Finish', datetime.fromordinal(date.today().toordinal()) + timedelta(days=1, hours=22))
    capacity = session.pop('Capacity', 25)
    #busyRooms = Booking.select().where((Booking.startTime >= start) & (Booking.endTime <= finish)).alias('bk')
    #rooms = Room.select().join(busyRooms, JOIN.LEFT_OUTER, on=(Room.id == ))
    # TODO Make logic to not show already booked rooms
    rooms = {}
    i = 0
    for room in Room.select():
        i = i + 1
        rooms[i] = {'rooms': [room], 'total': room.price}

    # finalize
    return render_template('event/room.html', rooms=ret)
