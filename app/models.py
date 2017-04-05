import hashlib
from app import db
from peewee import CharField, DateTimeField, DecimalField, BooleanField, ForeignKeyField, IntegerField, JOIN


class User(db.Model):
    firstName = CharField()
    lastName = CharField()
    emailAddress = CharField(unique=True)
    passwordHash = CharField()
    lastLogin = DateTimeField(null=True, default=None)
    isAdmin = BooleanField(default=False)

    def setPassword(self, password):
        self.passwordHash = hashlib.sha512(password.encode()).hexdigest()

    def checkPassword(self, password):
        return self.passwordHash == hashlib.sha512(password.encode()).hexdigest()


class Room(db.Model):
    capacity = IntegerField()
    name = CharField()
    price = DecimalField()
    comboRooms = CharField(default="")

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
        return Room.select().join(BookingRoom, JOIN.LEFT_OUTER).join(Booking, JOIN.LEFT_OUTER).where(
            (Booking.startTime >> None) | (Booking.id == bookingIncludeId) |
            (((Booking.startTime < start) & (Booking.endTime < end) &
              (Booking.startTime < end) & (Booking.endTime < end)) |
             ((Booking.startTime > start) & (Booking.endTime > start) &
              (Booking.startTime > end) & (Booking.endTime > end))))

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


class Contact(db.Model):
    cell_phone = CharField(null=True)
    email = CharField(null=True)
    name = CharField()
    organization = ForeignKeyField(null=True, rel_model=Organization, to_field='id', related_name='contacts')
    work_phone = CharField(null=True)


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
        if hasattr(self, 'bookingroom_set_prefetch'):
            for br in self.bookingroom_set_prefetch:
                ret.append(br.room)
        else:
            for br in self.bookingroom_set:
                ret.append(br.room)
        return ret

    def selectedRoomIds(self):
        ret = []
        if hasattr(self, 'bookingroom_set_prefetch'):
            for br in self.bookingroom_set_prefetch:
                ret.append(br.room_id)
        else:
            for br in self.bookingroom_set:
                ret.append(br.room_id)
        return ret


class Attachment(db.Model):
    booking = ForeignKeyField(rel_model=Booking, to_field='id', related_name='attachments')
    filePath = CharField()


class BookingRoom(db.Model):
    booking = ForeignKeyField(rel_model=Booking, to_field='id')
    room = ForeignKeyField(rel_model=Room, to_field='id')


class Caterer(db.Model):
    name = CharField()
    phone = CharField()


class Dish(db.Model):
    caterer = ForeignKeyField(rel_model=Caterer, to_field='id', related_name='dishes')
    name = CharField()
    price = DecimalField()


class Order(db.Model):
    booking = ForeignKeyField(rel_model=Booking, to_field='id', related_name='orders')
    dish = ForeignKeyField(rel_model=Dish, to_field='id', related_name='orders')
    quantity = IntegerField()
