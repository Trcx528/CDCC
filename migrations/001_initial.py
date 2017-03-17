"""Peewee migrations: ::

    > Model = migrator.orm['name']

    > migrator.sql(sql)
    > migrator.python(func, *args, **kwargs)
    > migrator.create_model(Model)
    > migrator.remove_model(Model, cascade=True)
    > migrator.add_fields(Model, **fields)
    > migrator.change_fields(Model, **fields)
    > migrator.remove_fields(Model, *field_names, cascade=True)
    > migrator.rename_field(Model, old_field_name, new_field_name)
    > migrator.rename_table(Model, new_table_name)
    > migrator.add_index(Model, *col_names, unique=False)
    > migrator.drop_index(Model, *col_names)
    > migrator.add_not_null(Model, *field_names)
    > migrator.drop_not_null(Model, *field_names)
    > migrator.add_default(Model, field_name, default)

"""

import datetime as dt
import peewee as pw


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    @migrator.create_model
    class Caterer(pw.Model):
        name = pw.CharField(max_length=255)
        phone = pw.CharField(max_length=255)

    @migrator.create_model
    class Dishes(pw.Model):
        caterer = pw.ForeignKeyField(db_column='caterer_id', rel_model=Caterer, to_field='id')
        dishName = pw.CharField(max_length=255)
        price = pw.DecimalField(auto_round=False, decimal_places=5, max_digits=10, rounding='ROUND_HALF_EVEN')

    @migrator.create_model
    class Organization(pw.Model):
        address = pw.CharField(max_length=255)
        name = pw.CharField(max_length=255)

    @migrator.create_model
    class Contact(pw.Model):
        cell_phone = pw.CharField(max_length=255, null=True)
        email = pw.CharField(max_length=255, null=True)
        name = pw.CharField(max_length=255)
        organization = pw.ForeignKeyField(db_column='organization_id', null=True, rel_model=Organization, to_field='id')
        work_phone = pw.CharField(max_length=255, null=True)

    @migrator.create_model
    class Room(pw.Model):
        capacity = pw.IntegerField()
        name = pw.CharField(max_length=255)
        price = pw.DecimalField(auto_round=False, decimal_places=5, max_digits=10, rounding='ROUND_HALF_EVEN')

    @migrator.create_model
    class User(pw.Model):
        firstName = pw.CharField(max_length=255)
        lastName = pw.CharField(max_length=255)
        emailAddress = pw.CharField(max_length=255, unique=True)
        passwordHash = pw.CharField(max_length=255)
        lastLogin = pw.DateTimeField(null=True)

    @migrator.create_model
    class Booking(pw.Model):
        canceler = pw.IntegerField(index=True, null=True)
        contact = pw.ForeignKeyField(db_column='contact_id', rel_model=Contact, to_field='id')
        creator = pw.ForeignKeyField(db_column='creator_id', rel_model=User, to_field='id')
        discountAmount = pw.DecimalField(auto_round=False, decimal_places=5, max_digits=10, rounding='ROUND_HALF_EVEN')
        discountPercent = pw.DecimalField(auto_round=False, decimal_places=5, max_digits=10, rounding='ROUND_HALF_EVEN')
        endTime = pw.DateTimeField()
        eventName = pw.CharField(max_length=255)
        finalPrice = pw.DecimalField(auto_round=False, decimal_places=5, max_digits=10, null=True, rounding='ROUND_HALF_EVEN')
        isCanceled = pw.BooleanField()
        startTime = pw.DateTimeField()

    @migrator.create_model
    class Order(pw.Model):
        booking = pw.ForeignKeyField(db_column='booking_id', rel_model=Booking, to_field='id')
        menu = pw.ForeignKeyField(db_column='menu_id', rel_model=Dishes, to_field='id')
        quantity = pw.IntegerField()

    @migrator.create_model
    class BookingRoom(pw.Model):
        booking = pw.ForeignKeyField(db_column='booking_id', rel_model=Booking, to_field='id')
        room = pw.ForeignKeyField(db_column='room_id', rel_model=Room, to_field='id')

    @migrator.create_model
    class Attachment(pw.Model):
        booking = pw.ForeignKeyField(db_column='booking_id', rel_model=Booking, to_field='id')
        filePath = pw.CharField(max_length=255)



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('attachment')

    migrator.remove_model('bookingroom')

    migrator.remove_model('order')

    migrator.remove_model('booking')

    migrator.remove_model('user')

    migrator.remove_model('room')

    migrator.remove_model('contact')

    migrator.remove_model('organization')

    migrator.remove_model('dishes')

    migrator.remove_model('caterer')
