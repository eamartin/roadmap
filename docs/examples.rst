Examples
=========

Let's create a basic :class:`~roadmap.Router` instance to route email
addresses. We will route them by subdomain. The goal is to respond to basic
commands from string. We only want the bot to respond to commands, which will
all be prefixed by ``!``. The output of this Roadmap will just be printing.
Therefore, it is logical for each handler to return a string. Here we go::

    import roadmap.Router

    def my_processor(string):
        print string

    r = roadmap.Router(my_processor)

    @r.destination(r'^echo (.*)', pass_obj=False)
    def echo(message):
        return message

    @r.destination(r'^divide ([0-9]+) ([0-9]+)', pass_obj=False)
    def divide(dividend, divisor):
        return int(dividend) / float(divisor)

    @r.destination(r'^test .*')
    def test(string):
        return 'Input received: %s' % string

    @r.destination(r'^intials (?P<last>),\W+(?P<first>)\W+(?P<middle>) ',\
                                                        pass_obj=False)
    def initials(first, middle, last):
        return '%s. %s. %s.' % (first[0], middle[0], last[0])

    for input in input_stream():
        if input.startswith('!'):
            r.route(input[1:])

Sorry this example is simple and extremely contrived, but it shows the
main mechanics of Roadmap. Below, each part of the example is explained.

Initialization
----------------
::

    def my_processor(string):
        print string

    r = roadmap.Router(my_processor)

Each of the Router's function will be printable, and all we want to do with the
output is print right now. The :func:`my_processor` function could just as
easily handle instances as it handles strings in this function, and it save to
database or communicate over a socket rather than just printing. :obj:`r` is
created as a new :class:`~roadmap.Router` that will use :func:`my_processor`.

Echo Function
--------------
::

    @r.destination(r'echo (.*)', pass_obj=False)
    def echo(message):
        return message

Any string that begins with ``echo`` will route to this function.
:obj:`pass_obj` is set to :obj:`False`, so the full input string (including
``echo``) will not be passed to the function, because there is no need for
every message to being with ``echo``. However, the regular expression does
contain a group (indicated by the parenthesis) that will match any string.
Unnamed groups are passed to the function in the order they are assigned.
The regular expression group becomes :obj:`message` and is returned by the
function, and then printed by :func:`my_processor`.

Add Function
-------------
::

    @r.destination(r'^divide ([0-9]+) ([0-9]+)', pass_obj=False)
    def divide(dividend, divisor):
        return int(dividend) / double(divisor)

:func:`add` follows the exact same rules as :func:`echo`, but simply shows that
multiple unnamed groups can be used. The first group becomes :obj:`dividend`,
the second group becomes :obj:`divisor`. Notice the type casting, because
regular expression matches return strings.

Test Function
--------------
::

    @r.destination(r'^test .*')
    def test(string):
        return 'Input received: %s' % string

Note that no groups are captured in the regular expression. However,
:obj:`pass_obj` is not specified, and defaults to :obj:`True`. Therefore, the
string passed to :meth:`roadmap.Router.route` where will be passed to
:func:`test` as :obj:`string`.

Initials Function
------------------
::

    @r.destination(r'^intials (?P<last>),\W+(?P<first>)\W+(?P<middle>) ',\
                                                        pass_obj=False)
    def initials(first, middle, last):
        return '%s. %s. %s.' % (first[0], middle[0], last[0])

This is how named groups are handled by Roadmap. The order in the regular
expression does not have to correspond to the order of the parameters.

Calling :meth:`~roadmap.Router.route`
--------------------------------------
::

    for in_string in input_stream():
        if in_string.startswith('!'):
            r.route(in_string[1:])

This calls :meth:`~roadmap.Router.route` with the ``!`` stripped from the input
string. Notice that :meth:`roadmap.Router.route` returns no value.