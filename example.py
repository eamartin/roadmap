from roadmap import Roadmap

r = Roadmap()

def foo():
    print 'Sorry, regex not found'
    
r.default = foo

class EmailAdress(object):
    def __init__(self, adr):
        self.adr = adr

@r.destination(r'^\w+@\w+\.com$')
def com_address(full_address):
    print 'Commercial address'
    print full_address
    
@r.destination('^(\w+)@\w+\.org$', pass_obj=False)
def org_address(username):
    print 'Organization address'
    print username
    
@r.destination(r'^[yY]', pass_obj=False)
def yes():
    return 'yes'

@r.destination(r'^[nN]')    
def no(response):
    print 'You said no :('
    print '("' + str(response) + '" to be exact)'
    
while True:
    r.route(raw_input('Test me>\t'))