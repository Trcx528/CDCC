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

    migrator.add_fields(
        'booking',

        catereringTotal=pw.DecimalField(auto_round=False, decimal_places=5, max_digits=10, null=True, rounding='ROUND_HALF_EVEN'),
        discountTotal=pw.DecimalField(auto_round=False, decimal_places=5, max_digits=10, null=True, rounding='ROUND_HALF_EVEN'),
        roomTotal=pw.DecimalField(auto_round=False, decimal_places=5, max_digits=10, null=True, rounding='ROUND_HALF_EVEN'),
        subtotal=pw.DecimalField(auto_round=False, decimal_places=5, max_digits=10, null=True, rounding='ROUND_HALF_EVEN'),
        canceledRooms=pw.CharField(max_length=255, null=True))


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_fields('booking', 'catereringTotal', 'discountTotal', 'roomTotal', 'subtotal', 'canceledRooms')
