"""This file contains the entities present in the database"""

import hashlib
from app import db
from peewee import CharField, DateTimeField, DecimalField, BooleanField, ForeignKeyField, IntegerField, JOIN, fn


class User(db.Model):
    firstName = CharField()
    lastName = CharField()
    emailAddress = CharField(unique=True)
    passwordHash = CharField()
    lastLogin = DateTimeField(null=True, default=None)
    isAdmin = BooleanField(default=False)
    isDeleted = BooleanField(default=False)

    def setPassword(self, password):
        self.passwordHash = hashlib.sha512(password.encode()).hexdigest()

    def checkPassword(self, password):
        if self.isDeleted:
            return False
        return self.passwordHash == hashlib.sha512(password.encode()).hexdigest()


class Room(db.Model):
    capacity = IntegerField()
    name = CharField()
    price = DecimalField()
    comboRooms = CharField(default="")
    dimensions = CharField(default='')
    isDeleted = BooleanField(default=False)

    def adjacentRoomIds(self):
        ret = []
        for id in self.comboRooms.split(','):
            if id != '':
                ret.append(id)
        return ret

    def adjacentRooms(self):
        return Room.select().where(Room.id << self.adjacentRoomIds())

    def setAdjacentRooms(self, roomList):
        for id in self.adjacentRoomIds():
            if id not in roomList:
                self.removeAdjacentRoom(id)
        for id in roomList:
            if id not in self.adjacentRoomIds():
                self.addAdjacentRoom(id)

    def addAdjacentRoom(self, id):
        if hasattr(id, "id"):
            id = id.id
        arids = self.adjacentRoomIds()
        oroom = Room.select().where(Room.id == id).get()
        orids = oroom.adjacentRoomIds()
        arids.append(str(id))
        orids.append(str(self.id))
        self.comboRooms = ",".join(arids)
        oroom.comboRooms = ",".join(orids)
        self.save()
        oroom.save()

    def removeAdjacentRoom(self, id):
        if hasattr(id, "id"):
            id = id.id
        arids = self.adjacentRoomIds()
        oroom = Room.select().where(Room.id == id).get()
        orids = oroom.adjacentRoomIds()
        arids.remove(str(id))
        orids.remove(str(self.id))
        self.comboRooms = ",".join(arids)
        oroom.comboRooms = ",".join(orids)
        self.save()
        oroom.save()

    def getTotal(self, duration):
        return duration * float(self.price)

    def perPersonRate(self):
        return self.price/self.capacity

    def __repr__(self):
        return "<Room Name=%s>" % self.name

    @classmethod
    def openRooms(cls, start, end, bookingIncludeId=0):
        """Returns rooms that are open during a specific time period"""
        print(start, end, bookingIncludeId)
        # get a list of rooms that are unavalible for a given time
        taken_rooms = Room.select(Room.id).join(BookingRoom, JOIN.LEFT_OUTER).join(Booking, JOIN.LEFT_OUTER).where(
            (((start <= Booking.endTime) & (end >= Booking.endTime)) | # Booking.endTime is in the middle of new booking
             ((end >= Booking.endTime) & (start <= Booking.startTime)) | # Booking is inside of new booking
             ((start <= Booking.startTime) & (end >= Booking.startTime))) & # Booking.startTime is in new booking
            (Booking.isCanceled == False) & # exclude cancled bookings
            (Booking.id != bookingIncludeId) # exclude the currrent booking (so the room will be avalible)
        ).group_by(Room.id)
        return Room.select().where(Room.id.not_in(taken_rooms) & (Room.isDeleted == False))

    @classmethod
    def areRoomsFree(cls, rooms, start, end, bookingIncludeId=0):
        flag = True
        openRooms = cls.openRooms(start, end, bookingIncludeId).execute()
        for room in rooms:
            if room not in openRooms:
                flag = False
        return flag

class Organization(db.Model):
    address = CharField()
    name = CharField()
    isDeleted = BooleanField(default=False)


class Contact(db.Model):
    cell_phone = CharField(null=True)
    email = CharField(null=True)
    name = CharField()
    organization = ForeignKeyField(null=True, rel_model=Organization, to_field='id', related_name='contacts')
    work_phone = CharField(null=True)
    isDeleted = BooleanField(default=False)


class Booking(db.Model):
    canceler = IntegerField(index=True, null=True)
    contact = ForeignKeyField(rel_model=Contact, to_field='id', related_name='bookings')
    creator = ForeignKeyField(rel_model=User, to_field='id', related_name='createdBookings')
    discountAmount = DecimalField()
    discountPercent = DecimalField()
    endTime = DateTimeField()
    eventName = CharField()
    finalPrice = DecimalField(null=True)
    isCanceled = BooleanField()
    startTime = DateTimeField()
    cancelationReason = CharField(max_length=2048, default='')
    catereringTotal = DecimalField(null=True)
    roomTotal = DecimalField(null=True)
    subtotal = DecimalField(null=True)
    discountTotal = DecimalField(null=True)
    canceledRooms = CharField(null=True)

    def delete(self, canceler, reason):
        self.calculateTotal()
        self.cancelationReason = reason
        self.canceler = canceler
        tmpRooms = []
        for rid in self.selectedRoomIds():
            tmpRooms.append(str(rid))
        self.canceledRooms = ','.join(tmpRooms)
        self.isCanceled = True
        return self

    @property
    def canceledBy(self):
        if not hasattr(self, 'cancelerUserPre'):
            self.cancelerUserPre = User.select().where(User.id == self.canceler).get()
        return self.cancelerUserPre

    def foodList(self):
        ret = {}
        if hasattr(self, 'orders_prefetch'):
            for o in self.orders_prefetch:
                ret[o.dish_id] = o.quantity
        else:
            for o in self.orders:
                ret[o.dish_id] = o.quantity
        return ret

    def selectedRooms(self):
        ret = []
        if self.isCanceled:
            if not hasattr(self, 'cancledRoomsPrebuilt'):
                self.cancledRoomsPrebuilt = Room.select().where(Room.id << self.selectedRoomIds()).execute()
            return self.cancledRoomsPrebuilt
        if hasattr(self, 'bookingroom_set_prefetch'):
            for br in self.bookingroom_set_prefetch:
                ret.append(br.room)
        else:
            for br in self.bookingroom_set:
                ret.append(br.room)
        return ret

    def selectedRoomIds(self):
        ret = []
        if self.isCanceled:
            if self.canceledRooms is None:
                return []
            return self.canceledRooms.split(',')
        if hasattr(self, 'bookingroom_set_prefetch'):
            for br in self.bookingroom_set_prefetch:
                ret.append(br.room_id)
        else:
            for br in self.bookingroom_set:
                ret.append(br.room_id)
        return ret

    def calculateRoomTotal(self):
        self.roomTotal = self.roomCombo.price

    def calculateCatereringTotal(self):
        self.catereringTotal = 0
        orders = self.orders
        if hasattr(self, 'orders_prefetch'):
            orders = self.orders_prefetch
        for order in orders:
            self.catereringTotal += float(order.quantity) * float(order.dish.price)

    def calculateSubtotal(self):
        self.subtotal = self.catereringTotal + self.roomTotal

    def calculateDiscountTotal(self):
        self.discountTotal = ((self.subtotal - float(self.discountAmount)) * float(self.discountPercent)/100)
        self.discountTotal += float(self.discountAmount)

    def calculateTotal(self):
        self.calculateCatereringTotal()
        self.calculateRoomTotal()
        self.calculateSubtotal()
        self.calculateDiscountTotal()
        self.finalPrice = self.subtotal - self.discountTotal

    @property
    def duration(self):
        return float((self.endTime - self.startTime).total_seconds()/60/60)

    @property
    def roomCombo(self):
        if not hasattr(self, 'roomComboPre'):
            import app.logic
            self.roomComboPre = app.logic.RoomCombo(self.selectedRooms(), self.duration)
        return self.roomComboPre

class Attachment(db.Model):
    booking = ForeignKeyField(rel_model=Booking, to_field='id', related_name='attachments')
    filePath = CharField()


class BookingRoom(db.Model):
    booking = ForeignKeyField(rel_model=Booking, to_field='id')
    room = ForeignKeyField(rel_model=Room, to_field='id')


class Caterer(db.Model):
    name = CharField()
    phone = CharField()
    isDeleted = BooleanField(default=False)


class Dish(db.Model):
    caterer = ForeignKeyField(rel_model=Caterer, to_field='id', related_name='dishes')
    name = CharField()
    price = DecimalField()
    isDeleted = BooleanField(default=False)


class Order(db.Model):
    booking = ForeignKeyField(rel_model=Booking, to_field='id', related_name='orders')
    dish = ForeignKeyField(rel_model=Dish, to_field='id', related_name='orders')
    quantity = IntegerField()
