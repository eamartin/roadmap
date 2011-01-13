# -*- coding: utf-8 -*-

from attest import Assert, Tests
import roadmap

roadmap_tests = Tests()

@roadmap_tests.context
def make_context():
    L = []

    r = roadmap.Router(L.append)

    @r.destination(r'^[yY]', pass_obj=False)
    def starts_with_y():
        return 'YES'

    @r.destination(r'^[nN]')
    def starts_with_n(response):
        return 'NO: %s' % response

    @r.destination(r'^org:(\w+)@\w+\.org$', pass_obj=False)
    def org_address(username):
        return 'ORG ADDRESS: %s' % username

    @r.destination(r'^com:\w+@\w+\.com$')
    def com_address(email_obj):
        return 'COM ADDRESS: %s' % email_obj.address

    @r.destination(r'end(.*?)[wW]+(?P<after_w>.*)')
    def ends_with_w(*args, **kwargs):
        return (args, kwargs)

    yield r, L

@roadmap_tests.test
def initialization(instance, L):
    Assert.isinstance(instance, roadmap.Router)

@roadmap_tests.test
def route_without_passing_obj(instance, L):
    instance.route('yeah')
    Assert(L[-1]) == 'YES'

@roadmap_tests.test
def route_with_passing_obj(instance, L):
    string = 'No way'
    instance.route(string)
    Assert(L[-1]) == 'NO: %s' % string

@roadmap_tests.test
def route_with_captured_group(instance, L):
    string = 'org:email@example.org'
    instance.route(string)
    Assert(L[-1]) == 'ORG ADDRESS: %s' % string.split(':')[1].split('@')[0]

@roadmap_tests.test
def route_object_by_key(instance, L):
    class Email(object):

        def __init__(self, adr):
            self.address = adr

    string = 'com:email@example.com'
    obj = Email(string)
    instance.route(obj, key=obj.address)
    Assert(L[-1]) == 'COM ADDRESS: %s' % string

@roadmap_tests.test
def get_function(instance, L):
    Assert(instance.get_function('com:email@example.com').__name__) == \
                                                                   'com_address'

@roadmap_tests.test
def argument_passing(instance, L):
    string = 'endbeforewwwwafter'
    objs = ('woot', 'scoot')
    instance.route(objs, key=string)
    Assert(L[-1]) == (('woot', 'scoot', 'before'), {'after_w': 'after'})


if __name__ == '__main__':
    roadmap_tests.main()