Roadmap

This library is all about routing. A Roadmap instance is instantiated,
"destinations" (aka functions) are registered, and strings are passed to the
Roadmap's instance's route method. Code is better than english, so here is an
example.

def process(s):
    print s

r = Roadmap(process)

@r.destination(r'[Yy]')
def yes(string):
    return 'You said yes\nTo be exact, you actually said %s' % string

@r.destination(r'(.+)@.+', pass_obj=False)
def email(username):
    '''doesnt pass the string itself, just the capture from the regex'''
    print username