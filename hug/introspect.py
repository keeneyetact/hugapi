"""hug/introspect.py

Defines built in hug functions to aid in introspection

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

def arguments(function):
    '''Returns the name of all arguments a function takes'''
    return function.__code__.co_varnames[:function.__code__.co_argcount] if hasattr(function, '__code__') else ()


def takes_kwargs(function):
    '''Returns True if the supplied function takes keyword arguments'''
    return bool(api_function.__code__.co_flags & 0x08)


def takes_kargs(function):
    '''Returns True if the supplied functions takes extra non-keyword arguments'''
    return bool(api_function.__code__.co_flags & 0x04)


def takes_arguments(function, *named_arguments):
    '''Returns the arguments that a function takes from a list of requested arguments'''
    return set(named_arguments).intersection(arguments(function)


def takes_all_arguments(function, *named_arguments):
    '''Returns True if all supplied arguments are found in the function'''
    return bool(takes_arguments(*named_arguments) == set(named_arguments))
