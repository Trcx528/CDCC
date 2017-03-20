import re
from functools import wraps
from flask import request, g, redirect, session, abort
from app.models import User


_validators = {}


def validate(csrf_protection=True, methods=['POST'], **params):
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            if request.method not in methods:
                return func(*args, **kwargs)
            valErrors = {}
            g.data = {}
            g.errors = {}
            g.hasErrors = False
            if csrf_protection:
                token = session.pop('csrf_token', None)
                if not token or token != request.form['csrf_token']:
                    abort(400)
            for field in params:
                valType = params[field].split('|', 1)[0]
                ruleparams = {'fieldName': field}
                if len(params[field].split("|", 1)) > 1:
                    for param in params[field].split('|', 1)[1].split('|'):
                        rulekey = param.split('=')[0]
                        rulevalue = True
                        if len(param.split('=')) == 2:
                            rulevalue = param.split('=')[1]
                        ruleparams[rulekey] = rulevalue
                error = None
                if valType == "multiselect":
                    fieldVal = [] if field not in request.form else request.form.getlist(field)
                else:
                    fieldVal = "" if field not in request.form else request.form[field]
                    # for key in request.form:
                    #     if key.startswith(field):
                    #         fieldVal = request.form[key]
                if valType in _validators:
                    g.data[field], error = _validators[valType](fieldVal, **ruleparams)
                if error is not None and (len(error) > 0):
                    valErrors[field] = error
            if len(valErrors) > 0:
                # redirect to a get and repopulate with the original data + errors
                session["validationErrors"] = valErrors
                session["validationData"] = g.data
                return redirect(request.referrer)
            rparams = {}
            for var in func.__code__.co_varnames:
                lvar = var.lower()
                for kvar in kwargs:
                    if lvar == kvar.lower():
                        rparams[var] = kwargs[kvar]
                for kvar in g.data:
                    if lvar == kvar.lower():
                        rparams[var] = g.data[kvar]
            return func(*args, **rparams)
        return decorator
    return wrapper


def registerValidator(type, func):
    _validators[type] = func


def commonValidation(name, value, required=False, matches=None):
    errors = []
    if required:
        if value is None or value == "":
            errors.append("Required")
    if matches is not None:
        if request.form[matches] != value:
            errors.append("Does not match %s" % matches)
    return errors


def valEmail(value, fieldName=None, dbunique=False, **commonArgs):
    errors = commonValidation(fieldName, value, **commonArgs)
    if not re.match("[^@]+@[^@]+.[^@]+", value):
        errors.append("Invalid Email Format")
    if dbunique:
        count = User.select().where(User.emailAddress == value).count()
        if count > 0:
            errors.append("Email already in use")
    return value, errors


def valString(value, fieldName=None, maxlength=None, minlength=0, **commonArgs):
    errors = commonValidation(fieldName, value, **commonArgs)
    value = "" if value is None else value
    if maxlength is not None:
        if len(value) > int(maxlength):
            errors.append("Exceeds Max Length (%s)" % maxlength)
    if len(value) < int(minlength):
        errors.append("Too Short (%s)" % minlength)
    return value, errors


def valInt(value, fieldName=None, max=None, min=None, **commonArgs):
    errors = commonValidation(fieldName, value, **commonArgs)
    if value != "" and value is not None:
        value = int(value)
        if max is not None:
            if value > int(max):
                errors.append("Must be less than %s" % max)
        if min is not None:
            if value < int(min):
                errors.append("Must be greater than %s" % min)
    else:
        if len(errors) == 0:
            errors.append("Failed to parse")
    return value, errors


def valFloat(value, fieldName=None, max=None, min=None, **commonArgs):
    errors = commonValidation(fieldName, value, **commonArgs)
    if value != "" and value is not None:
        value = float(value)
        if max is not None:
            if value > float(max):
                errors.append("Must be less than %s" % max)
        if min is not None:
            if value < float(min):
                errors.append("Must be greater than %s" % min)
    else:
        if len(errors) == 0:
            errors.append("Failed to parse")
    return value, errors

def valMutliSelect(value, fieldName=None, minSelect=0, maxSelect=None, **commonArgs):
    errors = commonValidation(value, fieldName, **commonArgs)
    if len(value) < int(minSelect):
        errors.append("Too Few Selections")
    if maxSelect is not None:
        if len(value) > int(maxSelect):
            errors.append("Too Many Selections")
    return value, errors


def valBool(value, fieldName=None, **commonArgs):
    errors = commonValidation(value, fieldName, **commonArgs)
    return value == "on", errors


def valCurrency(value, **args):
    value = value.replace("$", "")
    return valFloat(value, **args)

def valPhone(value, fieldName=None, minlength=10, **commonArgs):
    errors = commonValidation(value, fieldName, **commonArgs)
    value = value.replace("(", "").replace(")", "").replace(" ", "").replace("-", "").lower()
    if value is None or value.replace("x", "") is "":
        return value, errors
    if not value.replace("x", "").isnumeric():
        errors.append("Invalid Format")
    if not len(value.replace("x", "")) >= minlength:
        errors.append("Phone Number Too Short")
    area, block, num, ext = "", "", "", ""
    if value.startswith("1"):
        area = value[:4] + " "
        value = value[4:]
    else:
        area = "(" + value[:3] + ") "
        value = value[3:]
    block = value[:3] + "-"
    value = value[3:]
    num = value[:4]
    value = value[4:]
    if len(value) > 0:
        ext = " x" + value.replace("x", "")
    return area + block + num + ext, errors




registerValidator("str", valString)
registerValidator("string", valString)
registerValidator("int", valInt)
registerValidator("email", valEmail)
registerValidator("check", valBool)
registerValidator("multiselect", valMutliSelect)
registerValidator("decimal", valFloat)
registerValidator("currency", valCurrency)
registerValidator("phone", valPhone)
