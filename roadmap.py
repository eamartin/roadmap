# -*- coding: utf-8 -*-

import re

def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        cr.next()
        return cr
    return start

class Router(dict):

    def __init__(self, processor):
        @coroutine
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
        regex = re.compile(reg_str)

        def decorator(func):
            self[regex] = {'func': func, 'pass_obj': pass_obj}
            return func
        return decorator

    def route(self, obj, key=None):
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