# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    if getattr(exc, "default_code", "") == "not_authenticated":
        exc.status_code = 401
    response = exception_handler(exc, context)
    if response is not None:
        error_data = response.data
        response.data = {
            "msg": error_data,
            "code": response.status_code
        }
    return response
