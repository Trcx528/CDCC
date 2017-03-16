import hashlib
from app import db
from peewee import CharField, DateTimeField



class User(db.Model):
    FirstName = CharField()
    LastName = CharField()
    EmailAddress = CharField(unique=True)
    PasswordHash = CharField()
    LastLogin = DateTimeField(null=True, default=None)

    def setPassword(self, password):
        self.PasswordHash = hashlib.sha512(password.encode()).hexdigest()

    def checkPassword(self, password):
        return self.PasswordHash == hashlib.sha512(password.encode()).hexdigest()
