import hashlib
from app import db
from peewee import CharField, DateTimeField, DecimalField, BooleanField, ForeignKeyField, IntegerField


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
        print(self.comboRooms)
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

    def rooms(self):
        ret = []
        for room in BookingRoom.select().where(BookingRoom.booking == self).join(Room):
            ret.append(room)
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


class Dishes(db.Model):
    caterer = ForeignKeyField(rel_model=Caterer, to_field='id', related_name='dishes')
    dishName = CharField()
    price = DecimalField()


class Order(db.Model):
    booking = ForeignKeyField(rel_model=Booking, to_field='id', related_name='orders')
    menu = ForeignKeyField(rel_model=Dishes, to_field='id', related_name='orders')
    quantity = IntegerField()
