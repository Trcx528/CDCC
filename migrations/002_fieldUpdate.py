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
        'caterer',

        isDeleted=pw.BooleanField(default=False))

    migrator.add_fields(
        'dish',

        isDeleted=pw.BooleanField(default=False))

    migrator.add_fields(
        'organization',

        isDeleted=pw.BooleanField(default=False))

    migrator.add_fields(
        'contact',

        isDeleted=pw.BooleanField(default=False))

    migrator.add_fields(
        'room',

        isDeleted=pw.BooleanField(default=False),
        dimensions=pw.CharField(default='', max_length=255))

    migrator.add_fields(
        'user',

        isDeleted=pw.BooleanField(default=False))

    migrator.add_fields(
        'booking',

        cancelationReason=pw.CharField(default='', max_length=2048))


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_fields('booking', 'cancelationReason')

    migrator.remove_fields('user', 'isDeleted')

    migrator.remove_fields('room', 'isDeleted', 'dimensions')

    migrator.remove_fields('contact', 'isDeleted')

    migrator.remove_fields('organization', 'isDeleted')

    migrator.remove_fields('dish', 'isDeleted')

    migrator.remove_fields('caterer', 'isDeleted')
