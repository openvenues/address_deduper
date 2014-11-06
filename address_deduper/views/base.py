import flask
import ujson

import six

from werkzeug.exceptions import default_exceptions, HTTPException

flask.json = json = ujson

from flask import url_for, request, Response, Blueprint, abort

from functools import wraps

view_registry = {}

class ViewMeta(type):
    def __init__(cls, name, bases, dict_):
        super(ViewMeta, cls).__init__(name, bases, dict_)

        if 'abstract' not in dict_:
            cls.abstract = False
            assert hasattr(cls, 'blueprint'), 'BaseView subclasses must define blueprint'
            view_registry[name] = cls

        for name, value in dict_.iteritems():
            if hasattr(value, 'rule'):
                func = cls.wrap_function(value)
                cls.blueprint.add_url_rule(value.rule, name, func, **value.options)


class BaseView(object):
    abstract = True
    
    __metaclass__ = ViewMeta
    
    delete_response = {'status': 200, 'message': 'OK', 'deleted': True}, 200
    success_response = {'status': 200, 'message': 'OK'}, 200
    
    def url_for(self, resource, **values):
        """Generates a URL to the given resource."""
        return url_for(resource.endpoint, **values)

    @classmethod
    def wrap_function(cls, func):
        @wraps(func)
        def wrapper(*args, **kw):
            return func(cls, *args, **kw)
        return wrapper

def unpack(value):
    if not isinstance(value, tuple):
        return value, 200, {}

    if len(value) == 2:
        data, code = value
        return data, code, {}
    elif len(value) == 3:
        data, code, headers = value
        return data, code, headers
    
    return value, 200, {}

def route(rule, **options):

    def with_func(f):
        f.rule = rule
        f.options = options  
        return f
    return with_func

JSON_MIME_TYPE = 'application/json'

def jsonify(d, status_code=200, headers=None):
    return Response(json.dumps(d), mimetype=JSON_MIME_TYPE, headers=headers or {}, status=str(status_code))

def handle_http_error(exc):
    response = jsonify({'message': six.text_type(exc)})
    response.status_code = exc.code if isinstance(exc, HTTPException) else 500
    return response

def add_error_handlers(app):
    @app.errorhandler(ModelConversionError)
    def handle_model_conversion(error):
        return jsonify({
            'message': error.message
            }, 
            status_code=401)

    for code in default_exceptions:
        app.error_handler_spec[None][code] = handle_http_error
    return app
