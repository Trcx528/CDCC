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
    class User(pw.Model):
        firstName = pw.CharField(max_length=255)
        lastName = pw.CharField(max_length=255)
        emailAddress = pw.CharField(max_length=255, unique=True)
        passwordHash = pw.CharField(max_length=255)
        lastLogin = pw.DateTimeField(null=True)

    @migrator.create_model
    class Booking(pw.Model):
        startTime = pw.DateTimeField()
        endTime = pw.DateTimeField()
        eventName = pw.CharField(max_length=255)
        discountPercent = pw.DecimalField(auto_round=False, decimal_places=5, default=0, max_digits=10, rounding='ROUND_HALF_EVEN')
        discountAmount = pw.DecimalField(auto_round=False, decimal_places=5, default=0, max_digits=10, rounding='ROUND_HALF_EVEN')
        finalPrice = pw.DecimalField(auto_round=False, decimal_places=5, max_digits=10, null=True, rounding='ROUND_HALF_EVEN')
        isCanceled = pw.BooleanField(default=False)
        creator = pw.ForeignKeyField(db_column='creator_id', rel_model=User, to_field='id')



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('booking')

    migrator.remove_model('user')
