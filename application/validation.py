from werkzeug.exceptions import HTTPException
from flask import make_response
import json

class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)

class DuplicationError(HTTPException):
    def __init__(self, status_code, mess):
        self.response = make_response(mess, status_code)

class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_description": error_message}
        self.response = make_response(json.dumps(message), status_code) 

class NotAuthorizedError(HTTPException):
    def __init__(self, status_code, error_message):
        self.response = make_response(error_message, status_code)