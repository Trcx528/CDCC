from flask import Blueprint, render_template, redirect, url_for, session, request, g, flash
from app.validation import validate, datetimeFormat
from peewee import prefetch
from app.models import *
from app.logic import TenativeBooking, RoomCombo

blueprint = Blueprint('event', __name__)

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
    t = TenativeBooking.loadFromSession()
    openRooms = Room.openRooms(t.start, t.finish)
    rooms = RoomCombo.getCombos(openRooms, t.duration(), t.capacity)
    rooms.sort(key=RoomCombo.rateSort)
    return render_template('event/room.html', rooms=rooms[:10], booking=t,
                           comboId=t.roomCombo().id if len(t.roomIds) > 0 else None)

@blueprint.route('/book/room', methods=['POST'])
@validate(roomIds='list|required|type=int')
def processSelectRoom(roomIds):
    TenativeBooking.saveToSession(roomIds=roomIds)
    return redirect(url_for('event.selectFood'))


@blueprint.route('/book/caterers')
def selectFood():
    t = TenativeBooking.loadFromSession()
    d = Dish.select()
    c = Caterer.select()
    dishes = prefetch(d, c)
    return render_template('event/caterer.html', dishes=dishes, booking=t)


@blueprint.route('/book/caterers', methods=['POST'])
@validate() # check the csrf token
def processFoodSelection():
    food = {}
    for field in request.form:
        if field.startswith('dish_'):
            food[int(field.replace('dish_', ''))] = int(request.form[field])
    TenativeBooking.saveToSession(food=food)
    return redirect(url_for('event.finalizeBooking'))


@blueprint.route('/book/finalize')
def finalizeBooking():
    orgs = Organization.select().where(Organization.isDeleted == False)
    contacts = Contact.select().where(Contact.isDeleted == False)
    t = TenativeBooking.loadFromSession()
    json = {}
    for c in contacts:
        oid = c.organization_id if c.organization_id is not None else 0
        if oid not in json:
            json[oid] = {}
        json[oid][c.id] = c.name
    existing = True if 'existing' in g.data and g.data['existing'] != '' else False
    newContact = True if 'newContact' in g.data and g.data['newContact'] != '' else False
    newOrg = True if 'newOrg' in g.data and g.data['newOrg'] != '' else False
    if not existing and not newContact and not newOrg:
        existing = True
    return render_template('event/finalize.html', orgs=orgs, contacts=contacts, booking=t, json=json,
                           existing=existing, newContact=newContact, newOrg=newOrg)


@blueprint.route('/book/finalize', methods=['POST'])
@validate(EventName="str|required", DiscountPercent="percent|required|max=100|min=0",
          DiscountAmount="currency|required|min=0", existing="str", newContact="str", newOrg="str",
          Organization="int", Contact="int", ContactName="str", Email="email", CellPhone="phone",
          WorkPhone="phone", OrganizationName="str", OrganizationAddress="str")
def processFinalizeBooking(eventName, discountPercent, discountAmount, organization, contact, contactName, email,
                           cellPhone, workPhone, organizationName, organizationAddress, existing, newContact, newOrg):
    TenativeBooking.saveToSession(name=eventName, discountPercent=discountPercent, discountAmount=discountAmount)
    errors = {}
    if existing != "":
        if Organization is None:
            errors['Organization'] = ["Required"]
        if Contact is None:
            errors["Contact"] = ["Required"]
    elif newContact != "" or newOrg != "":
        if Organization is None and newContact is not None:
            errors['Organization'] = ['Required']
        if contactName is None or contactName == "":
            errors['ContactName'] = ['Required']
        if email is None or email == "":
            errors['Email'] = ['Required']
        if newOrg is not None:
            if organizationName is None or organizationName == "":
                errors['OrganizationName'] = ['Required']
            if organizationAddress is None or organizationAddress == "":
                errors['OrganizationAddress'] = ['Required']
    if len(errors) > 0:
        session["validationErrors"] = errors
        session["validationData"] = g.data
        return redirect(request.referrer)
    # Finally all the form validation is done
    if existing != "":
        TenativeBooking.saveToSession(organizationId=organization, contactId=contact)
    elif newContact != "":
        # create new contact and save id to session
        c = Contact(name=contactName, cell_phone=cellPhone, work_phone=workPhone, email=email,
                    organization_id=organization)
        c.save()
        TenativeBooking.saveToSession(organizationId=organization, contactId=c.id)
    elif newOrg != "":
        # create new org and new contact and save to session
        org = Organization(name=organizationName, address=organizationAddress)
        org.save()
        c = Contact(name=contactName, cell_phone=cellPhone, work_phone=workPhone, email=email, organization_id=org.id)
        c.save()
        TenativeBooking.saveToSession(organizationId=org.id, contactId=c.id)
    return redirect(url_for('event.confirmBooking'))


@blueprint.route('/book/confirm')
def confirmBooking():
    t = TenativeBooking.loadFromSession()
    return render_template('event/confirm.html', booking=t)


@blueprint.route('/book/confirm', methods=['POST'])
def processConfirmBooking():
    # TODO group inserts together and not individually
    # http://docs.peewee-orm.com/en/latest/peewee/querying.html#bulk-inserts
    t = TenativeBooking.loadFromSession()
    b = Booking(contact=t.contact(), creator=g.User, discountAmount=t.discountAmount,
                discountPercent=t.discountPercent, startTime=t.start, endTime=t.finish,
                eventName=t.name, finalPrice=t.total(), isCanceled=False)
    rooms = t.rooms()
    if Room.areRoomsFree(rooms, t.start, t.finish):
        b.save()

        for room in rooms:
            br = BookingRoom(booking=b, room=room)
            br.save()
        for f in t.food:
            if t.food[f] > 0:
                Order(dish=Dish.get(Dish.id == int(f)), booking=b, quantity=t.food[f]).save()
        flash("Created event: '%s'" % t.name, 'success')
        t.cleanSession()
    else:
        flash('The room you selected has been taken by another booking.  Please select a different room.', 'error')
        return redirect(url_for('event.selectRoom'))
    return redirect(url_for('main.index'))

