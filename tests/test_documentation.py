"""tests/test_documentation.py.

Tests the documentation generation capibilities integrated into Hug

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
import json

from falcon import Request
from falcon.testing import StartResponseMock, create_environ

import hug

api = hug.API(__name__)


def test_basic_documentation():
    """Ensure creating and then documenting APIs with Hug works as intuitively as expected"""
    @hug.get()
    def hello_world():
        """Returns hello world"""
        return "Hello World!"

    @hug.post()
    def echo(text):
        """Returns back whatever data it is given in the text parameter"""
        return text

    @hug.post('/happy_birthday', examples="name=HUG&age=1")
    def birthday(name, age:hug.types.number=1):
        """Says happy birthday to a user"""
        return "Happy {age} Birthday {name}!".format(**locals())

    @hug.post()
    def noop(request, response):
        """Performs no action"""
        pass

    @hug.get()
    def string_docs(data:'Takes data') -> 'Returns data':
        """Annotations defined with strings should be documentation only"""
        pass

    documentation = api.documentation()
    assert 'test_documentation' in documentation['overview']

    assert '/hello_world' in documentation
    assert '/echo' in documentation
    assert '/happy_birthday' in documentation
    assert not '/birthday' in documentation
    assert '/noop' in documentation
    assert '/string_docs' in documentation

    assert documentation['/hello_world']['GET']['usage']  == "Returns hello world"
    assert documentation['/hello_world']['GET']['examples']  == ["/hello_world"]
    assert documentation['/hello_world']['GET']['outputs']['content_type']  == "application/json"
    assert not 'inputs' in documentation['/hello_world']['GET']

    assert 'text' in documentation['/echo']['POST']['inputs']['text']['type']
    assert not 'default' in documentation['/echo']['POST']['inputs']['text']

    assert 'number' in documentation['/happy_birthday']['POST']['inputs']['age']['type']
    assert documentation['/happy_birthday']['POST']['inputs']['age']['default'] == 1

    assert not 'inputs' in documentation['/noop']['POST']

    assert documentation['/string_docs']['GET']['inputs']['data']['type'] == 'Takes data'
    assert documentation['/string_docs']['GET']['outputs']['type'] == 'Returns data'

    @hug.post(versions=1)
    def echo(text):
        """V1 Docs"""
        return 'V1'

    @hug.get()
    def unversioned():
        return 'Hello'

    versioned_doc = api.documentation()
    assert 'versions' in versioned_doc
    assert 1 in versioned_doc['versions']
    assert '/unversioned' in versioned_doc['versions'][1]

    specific_version_doc  = api.documentation(api_version=1)
    assert not 'versions' in specific_version_doc
    assert '/echo' in specific_version_doc
    assert '/unversioned' in specific_version_doc

    handler = hug.run.documentation_404(api)
    response = StartResponseMock()
    handler(Request(create_environ(path='v1/doc')), response)
    documentation = json.loads(response.data.decode('utf8'))['documentation']
    assert not 'versions' in documentation
    assert '/echo' in documentation
