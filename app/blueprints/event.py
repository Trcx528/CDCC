from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, redirect, url_for, session, request, g, flash
from app.validation import validate, datetimeFormat
from app.models import *
from peewee import JOIN, prefetch

blueprint = Blueprint('event', __name__)

class TenativeBooking():
    start = None
    finish = None
    capacity = None
    roomIds = None
    food = None
    name = None
    discountPercent = None
    discountAmount = None
    contactId = None
    organizationId = None

    @classmethod
    def loadFromSession(cls, prefix=""):
        s = cls()
        today = datetime.fromordinal(date.today().toordinal())
        s.start = session[prefix + 'start'] if prefix + 'start' in session else today + timedelta(days=1, hours=8)
        s.finish = session[prefix + 'finish'] if prefix + 'finish' in session else today + timedelta(days=1, hours=12)
        s.capacity = session[prefix + 'capacity'] if prefix + 'capacity' in session else 25
        s.roomIds = session[prefix + 'roomIds'] if prefix + 'roomIds' in session else []
        s.food = session[prefix + 'food'] if prefix + 'food' in session else {}
        s.name = session[prefix + 'name'] if prefix + 'name' in session else ""
        s.discountPercent = session[prefix + 'discountPercent'] if prefix + 'discountPercent' in session else 0.0
        s.discountAmount = session[prefix + 'discountAmount'] if prefix + 'discountAmount' in session else 0.0
        s.contactId = session[prefix + 'contactId'] if prefix + 'contactId' in session else 0
        s.organizationId = session[prefix + 'organizationId'] if prefix + 'organizationId' in session else 0
        return s

    @classmethod
    def saveToSession(cls, prefix="", **kwargs):
        for k in kwargs:
            session[prefix + k] = kwargs[k]

    def cleanSession(self, prefix=""):
        session.pop(prefix + "start")
        session.pop(prefix + "finish")
        session.pop(prefix + "capacity")
        session.pop(prefix + "roomIds")
        session.pop(prefix + "food")
        session.pop(prefix + "name")
        session.pop(prefix + "discountPercent")
        session.pop(prefix + "discountAmount")
        session.pop(prefix + "contactId")
        session.pop(prefix + "organizationId")

    def roomPrice(self):
        ret = 0
        for r in Room.select().where(Room.id << self.roomIds):
            ret += r.price
        return float(ret)

    def duration(self):
        return float((self.finish - self.start).total_seconds()/60/60)

    def rooms(self):
        return Room.select().where(Room.id << self.roomIds)

    def contact(self):
        return Contact.select().where(Contact.id == self.contactId).get()

    def organization(self):
        if self.organizationId != 0: # will return none if no return value
            return Organization.select().where(Organization.id == self.organizationId).get()

    def getFood(self):
        foodIds = []
        for f in self.food:
            if self.food[f] > 0:
                foodIds.append(int(f))
        ret = []
        for food in Dish.select().where(Dish.id << foodIds):
            ret.append({'name': food.name, 'rate': food.price, 'quantity': self.food[str(food.id)],
                        'total': self.food[str(food.id)] * food.price})
        return ret
    
    def foodTotal(self):
        ret = 0
        for f in self.getFood():
            ret += float(f['total'])
        return ret

    def roomTotal(self):
        ret = 0
        for room in self.rooms():
            ret += float(room.getTotal(self.duration()))
        return ret

    def subTotal(self):
        ret = self.foodTotal()
        ret += self.roomTotal()
        return ret

    def total(self):
        return self.subTotal() - self.getDiscount()

    def getDiscount(self):
        return ((self.subTotal() - self.discountAmount) * self.discountPercent/100) + self.discountAmount



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
        rooms.append({'ids': [room.id], 'rate': room.price, 'capacity': room.capacity, 'name': room.name,
                      'optionId': len(rooms) + 1, 'total': (float(room.price) * t.duration())})

    # finalize
    return render_template('event/room.html', rooms=rooms, start=t.start, finish=t.finish, capacity=t.capacity,
                           selectedIds=t.roomIds if len(t.roomIds) > 0 else None)


@blueprint.route('/book/room', methods=['POST'])
@validate(roomIds='list|required|type=int')
def processSelectRoom(roomIds):
    TenativeBooking.saveToSession(roomIds=roomIds)
    return redirect(url_for('event.selectFood'))


@blueprint.route('/book/caterers')
def selectFood():
    t = TenativeBooking.loadFromSession()
    hours = t.duration()
    price = t.roomPrice()
    d = Dish.select()
    c = Caterer.select()
    dishes = prefetch(d, c)
    return render_template('event/caterer.html', dishes=dishes, roomHours=hours, roomPrice=price,
                           roomTotal=(hours * price), rooms=t.rooms(), food=t.food)


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
    orgs = Organization.select()
    contacts = Contact.select()
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
    try:
        # TODO group inserts together and not individually
        # http://docs.peewee-orm.com/en/latest/peewee/querying.html#bulk-inserts
        t = TenativeBooking.loadFromSession()
        b = Booking(contact=t.contact(), creator=g.User, discountAmount=t.discountAmount,
                    discountPercent=t.discountPercent, startTime=t.start, endTime=t.finish,
                    eventName=t.name, finalPrice=t.total(), isCanceled=False)
        b.save()
        rooms = t.rooms()
        for room in rooms:
            br = BookingRoom(booking=b, room=room)
            br.save()
        for f in t.food:
            if t.food[f] > 0:
                Order(dish=Dish.get(Dish.id == int(f)), booking=b, quantity=t.food[f]).save()
        flash("Created event: '%s'" % t.name, 'success')
        t.cleanSession()
    except:
        flash("Error Creating Booking", "error")
    return redirect(url_for('main.index'))

