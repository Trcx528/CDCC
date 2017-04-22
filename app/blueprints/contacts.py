""" This file contains the CRUD for contacts """

from flask import Blueprint, render_template, flash, redirect, url_for
from app.validation import validate
from app.models import Organization, Contact
from peewee import prefetch

blueprint = Blueprint('contacts', __name__)

@blueprint.route('/admin/contacts')
def index():
    """Lists all contacts"""
    orgs = Organization.select().where(Organization.isDeleted == False)
    contacts = Contact.select().where(Contact.isDeleted == False)
    org_contacts = prefetch(orgs, contacts)
    contacts = Contact.select().where(Contact.organization == None, Contact.isDeleted == False)
    return render_template('admin/contacts/index.html', organizations=org_contacts, contacts=contacts)


@blueprint.route('/admin/contacts/create')
def create():
    """View to gather information to create a new contact"""
    orgs = {0: "None"}
    for org in Organization.select().where(Organization.isDeleted == False):
        orgs[org.id] = org.name
    return render_template('admin/contacts/create.html', orgs=orgs)


@blueprint.route('/admin/contacts/create', methods=['POST'])
@validate(Name="str|required", CellPhone="phone", WorkPhone="phone", Email="email|required", Organization="int")
def processCreate(name, email, cellPhone, workPhone, organization):
    """Creates a new contact based on POST data"""
    organization = None if organization == 0 else organization
    newContact = Contact(name=name, email=email, work_phone=workPhone, cell_phone=cellPhone,
                         organization_id=organization)
    newContact.save()
    flash("Created Contact %s" % name, 'success')
    return redirect(url_for('contacts.index'))


@blueprint.route('/admin/contacts/<int:id>')
def edit(id):
    """View to display contact data"""
    contact = Contact.select().where(Contact.id == id).get()
    orgs = {0: "None"}
    for org in Organization.select().where((Organization.isDeleted == False) |
                                           (Organization.id == contact.organization_id)):
        orgs[org.id] = org.name
    return render_template('admin/contacts/edit.html', contact=contact, orgs=orgs)


@blueprint.route('/admin/contacts/<int:id>', methods=['POST'])
@validate(Name="str|required", CellPhone="phone", WorkPhone="phone", Email="email|required", Organization="int")
def processEdit(id, name, email, cellPhone, workPhone, organization):
    """Updates a contact based on POST data"""
    organization = None if organization is 0 else organization
    contact = Contact.select().where(Contact.id == id).get()
    contact.name = name
    contact.email = email
    contact.cell_phone = cellPhone
    contact.work_phone = workPhone
    contact.organization_id = organization
    contact.save()
    flash("Updated %s" % name, 'success')
    return redirect(url_for('contacts.index'))


@blueprint.route('/admin/contacts/<int:id>/delete', methods=['POST'])
def delete(id):
    """Softdeletes a contact"""
    contact = Contact.select().where(Contact.id == id).get()
    contact.isDeleted = True
    contact.save()
    flash('Contact %s deleted' % contact.name, 'success')
    return redirect(url_for('contacts.index'))

@blueprint.route('/admin/contacts/<int:id>/restore', methods=['POST'])
def restore(id):
    """Restores a softdeleted contact"""
    Contact.update(isDeleted=False).where(Contact.id == id).execute()
    flash('Contact restored', 'success')
    return redirect(url_for('contacts.edit', id=id))

