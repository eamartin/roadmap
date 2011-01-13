# -*- coding: utf-8 -*-
'''Roadmap is a routing library powered by regular expressions. Roadmap was
created to quickly map large amounts of input to functions. In the particular
case that sparked Roadmap's development, I was writing an IRC bot and I wanted
a fast (to code and to execute) way to map input strings to functions. Beyond an
IRC bot, I could also picture Roadmap being used to process data from a web API,
user input, a socket, or really any stream of data.

Interface
----------

Using Roadmap is hopefully very simple. The complete public interface of Roadmap
consists of 3 methods.

    .. automethod:: roadmap.Router.destination

    .. automethod:: roadmap.Router.__init__

    .. automethod:: roadmap.Router.route

Details on Argument Passing
------------------------------

One slightly difficult aspect of using Roadmap is ensuring the desired arguments
get passed to the routed functions. Briefly, here is the algorithm:

*   The object routed (the primary input to :meth:`roadmap.Router.route`) will
    be passed to the function unless :obj:`pass_obj` is set to :obj:`False` upon
    registering the function with the :class:`~roadmap.Router` instance.
*   If :obj:`pass_obj` is :obj:`True` and :obj:`obj` is iterable, each item
    in the iterable will be passed to the function. This feature may or may not
    be convenient, but it was useful for my IRC bot so I could nearly
    transparently route tuples.
*   If unnamed groups are defined in the regular expression for the function,
    the value of each of these groups will be passed after the arguments from
    the object itself.
*   If named groups are defined in the regular expression for the function,
    they will be passed as keyword arguments (``name=value``) to the function.

The examples should make this admittedly complex behavior a bit clearer.

'''
import functools
import re

def coroutine(func):
    @functools.wraps(func)
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        cr.next()
        return cr
    return start

class Router(dict):

    def __init__(self, processor):
        '''Creates a new :class:`roadmap.Router` and assigns a processor.

        :param processor: single variable function that *does something* with output

        Because of Roadmap's coroutine based architechture, routing an object
        returns no value. At first it may seem strange that nothing can be
        returned, but the mindset of Roadmap is that you don't return values
        just for the sake of returning them; you return values to *do something*
        with them. In the case of my IRC bot, I wanted my functions to return
        strings. My :func:`processor` function received these strings and sent
        them over the socket. Other processing functions I can easily imagine are
        printing, logging, or commiting an object to a database.

        This concept might be a little tricky, but the example will show
        how simple it actually is.

        '''
        @coroutine
        @functools.wraps(processor)
        def _processor():
            try:
                while True:
                    obj = (yield)
                    processor(obj)
            except GeneratorExit:
                pass

        self.processor = _processor()
        self.find_match_target = self.find_match()

    def destination(self, reg_str, pass_obj=True):
        '''Decorates functions to be called from a :class:`roadmap.Router`
        instance.

        :param reg_str: string that a regular expression can be created from
        :param pass_obj: whether or not to pass object to decorated function
        :type pass_obj: boolean

        It is generally a good idea to use raw strings to create regular
        expressions. If the input string matches :obj:`reg_str`, the decorated
        function will be called.

        '''
        regex = re.compile(reg_str)

        def decorator(func):
            self[regex] = {'func': func, 'pass_obj': pass_obj}
            return func
        return decorator

    def get_function(self, obj, key=None):
        string = key or obj
        for regex in self.keys():
            match = regex.match(string)
            if match:
                return self[regex]['func']

    def route(self, obj, key=None):
        '''Maps an object to its appropriate function

        :param obj: object to route
        :param key: an optional string to route :obj`obj` by
        :rtype: :obj:`None`

        :meth:`~roadmap.Router.route` is the method that will receive the input
        and begin the routing process for an object. The :obj:`key` parameter
        must be used if the object itself can't be match by a regular
        expression, which, to the extent of my knowledge, means that that
        :obj:`obj` isn't a string. Even if :obj:`obj` is matchable, :obj:`key`
        will be used if defined.

        '''
        string = key or obj
        self.find_match_target.send((obj, string))

    @coroutine
    def find_match(self):
        handle_match = self.handle_match()
        while True:
            obj, string = (yield)
            for regex in self.keys():
                match = regex.match(string)
                if match:
                    handle_match.send((match, obj))

    @coroutine
    def handle_match(self):
        process_pair = self.process_pair()
        while True:
            match, obj = (yield)

            groups = match.groups()
            groupdict = match.groupdict()

            if groupdict:
                if len(groupdict) == len(groups):
                    process_pair.send((match.re, obj, (), groupdict))
                else:
                    exclusives = [s for s in groups if s not in groupdict.values()]
                    process_pair.send((match.re, obj, exclusives, groupdict))
            else:
                process_pair.send((match.re, obj, groups, {}))

    @coroutine
    def process_pair(self):
        while True:
            regex, obj, args, kwargs = (yield)

            if self[regex]['pass_obj']:
                if hasattr(obj, '__iter__'):
                    objects = [o for o in obj]
                    objects.extend(args)
                    self.processor.send(self[regex]['func'](*objects, **kwargs))
                else:
                    self.processor.send(self[regex]['func'](obj, *args, **kwargs))
            else:
                self.processor.send(self[regex]['func'](*args, **kwargs))