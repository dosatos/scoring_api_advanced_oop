#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
from dateutil.relativedelta import relativedelta
import logging
import hashlib
import uuid
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from scoring import get_score, get_interests
from store import Store


SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
INSUFFICIENT_ARG_PAIRS_MESSAGE = "least required pairs: (phone, email), (first_name, last_name), (gender, birthday)"
INVALID_ARGS_MESSAGE = "Invalid arguments: "
ALLOWED_METHODS = ["online_score", "client_interests"]



class BaseField(object):

    value = None

    def __init__(self, required=False, nullable=True):
        self.required = required
        self.nullable = nullable

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = None
        self._validate_required(value)
        if value is None:
            return
        self._validate_nullable(value)
        self._validate(value)
        if not self.value:
            self.value = value

    def _validate(self, value):
        pass

    def _validate_required(self, value):
        if self.required and value is None:
            log_errors("A required field is missing")
            raise ValueError

    def _validate_nullable(self, value):
        if not self.nullable and value in ["", " "]:
            log_errors("A field is not nullable")
            raise ValueError



class CharField(BaseField):
    def _validate(self, value):
        if not isinstance(value, (str, unicode)):
            log_errors("{self.__class__.__name__} is incorrect".format(self=self))
            raise TypeError


class EmailField(CharField):
    def _validate(self, value):
        super(EmailField, self)._validate(value)
        value = str(value).strip()
        if not value:
            return
        lacks_at_symbol = len(value.split("@")) != 2
        if lacks_at_symbol:
            log_errors("Incorrect email, ValueError, missing @")
            raise ValueError


class PhoneField(CharField):
    def _validate(self, value):
        super(PhoneField, self)._validate(value)
        value = str(value).strip()
        if not value:
            return
        length_is_11 = len(value) == 11
        starts_with_7 = value.startswith("7")
        if not (length_is_11 and starts_with_7):
            log_errors("Incorrect phone")
            raise ValueError
        return



class ArgumentsField(BaseField):
    def _validate(self, value):
        if not isinstance(value, dict):
            log_errors("Incorrect arguments, should be dict".format(self=self))
            raise TypeError



class DateField(CharField):
    def _validate(self, value):
        super(DateField, self)._validate(value)
        value = str(value).strip()
        if not value:
            return
        try:
            self.value = datetime.datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            log_errors("Incorrect data format, should be dd.mm.yyyy")
            raise ValueError



class BirthDayField(DateField):
    def _validate(self, value):
        super(BirthDayField, self)._validate(value)
        value = str(value).strip()
        if not value:
            return
        seventy_years_ago = datetime.datetime.now() - relativedelta(years=70)
        if datetime.datetime.strptime(value, '%d.%m.%Y') < seventy_years_ago:
            log_errors("The system supports only 70 year ages only")
            raise ValueError



class GenderField(BaseField):
    def _validate(self, value):
        if not isinstance(value, int) and value is not None:
            log_errors("TypeError, gender input. should be 0, 1, 2")
            raise ValueError
        if value not in [0, 1, 2, None]:
            log_errors("ValueError, gender input. should be 0, 1, 2")
            raise TypeError



class ClientIDsField(BaseField):
    def _validate(self, value):
        if isinstance(value, list):
            if len(filter(int, value)) == len(value):
                return
        log_errors("Wrong client id input")
        raise TypeError



class BaseRequest(object):
    def __init__(self, data):
        self.invalid_fields = []
        self.has_fields = []
        class_attribute_fields = [(key, field) for key, field in self.__class__.__dict__.iteritems()
                                    if not key.startswith("__")
                                    and isinstance(field, BaseField)]
        for attribute, field in class_attribute_fields:
            try:
                setattr(self, attribute, data.get(attribute))
                self.has_fields.append(attribute)
            except (TypeError, ValueError), e:
                # to send the errors to the api users
                self.invalid_fields.append(attribute)


    def is_valid(self):
        return len(self.invalid_fields)



class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    @property
    def has_client_ids(self):
        return self.client_ids is not None and self.client_ids != []

    @property
    def has_date(self):
        return self.date is not None and self.date != ""

    def is_valid(self):
        super(ClientsInterestsRequest, self).is_valid()



class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    @property
    def has_first_name(self):
        return self.first_name not in [None, ""]

    @property
    def has_last_name(self):
        return self.last_name not in [None, ""]

    @property
    def has_email(self):
        return self.email not in [None, ""]

    @property
    def has_phone(self):
        return self.phone not in [None, ""]

    @property
    def has_birthday(self):
        return self.birthday not in [None, ""]

    @property
    def has_gender(self):
        return self.gender is not None

    def is_valid(self):
        super(OnlineScoreRequest, self).is_valid()
        if not any([self.has_first_name and self.has_last_name,
                    self.has_birthday and self.has_gender,
                    self.has_phone and self.has_email]):
            return False
        return True



class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN



class Response(object):
    def __init__(self, method_request, context, store):
        self.context = context
        self.store = store
        self.response = None
        self.code = None
        self.set_response(method_request)

    def get_response(self):
        return self.response, self.code

    def set_response(self, method_request):
        if method_request.is_valid():
            self.response, self.code = "{}{}".format(INVALID_ARGS_MESSAGE, ", ".join(method_request.invalid_fields)), api.INVALID_REQUEST
        elif method_request.method not in ALLOWED_METHODS:
            self.response, self.code = ERRORS[INVALID_REQUEST], INVALID_REQUEST
        else:
            self.process(method_request)

    def get_score_from_request(self, request, is_admin):

        phone = request.phone
        email = request.email
        birthday = request.birthday
        gender = request.gender
        first_name = request.first_name
        last_name = request.last_name

        if is_admin:
            return 42
        return get_score(self.store, phone, email,
                         birthday=birthday, gender=gender,
                         first_name=first_name, last_name=last_name)

    def get_interests_from_request(self, method_request):
        return {i: get_interests(self.store, i) for i in method_request.client_ids}

    def process(self, method_request):
        if method_request.method == "online_score":
            request = OnlineScoreRequest(method_request.arguments)
            if request.invalid_fields:
                self.response, self.code = "{}{}".format(INVALID_ARGS_MESSAGE, ",- ".join(request.invalid_fields)), INVALID_REQUEST
            elif not request.is_valid():
                self.response, self.code = INSUFFICIENT_ARG_PAIRS_MESSAGE, INVALID_REQUEST
            else:
                self.response, self.code = {"score": self.get_score_from_request(request, method_request.is_admin)}, OK
                self.context['has'] = request.has_fields
        elif method_request.method == "client_interests":
            request = ClientsInterestsRequest(method_request.arguments)
            if request.is_valid():
                self.response, self.code = "{}{}".format(INVALID_ARGS_MESSAGE, ", ".join(request.invalid_fields)), INVALID_REQUEST
            else:
                self.response, self.code = self.get_interests_from_request(request), OK
                self.context['nclients'] = len(request.client_ids)


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, context, store):
    method_request = MethodRequest(request)
    response, code = Response(method_request, context, store).get_response()
    return response, code



class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = Store()

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return



def log_errors(message):
    print message
    # op = OptionParser()
    # op.add_option("-p", "--port", action="store", type=int, default=8080)
    # op.add_option("-l", "--log", action="store", default=None)
    # (opts, args) = op.parse_args()
    # if opts.log:
    #     logging.info(message)
    # else:
    #     print message


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
