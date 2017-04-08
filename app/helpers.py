import string
import random
from flask import Markup, g, session, request

datetimeFormat = "%m/%d/%Y %I:%M %p"
dateFormat = "%m/%d/%Y"
timeFormat = "%I:%M %p"

def value_for(name):
    if hasattr(g, "data"):
        if name in g.data:
            return g.data[name]
    return ""


def hidden(name, value):
    ret = '<input type="hidden" value="' + str(value) + '" name="' + str(name) + '"/>'
    return Markup(ret)

def form_group(ftype, label, inputName=None, placeholder=None, id=None, value=None, options={}, errors=[],
               innerDiv=["col-sm-10"], min=None, max=None, inputAttributes=None):
    """
    ftype: [text|password|select|multiselect|textarea|radio|number]
    label: visible name
    inputName: internal name (no spaces)
    """
    if inputName is None:
        inputName = label.replace(" ", "")
    if id is None:
        id = inputName
    if value is None:
        value = ""
        if hasattr(g, "data"):
            if inputName in g.data:
                value = str(Markup.escape(g.data[inputName]))
    if errors is not None:
        if hasattr(g, "hasErrors"):
            if g.hasErrors:
                if inputName in g.errors:
                    errors = g.errors[inputName]

    ret = '<div class="form-group'
    if errors is not None and len(errors) > 0:
        ret += ' has-error'
    ret += '">'
    if label is not None:
        ret += '<label class="col-sm-2 control-label" for="' + inputName + '">' + label + '</label>'
    if innerDiv is not None:
        ret += '<div class="' + ' '.join(innerDiv) + '">'

    if ftype == "text" or ftype == "password" or ftype == "number":
        ret += '<input class="form-control" name="' + inputName + '" type="' + ftype + '" id="' + id + '"'
        if value is not None:
            ret += ' value="' + str(value) + '"'
        if placeholder is not None:
            ret += ' placeholder="' + placeholder + '"'
        if min is not None:
            ret += ' min="' + str(min) + '"'
        if max is not None:
            ret += ' max="' + str(max) + '"'
        if inputAttributes is not None:
            for key in inputAttributes:
                ret += ' ' + str(key) + '="' + str(inputAttributes[key]) + '"   '
        ret += '>'
    elif ftype == "select" or ftype == "multiselect":
        if ftype == "multiselect":
            newval = []
            for val in value:
                newval.append(str(val))
            value = newval
        ret += '<select class="form-control" name="' + inputName + '" id="' + id + '"'
        if ftype == "multiselect":
            ret += ' multiple=""'
        ret += '>'
        for val in options:
            key = str(options[val])
            val = val
            ret += '<option value="' + str(val) + '"'
            if ftype == "multiselect":
                if str(val) in value:
                    ret += ' selected=""'
            elif val == value:
                ret += ' selected=""'
            ret += '>' + key + '</option>'
        ret += '</select>'
    elif ftype == "textarea":
        rows = options['rows'] if 'rows' in options else 3
        ret += '<textarea class="form-control" rows="' + str(rows) + '" name="' + inputName + '" id="' + id
        if placeholder is not None:
            ret += '" placeholder="' + placeholder
        ret += '" >' + value + '</textarea>'
    elif ftype == "radio":
        for val in options:
            ret += '<div class="radio"><label><input name="' + inputName + '" id="' + id + str(val) + '"'
            if str(value) == str(val):
                ret += ' checked=""'
            ret += ' value="' + str(val) + '" type="radio">'
            ret += str(options[val])
            ret += '</label></div>'
    if errors is not None:
        for error in errors:
            ret += '<span class="text-danger">' + error + '</span></br>'

    if innerDiv is not None:
        ret += '</div>'
    ret += '</div>'
    return Markup(ret)

def checkbox(label, inputName=None, id=None, value=None):
    if inputName is None:
        inputName = label.replace(" ", "")
    if id is None:
        id = inputName
    ret = '<div class="form-group"><div class="col-sm-10 col-sm-offset-2"><div class="checkbox">'
    ret += '<label for="' + id + '">'
    ret += '<input type="checkbox" name="' + inputName + '" id="' + id
    if value:
        ret += '" checked="checked'
    ret += '">'
    ret += label + '</label></div></div></div>'
    return Markup(ret)

def button(text, ftype="submit", cls=["btn", "btn-default"], destination=None, unique_id=None):
    classes = ' '.join(cls)
    if ftype == "link":
        ret = '<a href="' + destination + '" class="' + classes + '">' + text + '</a>'
    elif ftype == "post":
        if unique_id is None:
            unique_id = text.replace(" ", "") + destination.replace("/", "")
        ret = '<a href="' + destination + '" onclick="event.preventDefault();$(\'#' + unique_id + '\').submit()"'
        ret += ' class="' + classes + '">' + text + '</a>'
        ret += '<form id="' + unique_id + '" method="post" action="' + destination + '"></form>'
    else:
        ret = '<button type="' + ftype + '" class="' + classes + '">' + text + '</button>'
    return Markup(ret)

def active(url):
    if request.path == url:
        return "active"

def csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
    return hidden('csrf_token', session['csrf_token'])


def to_keyval(ilist, key='id', value='name', base={}):
    ret = base.copy()
    for i in ilist:
        ret[i.__getattribute__(key)] = i.__getattribute__(value)
    return ret


def to_list(ilist, value='id', base=[]):
    for i in ilist:
        base.append(i.__getattribute__(value))
    return base

def format_currency(value):
    return "${:,.2f}".format(value)

def format_date(value):
    return value.strftime(dateFormat)

def format_time(value):
    return value.strftime(timeFormat)

def format_datetime(value):
    return value.strftime(datetimeFormat)

def to_strings(ilist):
    ret = []
    for i in ilist:
        ret.append(str(i))
    return ret
