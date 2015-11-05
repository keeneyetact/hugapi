"""hug/types.py

Defines hugs built-in supported types / validators

Copyright (C) 2015  Timothy Edmund Crosley

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

"""
from decimal import Decimal
from json import loads as load_json


def accept(formatter, doc=None, error_text=None, cli_behaviour=None, exception_handlers=None):
    '''Allows quick wrapping any Python type converter for use with Hug type annotations'''
    defined_exception_handlers = exception_handlers or {}
    if defined_exception_handlers or error_text:
        def hug_formatter(data):
            try:
                return formatter(data)
            except Exception as exception:
                for take_exception, rewrite in defined_exception_handlers.items():
                    if isinstance(exception, take_exception):
                        if isinstance(rewrite, str):
                            raise ValueError(rewrite)
                        else:
                            raise rewrite(data)
                if error_text:
                    raise ValueError(error_text)
                raise exception
    else:
        def hug_formatter(data):
            return formatter(data)

    new_cli_behaviour = getattr(formatter, 'cli_behaviour', {})
    if cli_behaviour:
        new_cli_behaviour.update(cli_behaviour)
    if new_cli_behaviour:
        hug_formatter.cli_behaviour = new_cli_behaviour
    hug_formatter.__doc__ = doc or formatter.__doc__
    return hug_formatter


def multiple(value):
    '''Multiple Values'''
    return value if isinstance(value, list) else [value]
multiple.cli_behaviour = {'action': 'append'}


def comma_separated_list(value):
    '''Multiple values, separated by a comma'''
    return value.split(",")


number = accept(int, 'A whole number', 'Invalid whole number provided')
float_number = accept(float, 'A float number', 'Invalid float number provided')
decimal = accept(Decimal, 'A decimal number', 'Invalid decimal number provided')
text = accept(str, 'Basic text / string value', 'Invalid text value provided')
boolean = accept(bool, 'Providing any value will set this to true',
                 'Invalid boolean value provided', cli_behaviour={'action': 'store_true'})


def smart_boolean(input_value):
    '''Accepts a true or false value'''
    if type(input_value) == bool or input_value in (None, 1, 0):
        return bool(input_value)

    value = input_value.lower()
    if value in ('true', 't', '1'):
        return True
    elif value in ('false', 'f', '0', ''):
        return False

    raise KeyError('Invalid value passed in for true/false field')


def inline_dictionary(input_value):
    '''A single line dictionary, where items are separted by commas and key:value are separated by a pipe'''
    return {key.strip(): value.strip() for key, value in (item.split(":") for item in input_value.split("|"))}


def one_of(values):
    '''Ensures the value is within a set of acceptable values'''
    def matches(value):
        if not value in values:
            raise KeyError('Invalid value passed. The accepted values are: ({0})'.format("|".join(values)))
        return value

    matches.__doc__ = 'Accepts one of the following values: ({0})'.format("|".join(values))
    matches.cli_behaviour = {'choices': values}
    return matches


def mapping(value_map):
    '''Ensures the value is one of an acceptable set of values mapping those values to a Python equivelent'''
    values = value_map.keys()
    def matches(value):
        if not value in value_map.keys():
            raise KeyError('Invalid value passed. The accepted values are: ({0})'.format("|".join(values)))
        return value_map[value]

    matches.__doc__ = 'Accepts one of the following values: ({0})'.format("|".join(values))
    matches.cli_behaviour = {'choices': values}
    return matches


def json(value):
    '''Accepts a JSON formatted data structure'''
    if type(value) in (str, bytes):
        try:
            return load_json(value)
        except Exception:
            raise ValueError('Incorrectly formatted JSON provided')
    else:
        return value


def multi(*types):
    '''Enables accepting one of multiple type methods'''
    type_strings = (type_method.__doc__ for type_method in types)
    doc_string = 'Accepts any of the following value types:{0}\n'.format('\n  - '.join(type_strings))
    def multi_type(value):
        for type_method in types:
            try:
                return type_method(value)
            except:
                pass
        raise ValueError(doc_string)
    multi_type.__doc__ = doc_string
    return multi_type
