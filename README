Roadmap

This library is all about routing. A Roadmap instance is instantiated,
"destinations" (aka functions) are registered, and strings are passed to the
Roadmap's instance's route method. Code is better than english, so here is an
example.

r = Roadmap()

@r.destination(r'[Yy]')
def yes(string):
    print 'You said yes'
    print 'To be exact, you actually said %s' % string

@r.destination(r'(.+)@.+', pass_obj=False)
def email(username):
    '''doesnt pass the string itself, just the capture from the regex'''
    print username