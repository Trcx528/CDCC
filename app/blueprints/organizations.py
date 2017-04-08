from flask import Blueprint, render_template, g, flash, redirect, url_for
from app.validation import validate
from app.models import Organization, Contact


blueprint = Blueprint('organizations', __name__)

@blueprint.before_request
def adminCheck():
    if not g.User.isAdmin:
        flash("You are not allow to access that", "error")
        return redirect(url_for('main.index'))



@blueprint.route('/admin/organizations/create')
def create():
    return render_template('admin/organizations/create.html',
                           contacts=Contact.select().where(Contact.organization == None, Contact.isDeleted == False))


@blueprint.route('/admin/organizations/create', methods=['POST'])
@validate(Name="str|required", Address="str|required", Contacts="multiselect")
def processCreate(name, address, contacts):
    newOrg = Organization(name=name, address=address)
    newOrg.save()
    Contact.update(organization=newOrg).where(Contact.id << contacts).execute()
    flash('Created %s' % name, 'success')
    return redirect(url_for('contacts.index'))


@blueprint.route('/admin/organizations/<int:id>')
def edit(id):
    org = Organization.select().where(Organization.id == id).get()
    return render_template('admin/organizations/edit.html', org=org,
                           contacts=Contact.select().where((Contact.organization == None) |
                                                           (Contact.organization == org), Contact.isDeleted == False))


@blueprint.route('/admin/organizations/<int:id>', methods=['POST'])
@validate(Name="str|required", Address="str|required", Contacts="multiselect")
def processEdit(id, name, address, contacts):
    Organization.update(name=name, address=address).where(Organization.id == id).execute()
    org = Organization.select().where(Organization.id == id).get()
    Contact.update(organization=None).where(Contact.organization == org).execute()
    Contact.update(organization=org).where(Contact.id << contacts).execute()
    flash('Organization %s updated' % name, 'success')
    return redirect(url_for('contacts.index'))


@blueprint.route('/admin/organizations/<int:id>/delete', methods=["POST"])
def delete(id):
    Organization.update(isDeleted=True).where(Organization.id == id).execute()
    flash('Deleted organization', 'success')
    return redirect(url_for('contacts.index'))

@blueprint.route('/admin/organizations/<int:id>/restore', methods=["POST"])
def restore(id):
    Organization.update(isDeleted=False).where(Organization.id == id).execute()
    flash('Restored organization', 'success')
    return redirect(url_for('contacts.index'))
