HUG
===================

Everyone needs a hug every once in a while. Even API developers. Hug aims to make developing Python driven APIs as simple as possible, but no simpler.

[![PyPI version](https://badge.fury.io/py/hug.png)](http://badge.fury.io/py/hug)
[![PyPi downloads](https://pypip.in/d/hug/badge.png)](https://crate.io/packages/hug/)
[![Build Status](https://travis-ci.org/timothycrosley/hug.png?branch=master)](https://travis-ci.org/timothycrosley/hug)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/hug/)

Hug drastically simplifies Python API development.

Hug's Design Objectives:

- Make developing a Python driven API as succint as a written definition.
- The framework should encourage code that self-documents.
- It should be fast. Never should a developer feel the need to look somewhere else for performance reasons.
- Writing tests for APIs written on-top of Hug should be easy and intuitive.
- Magic done once, in an API, is better then pushing the problem set to the user of the API.


Basic Example API
===================

happy_birthday.py

    """A basic (single function) API written using Hug"""
    import hug


    @hug.get('/happy_birthday')
    def happy_birthday(name, age:hug.types.number=1):
        """Says happy birthday to a user"""
        return "Happy {age} Birthday {name}!".format(**locals())

To run the example:

    hug happy_birthday.py

Then you can access the example from localhost:8080/happy_birthday?name=Hug&age=1
Or access the documentation for your API from localhost:8080/documentation


Versioning with Hug
===================

versioning_example.py

    """A simple example of a hug API call with versioning"""


    @hug.version[1].get('/echo')
    def echo(text):
        return text


    @hug.version[2:].get('/echo')
    def echo(text):
        return "Echo: {text}".format(**locals())

To run the example:

    hug versioning_example.py

Then you can access the example from localhost:8080/v1/echo?text=Hi / localhost:8080/v2/echo?text=Hi
Or access the documentation for your API from localhost:8080/documentation

Note: versioning in hug automatically supports both the version header as well as direct URL based specification.


Testing Hug APIs
===================

Hugs http method decorators don't modify your original functions. This makes testing Hug APIs as simple as testing
any other Python functions. Additionally, this means interacting with your API functions in other Python code is as
straight forward as calling Python only API functions.


Why Hug?
===================
HUG simply stands for Hopefully Useful Guide. This represents the projects goal to help guide developers into creating
well written and intuitive APIs. Also, it's cheerful :)

--------------------------------------------

Thanks and I hope you find *this* hug helpful as you develop your next Python API!

~Timothy Crosley
