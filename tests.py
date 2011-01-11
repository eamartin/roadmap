# -*- coding: utf-8 -*-

from attest import Tests, Assert
from roadmap import Roadmap

roadmap = Tests()

@roadmap.context
def make_context():
    r = Roadmap()

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

    yield r

@roadmap.test
def initialization(instance):
    assert isinstance(instance, Roadmap)

@roadmap.test
def route_without_passing_obj(instance):
    Assert(instance.route('yeah')) == 'YES'

@roadmap.test
def route_with_passing_obj(instance):
    string = 'No way'
    Assert(instance.route(string)) == 'NO: %s' % string

@roadmap.test
def route_with_captured_group(instance):
    string = 'email@example.org'
    Assert(instance.route(string)) == 'ORG ADDRESS: %s' % string.split('@')[0]

@roadmap.test
def route_object_by_string(instance):
    class Email(object):

        def __init__(self, adr):
            self.address = adr

    string = 'email@example.com'
    obj = Email(string)
    Assert(instance.route(obj, key=obj.address)) == 'COM ADDRESS: %s' % string

if __name__ == '__main__':
    roadmap.main()