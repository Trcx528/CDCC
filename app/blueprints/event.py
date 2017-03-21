from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, g, flash, redirect, url_for, session
from app.validation import validate, datetimeFormat
from app.models import *

blueprint = Blueprint('event', __name__)


@blueprint.route('/event/plan')
def plan():
    start = datetime.fromordinal(date.today().toordinal()) + timedelta(days=1, hours=8)
    finish = datetime.fromordinal(date.today().toordinal()) + timedelta(days=1, hours=22)
    return render_template('event/search.html', capacity=25, start=start.strftime(datetimeFormat),
                           finish=finish.strftime(datetimeFormat), duration="4")

@blueprint.route('/event/plan', methods=['POST'])
@validate(Capacity="int|required", Start="date|required|before=Finish", Finish="date|required", Duration="int|required")
def processPlan(capacity, start, finish, duration):
    session['Capacity'] = capacity
    session['Start'] = start
    session['Finish'] = finish
    session['Duration'] = duration
    return redirect(url_for('event.selectRoom', capacity=capacity))

@blueprint.route('/event/room')
def selectRoom():
    return render_template('event/room.html')
