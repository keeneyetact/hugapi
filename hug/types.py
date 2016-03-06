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
import uuid as hug_uuid
from decimal import Decimal
from json import loads as load_json

from hug.exceptions import InvalidTypeData


class Type(object):
    """Defines the base hug concept of a type for use in function annotation.
       Override `__call__` to define how the type should be transformed and validated
    """
    _hug_type = True
    __slots__ = ()

    def __call__(self, value):
        raise NotImplementedError('To implement a new type __call__ must be defined')


def create(base_type=Type):
    """Creates a new type handler with the specified transformations"""
    def new_type_hdler(function):
        class NewType(base_type):
            def __call__(self, value):
                return function(value)
        NewType.__doc__ = function.__doc__
        return NewType

    return new_type_handler


class Accept(Type):
    """Allows quick wrapping any Python type converter for use with Hug type annotations"""
    __slots__ = ('kind', 'base_kind', 'error_text', 'exception_handlers', 'doc')

    def __init__(self, kind, doc=None, error_text=None, exception_handlers=None):
        self.kind = kind
        self.base_kind = getattr(self.kind, 'base_kind', self.kind)
        self.doc = doc or self.kind.__doc__
        self.error_text = error_text
        self.exception_handlers = exception_handlers or {}

    @property
    def __doc__(self):
        return self.doc

    def __call__(self, value):
        if self.exception_handlers or self.error_text:
            try:
                return self.kind(value)
            except Exception as exception:
                for take_exception, rewrite in self.exception_handlers.items():
                    if isinstance(exception, take_exception):
                        if isinstance(rewrite, str):
                            raise ValueError(rewrite)
                        else:
                            raise rewrite(value)
                if self.error_text:
                    raise ValueError(self.error_text)
                raise exception
        else:
            return self.kind(value)

number = Accept(int, 'A whole number', 'Invalid whole number provided')
float_number = Accept(float, 'A float number', 'Invalid float number provided')
decimal = Accept(Decimal, 'A decimal number', 'Invalid decimal number provided')
boolean = Accept(bool, 'Providing any value will set this to true',
                 'Invalid boolean value provided')
uuid = Accept(hug_uuid.UUID, 'A Universally Unique IDentifier', 'Invalid UUID provided')


class Text(Type):
    """Basic text / string value"""
    __slots__ = ()

    def __call__(self, value):
        if type(value) in (list, tuple):
            raise ValueError('Invalid text value provided')
        return str(value)

text = Text()


class Multiple(Type):
    """Multiple Values"""
    __slots__ = ()

    def __call__(self, value):
        return value if isinstance(value, list) else [value]


class DelimitedList(Type):
    """Defines a list type that is formed by delimiting a list with a certain character or set of characters"""
    __slots__ = ('using', )

    def __init__(self, using=","):
        self.using = using

    @property
    def __doc__(self):
        return '''Multiple values, separated by "{0}"'''.format(self.using)

    def __call__(self, value):
        return value if type(value) in (list, tuple) else value.split(self.using)


class SmartBoolean(Type):
    """Accepts a true or false value"""
    __slots__ = ()

    def __call__(self, value):
        if type(value) == bool or value in (None, 1, 0):
            return bool(value)

        value = value.lower()
        if value in ('true', 't', '1'):
            return True
        elif value in ('false', 'f', '0', ''):
            return False

        raise KeyError('Invalid value passed in for true/false field')


class InlineDictionary(Type):
    """A single line dictionary, where items are separted by commas and key:value are separated by a pipe"""
    __slots__ = ()

    def __call__(self, string):
        return {key.strip(): value.strip() for key, value in (item.split(":") for item in string.split("|"))}


class OneOf(Type):
    """Ensures the value is within a set of acceptable values"""
    __slots__ = ('values', )

    def __init__(self, values):
        self.values = values

    @property
    def __doc__(self):
        return 'Accepts one of the following values: ({0})'.format("|".join(self.values))

    def __call__(self, value):
        if not value in self.values:
            raise KeyError('Invalid value passed. The accepted values are: ({0})'.format("|".join(self.values)))
        return value


class Mapping(OneOf):
    """Ensures the value is one of an acceptable set of values mapping those values to a Python equivelent"""
    __slots__ = ('value_map', )

    def __init__(self, value_map):
        self.value_map = value_map
        self.values = value_map.keys()

    @property
    def __doc__(self):
        return 'Accepts one of the following values: ({0})'.format("|".join(self.values))

    def __call__(self, value):
        if not value in self.values:
            raise KeyError('Invalid value passed. The accepted values are: ({0})'.format("|".join(self.values)))
        return self.value_map[value]


class JSON(Type):
    """Accepts a JSON formatted data structure"""
    __slots__ = ()

    def __call__(self, value):
        if type(value) in (str, bytes):
            try:
                return load_json(value)
            except Exception:
                raise ValueError('Incorrectly formatted JSON provided')
        else:
            return value


class Multi(Type):
    """Enables accepting one of multiple type methods"""
    __slots__ = ('types', )

    def __init__(self, *types):
       self.types = types

    @property
    def __doc__(self):
        type_strings = (type_method.__doc__ for type_method in self.types)
        return 'Accepts any of the following value types:{0}\n'.format('\n  - '.join(type_strings))

    def __call__(self, value):
        for type_method in self.types:
            try:
                return type_method(value)
            except:
                pass
        raise ValueError(self.__doc__)


class InRange(Type):
    """Accepts a number within a lower and upper bound of acceptable values"""
    __slots__ = ('lower', 'upper', 'convert')

    def __init__(self, lower, upper, convert=number):
        self.lower = lower
        self.upper = upper
        self.convert = convert

    @property
    def __doc__(self):
        return "{0} that is greater or equal to {1} and less than {2}".format(self.convert.__doc__,
                                                                              self.lower, self.upper)

    def __call__(self, value):
        value = self.convert(value)
        if value < self.lower:
            raise ValueError("'{0}' is less than the lower limit {1}".format(value, self.lower))
        if value >= self.upper:
            raise ValueError("'{0}' reaches the limit of {1}".format(value, self.upper))
        return value


class LessThan(Type):
    """Accepts a number within a lower and upper bound of acceptable values"""
    __slots__ = ('limit', 'convert')

    def __init__(self, limit, convert=number):
        self.limit = limit
        self.convert = convert

    @property
    def __doc__(self):
         return "{0} that is less than {1}".format(self.convert.__doc__, self.limit)

    def __call__(self, value):
        value = self.convert(value)
        if not value < self.limit:
            raise ValueError("'{0}' must be less than {1}".format(value, self.limit))
        return value


class GreaterThan(Type):
    """Accepts a value above a given minimum"""
    __slots__ = ('minimum', 'convert')

    def __init__(self, minimum, convert=number):
        self.minimum = minimum
        self.convert = convert

    @property
    def __doc__(self):
        return "{0} that is greater than {1}".format(self.convert.__doc__, self.minimum)

    def __call__(self, value):
        value = self.convert(value)
        if not value > self.minimum:
            raise ValueError("'{0}' must be greater than {1}".format(value, self.minimum))
        return value


class Length(Type):
    """Accepts a a value that is withing a specific length limit"""
    __slots__ = ('lower', 'upper', 'convert')

    def __init__(self, lower, upper, convert=text):
        self.lower = lower
        self.upper = upper
        self.convert = convert

    @property
    def __doc__(self):
        return ("{0} that has a length longer or equal to {1} and less then {2}".format(self.convert.__doc__,
                                                                                        self.lower, self.upper))

    def __call__(self, value):
        value = self.convert(value)
        length = len(value)
        if length < self.lower:
            raise ValueError("'{0}' is shorter than the lower limit of {1}".format(value, self.lower))
        if length >= self.upper:
            raise ValueError("'{0}' is longer then the allowed limit of {1}".format(value, self.upper))
        return value


class ShorterThan(Type):
    """Accepts a text value shorter than the specified length limit"""
    __slots__ = ('limit', 'convert')

    def __init__(self, limit, convert=text):
        self.limit = limit
        self.convert = convert

    @property
    def __doc__(self):
        return "{0} with a length of no more than {1}".format(self.convert.__doc__, self.limit)

    def __call__(self, value):
        value = self.convert(value)
        length = len(value)
        if not length < self.limit:
            raise ValueError("'{0}' is longer then the allowed limit of {1}".format(value, self.limit))
        return value


class LongerThan(Type):
    """Accepts a value up to the specified limit"""
    __slots__ = ('limit', 'convert')

    def __init__(self, limit, convert=text):
        self.limit = limit
        self.convert = convert

    @property
    def __doc__(self):
        return "{0} with a length longer than {1}".format(self.convert.__doc__, self.limit)

    def __call__(self, value):
        value = self.convert(value)
        length = len(value)
        if not length > self.limit:
            raise ValueError("'{0}' must be longer than {1}".format(value, self.limit))
        return value


class CutOff(Type):
    """Cuts off the provided value at the specified index"""
    __slots__ = ('limit', 'convert')

    def __init__(self, limit, convert=text):
        self.limit = limit
        self.convert = convert

    @property
    def __doc__(self):
        return "'{0}' with anything over the length of {1} being ignored".format(self.convert.__doc__, self.limit)

    def __call__(self, value):
        return self.convert(value)[:self.limit]


class Chain(Type):
    """type for chaining multiple types together"""
    __slots__ = ('types', )

    def __init__(self, *types):
        self.types = types

    def __call__(self, value):
        for type_function in self.types:
            value = type_function(value)
        return value


class Nullable(Chain):
    """A Chain types that Allows None values"""
    __slots__ = ('types', )

    def __init__(self, *types):
        self.types = types

    def __call__(self, value):
        if value == None:
            return None
        else:
            return super(Nullable, self).__call__(value)


class TypedProperty(object):
    """class for building property objects for schema objects"""
    __slots__ = ('name', 'type_func')

    def __init__(self, name, type_func):
        self.name = "_" + name
        self.type_func = type_func

    def __get__(self, instance, cls):
        return getattr(instance, self.name, None)

    def __set__(self, instance, value):
        setattr(instance, self.name, self.type_func(value))

    def __delete__(self,instance):
        raise AttributeError("Can't delete attribute")


class NewTypeMeta(type):
    """Meta class to turn Schema objects into format usable by hug"""
    __slots__ = ()

    def __init__(cls, name, bases, nmspc):
        cls._types = {attr: getattr(cls, attr) for attr in dir(cls) if getattr(getattr(cls, attr), "_hug_type", False)}
        slots = getattr(cls, "__slots__", ())
        slots = set(slots)
        for attr, type_func in cls._types.items():
            slots.add("_" + attr)
            slots.add(attr)
            prop = TypedProperty(attr, type_func);
            setattr(cls, attr, prop)
        cls.__slots__ = tuple(slots)
        super(NewTypeMeta, cls).__init__(name, bases, nmspc)


class Schema(object, metaclass=NewTypeMeta):
    """Schema for creating complex types using hug types"""
    _hug_type = True
    __slots__ = ()

    def __new__(cls, json, *args, **kwargs):
        if json.__class__ == cls:
            return json
        else:
            return super(Schema, cls).__new__(cls)

    def __init__(self, json, force=False):
        if self != json:
            for (key, value) in json.items():
                if force:
                    key = "_" + key
                setattr(self, key, value)

json = JSON()


class MarshmallowSchema(Type):
    """Allows using a Marshmallow Schema directly in a hug type annotation"""
    __slots__ = ("schema", )

    def __init__(self, schema):
        self.schema = schema

    @property
    def __doc__(self):
        return self.schema.__doc__ or self.schema.__class__.__name__

    def __call__(self, value):
        value, errors = self.schema.loads(value) if isinstance(value, str) else self.schema.load(value)
        if errors:
            raise InvalidTypeData('Invalid {0} passed in'.format(self.schema.__class__.__name__), errors)
        return value


multiple = Multiple()
smart_boolean = SmartBoolean()
inline_dictionary = InlineDictionary()
comma_separated_list = DelimitedList(using=",")


# NOTE: These forms are going to be DEPRECATED, here for backwards compatibility only
accept = Accept
delimited_list = DelimitedList
one_of = OneOf
mapping = Mapping
multi = Multi
in_range = InRange
less_than = LessThan
greater_than = GreaterThan
length = Length
shorter_than = ShorterThan
longer_than = LongerThan
cut_off = CutOff
