import string
import random
from flask import Markup, g, session

def value_for(name):
    if hasattr(g, "data"):
        if name in g.data:
            return g.data[name]
    return ""


def form_group(ftype, label, inputName=None, placeholder=None, id=None, value=None, options={}, errors=[],
               innerDiv=["col-sm-10"]):
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

    if ftype == "text" or ftype == "password":
        ret += '<input class="form-control" name="' + inputName + '" type="' + ftype + '" id="' + id + '"'
        if value is not None:
            ret += ' value="' + value + '"'
        if placeholder is not None:
            ret += ' placeholder="' + placeholder + '"'
        ret += '>'
    elif ftype == "select" or ftype == "multiselect":
        ret += '<select class="form-control" name="' + inputName + '" id="' + id + '"'
        if ftype == "multiselect":
            ret += ' multiple=""'
        ret += '>'
        for val in options:
            key = str(options[val])
            val = str(val)
            ret += '<option value="' + val + '"'
            if ftype == "multiselect":
                if val in value:
                    ret += ' selected=""'
            elif val == value:
                ret += ' selected=""'
            ret += '>' + key + '</option>'
        ret += '</select>'
    elif ftype == "textarea":
        rows = options['rows'] if 'rows' in options else 3
        ret += '<textarea class="form-control" rows="' + str(rows) + '" name="' + inputName + '" id="' + id + '">'
        ret += value + '</textarea>'
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


def button(text, ftype="submit", cls=["btn", "btn-default"], destination=None):
    classes = ' '.join(cls)
    if ftype == "link":
        ret = '<a href="' + destination + '" class="' + classes + '">' + text + '</a>'
    else:
        ret = '<button type="' + ftype + '" class="' + classes + '">' + text + '</button>'
    return Markup(ret)


def csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
    retVal = Markup('<input type="hidden" name="csrf_token" value="' + session['csrf_token'] + '">')
    return retVal