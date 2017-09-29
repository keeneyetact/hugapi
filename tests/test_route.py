"""tests/test_decorators.py.

Tests that class based hug routes interact as expected

Copyright (C) 2016 Timothy Edmund Crosley

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
import hug
from hug.routing import CLIRouter, ExceptionRouter, NotFoundRouter, SinkRouter, StaticRouter, URLRouter

api = hug.API(__name__)


def test_simple_class_based_view():
    """Test creating class based routers"""
    @hug.object.urls('/endpoint', requires=())
    class MyClass(object):

        @hug.object.get()
        def my_method(self):
            return 'hi there!'

        @hug.object.post()
        def my_method_two(self):
            return 'bye'

    assert hug.test.get(api, 'endpoint').data == 'hi there!'
    assert hug.test.post(api, 'endpoint').data == 'bye'


def test_url_inheritance():
    """Test creating class based routers"""
    @hug.object.urls('/endpoint', requires=(), versions=1)
    class MyClass(object):

        @hug.object.urls('inherits_base')
        def my_method(self):
            return 'hi there!'

        @hug.object.urls('/ignores_base')
        def my_method_two(self):
            return 'bye'

        @hug.object.urls('ignore_version', versions=None)
        def my_method_three(self):
            return 'what version?'

    assert hug.test.get(api, '/v1/endpoint/inherits_base').data == 'hi there!'
    assert hug.test.post(api, '/v1/ignores_base').data == 'bye'
    assert hug.test.post(api, '/v2/ignores_base').data != 'bye'
    assert hug.test.get(api, '/endpoint/ignore_version').data == 'what version?'


def test_simple_class_based_method_view():
    """Test creating class based routers using method mappings"""
    @hug.object.http_methods()
    class EndPoint(object):

        def get(self):
            return 'hi there!'

        def post(self):
            return 'bye'

    assert hug.test.get(api, 'endpoint').data == 'hi there!'
    assert hug.test.post(api, 'endpoint').data == 'bye'


def test_routing_class_based_method_view_with_sub_routing():
    """Test creating class based routers using method mappings, then overriding url on sub method"""
    @hug.object.http_methods()
    class EndPoint(object):

        def get(self):
            return 'hi there!'

        @hug.object.urls('/home/')
        def post(self):
            return 'bye'

    assert hug.test.get(api, 'endpoint').data == 'hi there!'
    assert hug.test.post(api, 'home').data == 'bye'


def test_routing_class_with_cli_commands():
    """Basic operation test"""
    @hug.object(name='git', version='1.0.0')
    class GIT(object):
        """An example of command like calls via an Object"""

        @hug.object.cli
        def push(self, branch='master'):
            return 'Pushing {}'.format(branch)

        @hug.object.cli
        def pull(self, branch='master'):
            return 'Pulling {}'.format(branch)

    assert 'token' in hug.test.cli(GIT.push, branch='token')
    assert 'another token' in hug.test.cli(GIT.pull, branch='another token')


def test_routing_class_based_method_view_with_cli_routing():
    """Test creating class based routers using method mappings exposing cli endpoints"""
    @hug.object.http_methods()
    class EndPoint(object):

        @hug.object.cli
        def get(self):
            return 'hi there!'

        def post(self):
            return 'bye'

    assert hug.test.get(api, 'endpoint').data == 'hi there!'
    assert hug.test.post(api, 'endpoint').data == 'bye'
    assert hug.test.cli(EndPoint.get) == 'hi there!'


def test_routing_instance():
    """Test to ensure its possible to route a class after it is instanciated"""
    class EndPoint(object):

        @hug.object
        def one(self):
            return 'one'

        @hug.object
        def two(self):
            return 2

    hug.object.get()(EndPoint())
    assert hug.test.get(api, 'one').data == 'one'
    assert hug.test.get(api, 'two').data == 2


class TestAPIRouter(object):
    """Test to ensure the API router enables easily reusing all other routing types while routing to an API"""
    router = hug.route.API(__name__)

    def test_route_url(self):
        """Test to ensure you can dynamically create a URL route attached to a hug API"""
        assert self.router.urls('/hi/').route == URLRouter('/hi/', api=api).route

    def test_route_http(self):
        """Test to ensure you can dynamically create an HTTP route attached to a hug API"""
        assert self.router.http('/hi/').route == URLRouter('/hi/', api=api).route

    def test_method_routes(self):
        """Test to ensure you can dynamically create an HTTP route attached to a hug API"""
        for method in hug.HTTP_METHODS:
            assert getattr(self.router, method.lower())('/hi/').route['accept'] == (method, )

        assert self.router.get_post('/hi/').route['accept'] == ('GET', 'POST')
        assert self.router.put_post('/hi/').route['accept'] == ('PUT', 'POST')

    def test_not_found(self):
        """Test to ensure you can dynamically create a Not Found route attached to a hug API"""
        assert self.router.not_found().route == NotFoundRouter(api=api).route

    def test_static(self):
        """Test to ensure you can dynamically create a static route attached to a hug API"""
        assert self.router.static().route == StaticRouter(api=api).route

    def test_sink(self):
        """Test to ensure you can dynamically create a sink route attached to a hug API"""
        assert self.router.sink().route == SinkRouter(api=api).route

    def test_exception(self):
        """Test to ensure you can dynamically create an Exception route attached to a hug API"""
        assert self.router.exception().route == ExceptionRouter(api=api).route

    def test_cli(self):
        """Test to ensure you can dynamically create a CLI route attached to a hug API"""
        assert self.router.cli().route == CLIRouter(api=api).route

    def test_object(self):
        """Test to ensure it's possible to route objects through a specified API instance"""
        assert self.router.object().route == hug.route.Object(api=api).route
