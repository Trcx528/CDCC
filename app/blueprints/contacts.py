from flask import Blueprint, render_template, g, flash, redirect, url_for
from app.validation import validate
from app.models import Organization, Contact
from peewee import prefetch

blueprint = Blueprint('contacts', __name__)

@blueprint.before_request
def adminCheck():
    if not g.User.isAdmin:
        flash("You are not allow to access that", "error")
        return redirect(url_for('main.index'))



@blueprint.route('/admin/contacts')
def index():
    orgs = Organization.select()
    contacts = Contact.select()
    org_contacts = prefetch(orgs, contacts)
    contacts = Contact.select().where(Contact.organization == None)
    return render_template('admin/contacts/index.html', organizations=org_contacts, contacts=contacts)


@blueprint.route('/admin/contacts/create')
def create():
    orgs = {0: "None"}
    for org in Organization.select():
        orgs[org.id] = org.name
    return render_template('admin/contacts/create.html', orgs=orgs)


@blueprint.route('/admin/contacts/create', methods=['POST'])
@validate(Name="str|required", CellPhone="phone", WorkPhone="phone", Email="email|required", Organization="int")
def processCreate(name, email, cellPhone, workPhone, organization):
    organization = None if organization == 0 else organization
    newContact = Contact(name=name, email=email, work_phone=workPhone, cell_phone=cellPhone,
                         organization_id=organization)
    newContact.save()
    flash("Created Contact %s" % name, 'success')
    return redirect(url_for('contacts.index'))


@blueprint.route('/admin/contacts/<int:id>')
def edit(id):
    contact = Contact.select().where(Contact.id == id).get()
    orgs = {0: "None"}
    for org in Organization.select():
        orgs[org.id] = org.name
    return render_template('admin/contacts/edit.html', contact=contact, orgs=orgs)


@blueprint.route('/admin/contacts/<int:id>', methods=['POST'])
@validate(Name="str|required", CellPhone="phone", WorkPhone="phone", Email="email|required", Organization="int")
def processEdit(id, name, email, cellPhone, workPhone, organization):
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
    contact = Contact.select().where(Contact.id == id).get()
    contact.delete_instance()
    flash('Contact %s deleted' % contact.name, 'success')
    return redirect(url_for('contacts.index'))
