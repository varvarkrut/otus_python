#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABC

from scoring import get_score
from scoring import get_interests
import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer

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


class AbstractField(abc.ABC):
    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable

    def validate(self, value):
        raise NotImplementedError


class CharField(AbstractField):
    def __init__(self, required=False, nullable=True):
        super().__init__(required, nullable)

    def validate(self, value):
        if not self.nullable and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if self.required and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if not value:
            return value
        if not isinstance(value, str):
            raise ValueError("Value must be string")
        else:
            return value


class ArgumentsField(AbstractField):
    def __init__(self, required=False, nullable=False):
        super().__init__(required, nullable)

    def validate(self, value):
        if not self.nullable and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if self.required and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if not value:
            return value
        if not isinstance(value, dict):
            raise ValueError("Arguments error. Value must be dict")
        else:
            return value


class EmailField(AbstractField):
    def __init__(self, required=False, nullable=False):
        super().__init__(required, nullable)

    def validate(self, value):
        if not self.nullable and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if self.required and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if not value:
            return value
        if not isinstance(value, str):
            raise ValueError("Email field validate error. Value must be string")
        if "@" not in value:
            raise ValueError("Email field validate error. Value must be email")
        else:
            return value


class PhoneField(AbstractField):
    def __init__(self, required=False, nullable=False):
        super().__init__(required, nullable)

    def validate(self, value):
        if not self.nullable and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if self.required and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if not value:
            return value
        if len(str(value)) != 11:
            raise ValueError("Phone field validate error. Value must be 11 digits")
        if not str(value).isdigit():
            raise ValueError("Phone field validate error. Value must be digits")
        if str(value)[0] != "7":
            raise ValueError("Phone field validate error. Value must be start with 7")
        else:
            return str(value)


class DateField(AbstractField):
    def __init__(self, required=False, nullable=False):
        super().__init__(required, nullable)

    def validate(self, value):
        if not self.nullable and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if self.required and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if not value:
            return value
        if not isinstance(value, str):
            raise ValueError("Value must be string")
        try:
            datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError as e:
            raise ValueError("Date field validate error. Value must be date") from e
        else:
            return value


class BirthDayField(AbstractField):
    def __init__(self, required=False, nullable=False):
        super().__init__(required, nullable)

    def validate(self, value):
        if not self.nullable and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if self.required and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if not value:
            return value
        if not isinstance(value, str):
            raise ValueError("Birthday field validate error. Value must be string")
        try:
            date = datetime.datetime.strptime(value, "%d.%m.%Y")
            if date > datetime.datetime.now():
                raise ValueError("Birthday field validate error. Value must be date")

            delta = datetime.datetime.now() - date
            if delta.days > 25550:
                raise ValueError(
                    "Birthday field validate error. The delta cannot be more than 70 years"
                )
        except ValueError as e:
            raise ValueError("Birth day field validate error.") from e
        else:
            return value


class GenderField(AbstractField):
    def __init__(self, required=False, nullable=False):
        super().__init__(required, nullable)

    def validate(self, value):
        if not self.nullable and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if self.required and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if not value:
            return value
        GENDERS = {
            0: "unknown",
            1: "male",
            2: "female",
        }
        if value not in GENDERS:
            raise ValueError("Gender field validate error. Value must be 0, 1 or 2")

        else:
            return value


class ClientIDsField(AbstractField):
    def __init__(self, required=False, nullable=False):
        super().__init__(required, nullable)

    def validate(self, value):
        if not self.nullable and value is None:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if self.required and value is None or not value:
            raise ValueError(f"{type(self).__name__} Value must be not None")
        if not isinstance(value, list):
            raise ValueError("Value must be list")
        if len(value) != 0:
            for i in value:
                if not isinstance(i, int):
                    raise ValueError("Value must be int")

        return value


class MetaRequest(type):
    def __init__(self, name, bases, dct):
        super(MetaRequest, self).__init__(name, bases, dct)
        self.fields = []
        for key, attr in dct.items():
            if isinstance(attr, AbstractField):
                attr.name = key
                self.fields.append(attr)


class ClientsInterestsRequest(metaclass=MetaRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def __init__(self, request, context):
        self.request = request
        self.is_admin = False
        self.interests = {}
        self._errors = False
        context["nclients"] = 0
        for field in self.fields:
            try:
                setattr(self, field.name, field.validate(request.get(field.name)))
            except ValueError as e:
                self._errors = True
                self.errors = e

        try:
            context["nclients"] = len(self.client_ids)
        except TypeError as exc:
            context["nclients"] = 0

    def process_request(self, is_admin=False):
        if self._errors:
            return str(self.errors), INVALID_REQUEST
        clients_interests = {
            client_id: get_interests(cid=client_id) for client_id in self.client_ids
        }
        return clients_interests, OK


class OnlineScoreRequest(metaclass=MetaRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, request, ctx):
        self.response = None
        self.status_code = None
        self.errors = None
        self._errors = None
        ctx["has"] = []
        for field in self.fields:
            try:
                if request.get(field.name) is not None:
                    ctx["has"].append(field.name)
                setattr(self, field.name, field.validate(request.get(field.name)))
            except ValueError as e:
                self._errors = True
                self.errors = e

    def process_request(self, is_admin=False):
        self._validate_request()
        if is_admin:
            self.response = {"score": 42}
            return self.response, OK
        if self._errors:
            self.status_code = INVALID_REQUEST
            self.response = str(self.errors)
            return self.response, self.status_code

        self.response = {
            "score": get_score(
                phone=self.phone,
                email=self.email,
                birthday=self.birthday,
                gender=self.gender,
                first_name=self.first_name,
                last_name=self.last_name,
            )
        }

        if self.response is None:
            self.status_code = INTERNAL_ERROR
            self.response = "Internal error"

        else:
            self.status_code = OK

        return self.response, self.status_code

    def _validate_request(self):
        valid_pairs = (
            (self.first_name, self.last_name),
            (self.phone, self.email),
            (self.gender, self.birthday),
        )
        for pair in valid_pairs:
            if pair[0] is not None and pair[1] is not None:
                return
        self._errors = True
        self.errors = "at least one pair of fields must be filled"


class MethodRequest(metaclass=MetaRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    def __init__(self, request, ctx):
        self.ctx = ctx
        self.errors = None
        self._errors = False
        self.request_body = request["body"]
        for field in self.fields:
            try:
                setattr(
                    self, field.name, field.validate(self.request_body.get(field.name))
                )
            except ValueError as e:
                self._errors = True
                self.errors = e

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    def process_request(self):
        if self._errors:
            return str(self.errors), INVALID_REQUEST
        request_method = self.method
        if not check_auth(self.request_body):
            return "Forbidden", FORBIDDEN
        if request_method == "online_score":
            method_request = OnlineScoreRequest(self.arguments, self.ctx)
        elif request_method == "clients_interests":
            method_request = ClientsInterestsRequest(self.arguments, self.ctx)
        else:
            return {"code": INVALID_REQUEST, "response": {"error": "Invalid method"}}
        return method_request.process_request(self.is_admin)


def check_auth(request):
    if request.get("login", "") == ADMIN_LOGIN:
        digest = hashlib.sha512(
            (datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode()
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            (request["account"] + request["login"] + SALT).encode()
        ).hexdigest()
    if digest == request["token"]:
        return True
    return False


def method_handler(request, ctx, store):
    method_request = MethodRequest(request, ctx)
    response, code = method_request.process_request()
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {"method": method_handler}
    store = None

    def get_request_id(self, headers):
        return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context, self.store
                    )
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
        binary_response = json.dumps(r).encode("utf-8")
        self.wfile.write(binary_response)
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
