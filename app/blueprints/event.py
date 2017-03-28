from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, redirect, url_for, session, request, g
from app.validation import validate, datetimeFormat
from app.models import Caterer, Dish, Room, Organization, Contact, Attachment

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

    def roomPrice(self):
        ret = 0
        for r in Room.select().where(Room.id << self.roomIds):
            ret += r.price
        return round(float(ret), 2)

    def duration(self):
        return round(float((self.finish - self.start).total_seconds()/60/60), 2)

    def rooms(self):
        return Room.select().where(Room.id << self.roomIds)

    def contact(self):
        return Contact.select().where(Contact.id == self.contactId).get()

    def organization(self):
        return Organization.select().where(Organization.id == self.organizationId).get()

    def getFood(self):
        foodIds = []
        for f in self.food:
            if self.food[f] > 0:
                foodIds.append(int(f))
        ret = []
        for food in Dish.select().where(Dish.id << foodIds):
            ret.append({'name': food.name, 'rate': food.price, 'quantity': self.food[str(food.id)],
                        'total': round(self.food[str(food.id)] * food.price, 2)})
        print(ret)
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
        return round(self.subTotal() - self.getDiscount(), 2)

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
    return render_template('event/room.html', rooms=rooms, start=t.start, finish=t.finish, capacity=t.capacity)


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
    dishes = Dish.select().join(Caterer)
    print(t.food)
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
    contacts = Contact.select().join(Organization)
    t = TenativeBooking.loadFromSession()
    return render_template('event/finalize.html', orgs=orgs, contacts=contacts, booking=t)


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
    print(errors)
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
    return redirect(url_for('main.index'))
