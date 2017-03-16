import hashlib
from app import db
from peewee import CharField, DateTimeField, DecimalField, BooleanField, ForeignKeyField



class User(db.Model):
    firstName = CharField()
    lastName = CharField()
    emailAddress = CharField(unique=True)
    passwordHash = CharField()
    lastLogin = DateTimeField(null=True, default=None)

    def setPassword(self, password):
        self.passwordHash = hashlib.sha512(password.encode()).hexdigest()

    def checkPassword(self, password):
        return self.passwordHash == hashlib.sha512(password.encode()).hexdigest()

class Booking(db.Model):
    startTime = DateTimeField()
    endTime = DateTimeField()
    eventName = CharField()
    discountPercent = DecimalField(default=0)
    discountAmount = DecimalField(default=0)
    finalPrice = DecimalField(null=True)
    isCanceled = BooleanField(default=False)
    creator = ForeignKeyField(User, related_name="bookings")
