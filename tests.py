# -*- coding: utf-8 -*-

from attest import Tests, Assert
from roadmap import Router

roadmap = Tests()

@roadmap.context
def make_context():
    L = []

    r = Router(L.append)

    @r.destination(r'^[yY]', pass_obj=False)
    def yes():
        return 'YES'

    @r.destination(r'^[nN]')
    def no(response):
        return 'NO: %s' % response

    @r.destination(r'^(\w+)@\w+\.org$', pass_obj=False)
    def org_address(username):
        return 'ORG ADDRESS: %s' % username

    @r.destination(r'^\w+@\w+\.com$')
    def com_address(email_obj):
        return 'COM ADDRESS: %s' % email_obj.address

    yield r, L

@roadmap.test
def initialization(instance, L):
    assert isinstance(instance, Router)

@roadmap.test
def route_without_passing_obj(instance, L):
    instance.route('yeah')
    Assert(L[-1]) == 'YES'

@roadmap.test
def route_with_passing_obj(instance, L):
    string = 'No way'
    instance.route(string)
    Assert(L[-1]) == 'NO: %s' % string

@roadmap.test
def route_with_captured_group(instance, L):
    string = 'email@example.org'
    instance.route(string)
    Assert(L[-1]) == 'ORG ADDRESS: %s' % string.split('@')[0]

@roadmap.test
def route_object_by_string(instance, L):
    class Email(object):

        def __init__(self, adr):
            self.address = adr

    string = 'email@example.com'
    obj = Email(string)
    instance.route(obj, key=obj.address)
    Assert(L[-1]) == 'COM ADDRESS: %s' % string

if __name__ == '__main__':
    roadmap.main()