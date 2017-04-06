from datetime import datetime, date, timedelta
from flask import session
from app.models import *

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


    def duration(self):
        return float((self.finish - self.start).total_seconds()/60/60)

    def rooms(self):
        if not hasattr(self, 'roomsPrefetch'):
            self.roomsPrefetch = Room.select().where(Room.id << self.roomIds).execute()
        return self.roomsPrefetch

    def contact(self):
        return Contact.select().where(Contact.id == self.contactId).get()

    def organization(self):
        if self.organizationId != 0: # will return none if no return value
            if not hasattr(self, 'orgcache'):
                self.orgcache = Organization.select().where(Organization.id == self.organizationId).get()
            return self.orgcache

    def getFood(self):
        ret = []
        if not hasattr(self, 'dishPrefetch'):
            foodIds = []
            for f in self.food:
                if self.food[f] > 0:
                    foodIds.append(int(f))
            self.dishPrefetch = Dish.select().where(Dish.id << foodIds).execute()
        for food in self.dishPrefetch:
            ret.append({'name': food.name, 'rate': food.price, 'quantity': self.food[str(food.id)],
                        'total': self.food[str(food.id)] * food.price})
        return ret

    def foodTotal(self):
        ret = 0
        for f in self.getFood():
            ret += float(f['total'])
        return ret

    def roomTotal(self):
        return self.roomCombo().price

    def subTotal(self):
        ret = self.foodTotal()
        ret += self.roomCombo().price
        return ret

    def total(self):
        return self.subTotal() - self.getDiscount()

    def getDiscount(self):
        return ((self.subTotal() - self.discountAmount) * self.discountPercent/100) + self.discountAmount


class RoomCombo():
    rooms = None
    capacity = 0
    rate = 0
    name = ""
    id = ""
    price = ""
    roomIds = []

    def __init__(self, rooms, duration):
        self.rooms = rooms
        name = []
        self.roomIds = []
        for room in rooms:
            self.roomIds.append(str(room.id))
            name.append(room.name)
            self.capacity += room.capacity
            self.rate += float(room.price)
        self.roomIds.sort()
        self.name = ", ".join(name)
        self.id = "_".join(self.roomIds)
        self.price = float(duration) * float(self.rate)

    def __repr__(self):
        return "<RoomCombo Name=%s Capacity=%s Rate=%s Price=%s>"  % (self.name, self.capacity, self.rate, self.price)

    @classmethod
    def getCombos(cls, rooms, duration=1, capacity=None):
        # this is messy and recursion might be a better answer but this works and it maxes 3 rooms
        rsById = {}
        comboRooms = {}
        for room in rooms:
            rsById[str(room.id)] = room
        for id in rsById:
            room = rsById[id]
            comboRooms[str(id)] = RoomCombo([room], duration)
            for aid in room.adjacentRoomIds():
                if aid in rsById:
                    print(rsById[aid])
                    strid = [str(id), str(aid)]
                    strid.sort()
                    if "_".join(strid) not in comboRooms:
                        comboRooms["_".join(strid)] = RoomCombo([rsById[id], rsById[aid]], duration)
                    for aaid in room.adjacentRoomIds():
                        if aaid != aid and aaid in rsById:
                            strid = [str(id), str(aid), str(aaid)]
                            strid.sort()
                            if "_".join(strid) not in comboRooms:
                                comboRooms["_".join(strid)] = RoomCombo([rsById[id], rsById[aid], rsById[aaid]],
                                                                        duration)
        if capacity is not None:
            rets = comboRooms
            comboRooms = {}
            for id in rets:
                if rets[id].capacity >= capacity:
                    comboRooms[id] = rets[id]
        ret = []
        for val in comboRooms.values():
            ret.append(val)
        return ret

    @classmethod
    def rateSort(cls, self):
        return self.rate

