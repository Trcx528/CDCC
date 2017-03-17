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

    def adjacentRooms(self):
        # TODO
        pass

    def addAdjacentRoom(self):
        # TODO
        pass

    def removeAdjacentRoom(self):
        # TODO
        pass




class Organization(db.Model):
    address = CharField()
    name = CharField()


class Contact(db.Model):
    cell_phone = CharField(null=True)
    email = CharField(null=True)
    name = CharField()
    organization = ForeignKeyField(null=True, rel_model=Organization, to_field='id')
    work_phone = CharField(null=True)


class Booking(db.Model):
    canceler = IntegerField(index=True, null=True)
    contact = ForeignKeyField(rel_model=Contact, to_field='id')
    creator = ForeignKeyField(rel_model=User, to_field='id')
    discountAmount = DecimalField()
    discountPercent = DecimalField()
    endTime = DateTimeField()
    eventName = CharField()
    finalPrice = DecimalField(null=True)
    isCanceled = BooleanField()
    startTime = DateTimeField()


class Attachment(db.Model):
    booking = ForeignKeyField(rel_model=Booking, to_field='id')
    filePath = CharField()


class BookingRoom(db.Model):
    booking = ForeignKeyField(rel_model=Booking, to_field='id')
    room = ForeignKeyField(rel_model=Room, to_field='id')


class Caterer(db.Model):
    name = CharField()
    phone = CharField()


class Dishes(db.Model):
    caterer = ForeignKeyField(rel_model=Caterer, to_field='id')
    dishName = CharField()
    price = DecimalField()


class Order(db.Model):
    booking = ForeignKeyField(rel_model=Booking, to_field='id')
    menu = ForeignKeyField(rel_model=Dishes, to_field='id')
    quantity = IntegerField()
