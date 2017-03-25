from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, redirect, url_for, session
from app.validation import validate, datetimeFormat
from app.models import *
from peewee import JOIN

blueprint = Blueprint('event', __name__)

class TenativeBooking():
    start = None
    finish = None
    capacity = None
    roomIds = None

    @classmethod
    def loadFromSession(cls, prefix=""):
        s = cls()
        today = datetime.fromordinal(date.today().toordinal())
        s.start = session[prefix + 'start'] if prefix + 'start' in session else today + timedelta(days=1, hours=8)
        s.finish = session[prefix + 'finish'] if prefix + 'finish' in session else today + timedelta(days=1, hours=12)
        s.capacity = session[prefix + 'capacity'] if prefix + 'capacity' in session else 25
        return s

    @classmethod
    def saveToSession(cls, prefix="", **kwargs):
        for k in kwargs:
            session[prefix + k] = kwargs[k]


@blueprint.route('/book/search')
def plan():
    t = TenativeBooking.loadFromSession()
    return render_template('event/search.html', capacity=t.capacity, start=t.start.strftime(datetimeFormat),
                           finish=t.finish.strftime(datetimeFormat))

@blueprint.route('/book/search', methods=['POST'])
@validate(Capacity="int|required", Start="datetime|required|before=Finish", Finish="datetime|required")
def processPlan(capacity, start, finish):
    TenativeBooking.saveToSession(capacity=capacity, start=start, finish=finish)
    return redirect(url_for('event.selectRoom'))


@blueprint.route('/book/room')
def selectRoom():
    #busyRooms = Booking.select().where((Booking.startTime >= start) & (Booking.endTime <= finish)).alias('bk')
    #rooms = Room.select().join(busyRooms, JOIN.LEFT_OUTER, on=(Room.id == ))
    # TODO Make logic to not show already booked rooms
    t = TenativeBooking.loadFromSession()
    rooms = []
    for room in Room.select():
        rooms.append({'ids': [room.id], 'total': room.price, 'capacity': room.capacity, 'name': room.name,
                      'optionId': len(rooms) + 1})

    # finalize
    return render_template('event/room.html', rooms=rooms, start=t.start, finish=t.finish, capacity=t.capacity)


@blueprint.route('/book/room', methods=['POST'])
@validate(roomIds='list|required|type=int')
def processSelectRoom(roomIds):
    TenativeBooking.saveToSession(roomIds=roomIds)
    return redirect(url_for('event.selectFood'))


@blueprint.route('/book/caterers')
def selectFood():
    dishes = Dish.select().join(Caterer)
    return render_template('event/caterer.html', dishes=dishes)
