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



class BaseField(object):

    value = None

    def __init__(self, required=False, nullable=True):
        self.required = required
        self.nullable = nullable

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        if value is not None and isinstance(self.value, (str, unicode)):
            self.value = str(value).strip()
        else:
            self.value = value
        self._validate_required()
        self._validate_nullable()
        self._validate()

    def _validate(self):
        pass

    def _validate_required(self):
        # print "required: ", self.required, self.value
        if self.required and self.value is None:
            log_errors("A required field is missing")
            raise ValueError

    def _validate_nullable(self):
        # print "nullable: ", self.nullable, self.value
        if not self.nullable and self.value is "":
            log_errors("A field is not nullable")
            raise ValueError



class CharField(BaseField):
    def _validate(self):
        if not isinstance(self.value, (str, unicode)) and self.value is not None:
            log_errors("{self.__class__.__name__} is incorrect".format(self=self))
            raise TypeError
        self.additional_validation()

    def additional_validation(self):
        pass



class EmailField(CharField):
    def additional_validation(self):
        if self.value:
            lacks_at_symbol = len(self.value.split("@")) != 2
            if lacks_at_symbol:
                log_errors("Incorrect email, ValueError, missing @")
                raise ValueError



class PhoneField(CharField):
    def additional_validation(self):
        if self.value:
            length_is_11 = len(self.value) == 11
            starts_with_7 = str(self.value).startswith("7")
            if length_is_11 and starts_with_7:
                return
            log_errors("Incorrect phone")
            raise TypeError



class ArgumentsField(BaseField):
    def _validate(self):
        if not isinstance(self.value, dict):
            log_errors("Incorrect arguments, should be dict".format(self=self))
            raise TypeError



class DateField(BaseField):
    def _validate(self):
        if not self.value:
            return
        try:
            datetime.datetime.strptime(self.value, '%d.%m.%Y')
        except TypeError:
            log_errors("Incorrect data format, should be dd.mm.yyyy")
            raise TypeError
        self._validate_age(70)

    def _validate_age(self, age):
        pass



class BirthDayField(DateField):
    def _validate_age(self, age):
        seventy_years_ago = datetime.datetime.now() - relativedelta(years=70)
        if datetime.datetime.strptime(self.value, '%d.%m.%Y') < seventy_years_ago:
            log_errors("The system supports only 70 year ages only")
            raise TypeError



class GenderField(BaseField):
    def _validate(self):
        if isinstance(self.value, int) and self.value in [1, 2]:
            return
        if self.value in [None, 0, ""]:
            self.value = 0
            return
        log_errors("Wrong gender input. should be 0, 1, 2")
        raise TypeError



class ClientIDsField(BaseField):
    def _validate(self):
        if isinstance(self.value, list) or self.value is None:
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
                # if attribute != "method":
                #     continue
                # print "Started for: ", attribute
                setattr(self, attribute, data.get(attribute, None))
            except (TypeError, ValueError), e:
                # to send the errors to the api users
                self.invalid_fields.append(attribute)
                # print(self.invalid_fields)
            if attribute in data and data[attribute]:
                self.has_fields.append(attribute)


    def is_valid(self):
        pass



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
        return True



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
    def __init__(self, store):
        self.store = store

    def generate_response(self):
        used_method = self.store['used_method']
        if not check_auth(self.store['request']):
            response, code = "Forbidden", 403
        elif used_method.invalid_fields:
            response, code = "{}{}".format(INVALID_ARGS_MESSAGE, ", ".join(used_method.invalid_fields)), INVALID_REQUEST
        elif not used_method.is_valid():
            response, code = INSUFFICIENT_ARG_PAIRS_MESSAGE, BAD_REQUEST
        else:
            if isinstance(used_method, OnlineScoreRequest):
                response, code = {"score": self.get_score_from_request()}, OK
            elif isinstance(used_method, ClientsInterestsRequest):
                response, code = self.get_interests_from_request(), OK
        return response, code

    def get_score_from_request(self):
        phone, email = self.store['used_method'].phone, self.store['used_method'].email
        birthday, gender = self.store['used_method'].birthday, self.store['used_method'].gender
        first_name, last_name = self.store['used_method'].first_name, self.store['used_method'].last_name
        if self.store['is_admin']:
            return 42
        return get_score(self.store, phone, email,
                         birthday=birthday, gender=gender,
                         first_name=first_name, last_name=last_name)

    def get_interests_from_request(self):
        return {i: get_interests(self.store, i) for i in self.store['used_method'].client_ids}



def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, context, store):
    store = {
        'request': MethodRequest(request['body']),
        'is_admin': False,
    }
    if store['request'].method == "online_score":
        store['used_method'] = OnlineScoreRequest(store['request'].arguments)
        context['has'] = store['used_method'].has_fields
    elif store['request'].method == "clients_interests":
        store['used_method'] = ClientsInterestsRequest(store['request'].arguments)
        context['nclients'] = len(store['used_method'].client_ids)

    response, code = Response(store).generate_response()
    return response, code



class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

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
