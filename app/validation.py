import re
from datetime import datetime, date
from functools import wraps
from flask import request, g, redirect, session, abort
from app.models import User

datetimeFormat = "%m/%d/%Y %I:%M %p"
dateFormat = "%m/%d/%Y"
timeFormat = "%I:%M %p"

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
                            if rulevalue.startswith('<') and rulevalue.endswith('>'):
                                if rulevalue.replace('<', '').replace('>', '') in kwargs:
                                    rulevalue = kwargs[rulevalue.replace('<', '').replace('>', '')]
                        ruleparams[rulekey] = rulevalue
                error = None
                valContainer = request.args if request.method == "GET" else request.form
                if valType == "multiselect":
                    fieldVal = [] if field not in valContainer else valContainer.getlist(field)
                else:
                    fieldVal = "" if field not in valContainer else valContainer[field]
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
        if "" if matches not in request.form else request.form[matches] != value:
            errors.append("Does not match %s" % matches)
    return errors


def valUserEmail(value, fieldName=None, userid=None, **commonArgs):
    value, errors = valEmail(value, fieldName, **commonArgs)
    if userid:
        count = User.select().where((User.emailAddress == value) & (User.id != userid)).count()
    else:
        count = User.select().where(User.emailAddress == value).count()
    if count > 0:
        errors.append("Email already in use")
    return value, errors


def valEmail(value, fieldName=None, dbunique=None, **commonArgs):
    errors = commonValidation(fieldName, value, **commonArgs)
    # allow for blank email address, that is handled by the common required directive
    if value == "":
        return value, errors
    if not re.match("[^@]+@[^@]+.[^@]+", value):
        errors.append("Invalid Email Format")
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
    value = value.replace("$", "").replace(',', '')
    return valFloat(value, **args)

def valPercent(value, **args):
    value = value.replace("%", "")
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


def valUserPassword(value, fieldName=None, userid=None, admin=False, **commonArgs):
    errors = commonValidation(value, fieldName, **commonArgs)
    if userid == None:
        userid = session["user"]
    else:
        userid = int(userid)
    if not g.User.isAdmin or admin is False:
        user = User.select().where(User.id == userid).get()
        if not user.checkPassword(value):
            errors.append("Invalid Password")
    return value, errors

def valDate(value, fieldName=None, before=None, **commonArgs):
    errors = commonValidation(value, fieldName, **commonArgs)
    if value is not None and value is not "":
        try:
            value = datetime.strptime(value, dateFormat)
        except ValueError:
            errors.append("Invalid Format")
    else:
        return None, errors
    if before is not None:
        if before in request.form:
            try:
                bdate = datetime.strptime(request.form[before], dateFormat)
                if value > bdate:
                    errors.append("Date is too late")
            except ValueError:
                pass
    if len(errors) > 0:
        if isinstance(value, date):
            value = value.strftime(dateFormat)
    return value, errors


def valDateTime(value, fieldName=None, before=None, **commonArgs):
    errors = commonValidation(value, fieldName, **commonArgs)
    try:
        value = datetime.strptime(value, datetimeFormat)
    except ValueError:
        errors.append("Invalid Format")
    if before is not None:
        if before in request.form:
            try:
                bdate = datetime.strptime(request.form[before], datetimeFormat)
                if value > bdate:
                    errors.append("Date is too late")
            except ValueError:
                pass
    if len(errors) > 0:
        if isinstance(value, datetime):
            value = value.strftime(datetimeFormat)
    return value, errors


def valList(value, fieldName=None, type=None, **commonArgs):
    errors = commonValidation(value, fieldName, **commonArgs)
    if type == 'int':
        value = value.replace('[', '').replace(']', '').replace(' ', '').replace("'", '').split(',')
        tmp = []
        for val in value:
            tmp.append(int(val))
        value = tmp
    else:
        raise ValueError('Type %s is not supported' % type)
    return value, errors

def valDimensions(value, fieldName=None, **commonArgs):
    errors = commonValidation(value, fieldName, **commonArgs)
    dimensions = value.replace("'", '').split('x')
    valid = True
    tmp = []
    if len(dimensions) == 3:
        for dim in dimensions:
            if dim.strip().isnumeric():
                tmp.append(dim.strip() + "'")
    else:
        valid = False
    if not valid:
        errors.append("Invalid Format")
    else:
        value = ' x '.join(tmp)
    return value, errors

registerValidator("str", valString)
registerValidator("string", valString)
registerValidator("int", valInt)
registerValidator("email", valEmail)
registerValidator("check", valBool)
registerValidator("multiselect", valMutliSelect)
registerValidator("decimal", valFloat)
registerValidator("currency", valCurrency)
registerValidator("percent", valPercent)
registerValidator("phone", valPhone)
registerValidator("userPassword", valUserPassword)
registerValidator("userEmail", valUserEmail)
registerValidator("date", valDate)
registerValidator("datetime", valDateTime)
registerValidator("list", valList)
registerValidator('dimensions', valDimensions)
