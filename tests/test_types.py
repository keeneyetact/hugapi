"""tests/test_types.py.

Tests the type validators included with Hug

Copyright (C) 2015 Timothy Edmund Crosley

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
from datetime import datetime
from decimal import Decimal

import pytest

import hug


def test_number():
    '''Tests that Hugs number type correctly converts and validates input'''
    assert hug.types.number('1') == 1
    assert hug.types.number(1) == 1
    with pytest.raises(ValueError):
        hug.types.number('bacon')


def test_multiple():
    '''Tests that Hugs multile type correctly forces values to come back as lists, but not lists of lists'''
    assert hug.types.multiple('value') == ['value']
    assert hug.types.multiple(['value1', 'value2']) == ['value1', 'value2']


def test_comma_separated_list():
    '''Tests that Hugs comma separated type correctly converts into a Python list'''
    assert hug.types.comma_separated_list('value') == ['value']
    assert hug.types.comma_separated_list('value1,value2') == ['value1', 'value2']



def test_float_number():
    '''Tests to ensure the float type correctly allows floating point values'''
    assert hug.types.float_number('1.1') == 1.1
    assert hug.types.float_number('1') == float(1)
    assert hug.types.float_number(1.1) == 1.1
    with pytest.raises(ValueError):
        hug.types.float_number('bacon')


def test_decimal():
    '''Tests to ensure the decimal type correctly allows decimal values'''
    assert hug.types.decimal('1.1') == Decimal('1.1')
    assert hug.types.decimal('1') == Decimal('1')
    assert hug.types.decimal(1.1) == Decimal(1.1)
    with pytest.raises(ValueError):
        hug.types.decimal('bacon')


def test_boolean():
    '''Test to ensure the custom boolean type correctly supports boolean conversion'''
    assert hug.types.boolean('1') == True
    assert hug.types.boolean('T') == True
    assert hug.types.boolean('') == False
    assert hug.types.boolean('False') == True
    assert hug.types.boolean(False) == False


def test_text():
    '''Tests that Hugs text validator correctly handles basic values'''
    assert hug.types.text('1') == '1'
    assert hug.types.text(1) == '1'
    assert hug.types.text('text') == 'text'


def test_inline_dictionary():
    '''Tests that inline dictionary values are correctly handled'''
    assert hug.types.inline_dictionary('1:2') == {'1': '2'}
    assert hug.types.inline_dictionary('1:2|3:4') == {'1': '2', '3': '4'}
    with pytest.raises(ValueError):
        hug.types.inline_dictionary('1')


def test_one_of():
    '''Tests that Hug allows limiting a value to one of a list of values'''
    assert hug.types.one_of(('bacon', 'sausage', 'pancakes'))('bacon') == 'bacon'
    assert hug.types.one_of(['bacon', 'sausage', 'pancakes'])('sausage') == 'sausage'
    assert hug.types.one_of({'bacon', 'sausage', 'pancakes'})('pancakes') == 'pancakes'
    with pytest.raises(KeyError):
        hug.types.one_of({'bacon', 'sausage', 'pancakes'})('syrup')


def test_accept():
    '''Tests to ensure the accept type wrapper works as expected'''
    custom_converter = lambda value: value + " converted"
    custom_type = hug.types.accept(custom_converter, 'A string Value')
    with pytest.raises(TypeError):
        custom_type(1)


def test_accept_custom_exception_text():
    '''Tests to ensure it's easy to custom the exception text using the accept wrapper'''
    custom_converter = lambda value: value + " converted"
    custom_type = hug.types.accept(custom_converter, 'A string Value', 'Error occurred')
    assert custom_type('bacon') == 'bacon converted'
    with pytest.raises(ValueError):
        custom_type(1)


def test_accept_custom_exception_handlers():
    '''Tests to ensure it's easy to custom the exception text using the accept wrapper'''
    custom_converter = lambda value: (str(int(value)) if value else value) + " converted"
    custom_type = hug.types.accept(custom_converter, 'A string Value', exception_handlers={TypeError: '0 provided'})
    assert custom_type('1') == '1 converted'
    with pytest.raises(ValueError):
        custom_type('bacon')
    with pytest.raises(ValueError):
        custom_type(0)

    custom_type = hug.types.accept(custom_converter, 'A string Value', exception_handlers={TypeError: KeyError})
    with pytest.raises(KeyError):
        custom_type(0)


def test_accept_custom_cli_behavior():
    '''Tests to ensure it's easy to customize the cli behavior using the accept wrapper'''
    custom_type = hug.types.accept(hug.types.multiple, 'Multiple values', cli_behaviour={'type': list})
    assert custom_type.cli_behaviour == {'type': list, 'action': 'append'}
