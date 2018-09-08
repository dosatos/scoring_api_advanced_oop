#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

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


class BaseField(object):
    def __init__(self, required=False, nullable=True):
        self.value = None
        self.required = required
        self.nullable = nullable

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = value
        if self.required and self.value == None:
            raise ValueError("{instance} is a mandatory field".format(instance=instance))
        if self.nullable and self.value == "":
            raise ValueError("{instance} cannot be blank".format(instance=instance))
        self._validate()

    def _validate(self):
        pass



class CharField(BaseField):
    def _validate(self):
        pass


class ArgumentsField(BaseField):
    pass


class EmailField(CharField):
    pass


class PhoneField(BaseField):
    pass


class DateField(BaseField):
    pass


class BirthDayField(BaseField):
    pass


class GenderField(BaseField):
    pass


class ClientIDsField(BaseField):
    pass



class BaseRequest(object):
    def __init__(self, request):
        body = request['body']
        arguments = body['arguments']
        self.fields = []
        for argument, value in arguments.items():
            setattr(self, argument, value)
            if value is not None:
                self.fields.append(argument)

        account = body['account']
        login = body['login']
        token = body['token']

    def is_valid(self):
        names_pair = len(set(['phone', 'email']).intersection(self.request.fields)) == 2
        gender_birthday_pair = len(set(['first_name', 'last_name']).intersection(self.request.fields)) == 2
        phone_email_pair = len(set(['gender', 'birthday']).intersection(self.request.fields)) == 2
        if not any(names_pair, gender_birthday_pair, phone_email_pair):
            return False
        return True




# class ClientsInterestsRequest(object):
#     client_ids = ClientIDsField(required=True)
#     date = DateField(required=False, nullable=True)



class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)



# class MethodRequest(BaseRequest):
#     account = CharField(required=False, nullable=True)
#     login = CharField(required=True, nullable=True)
#     token = CharField(required=True, nullable=True)
#     arguments = ArgumentsField(required=True, nullable=True)
#     method = CharField(required=True, nullable=False)
#
#     @property
#     def is_admin(self):
#         return self.login == ADMIN_LOGIN



class Response(object):
    def __init__(self, request):
        self.request = request

    def generate_response(self):
        if self.request.is_valid():
            response = {"score": 1.0}
            code = 200
            return response, code
        response = "least required pairs: (phone, email), (first_name, last_name), (gender, birthday)"
        code = 400
        return response, code


# - phone-email
# - first name - last name
# - gender - birthday



def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, context, store):
    if request['body']['method'] == "online_score":
        r = OnlineScoreRequest(request)
    elif request['body']['method'] == "clients_interests":
        pass
    response, code = Response(r).generate_response()
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
