import webapp2
import httplib2
import cgi
import os

from apiclient.discovery import build
from oauth2client.appengine import oauth2decorator_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from google.appengine.api import users


# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found on the 
# API Access tab on the Google APIs Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1>
<p>
To make this sample run you will need to populate the client_secrets.json file
found at:
</p>
<code>%s</code>.
<p>with information found on the <a href="https://code.google.com/apis/console">APIs Console</a>.
</p>
""" % CLIENT_SECRETS


http = httplib2.Http(memcache)
service = build("plus", "v1", http=http)
decorator = oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/plus.me',
    message=MISSING_CLIENT_SECRETS_MESSAGE)

class MainHandler(webapp2.RequestHandler):

    @decorator.oauth_aware
    def get(self):
        
        path = os.path.join(os.path.dirname(__file__), 'main.html')
  
        try:
            http = decorator.http()
            mePerson = service.people().get(userId='me').execute(http=http)
            user_name = '%s' % mePerson['displayName']
            user_image_url = '%s' % mePerson['image']['url'];
            variables = {
               'user_name': user_name ,
               'user_image_url' : user_image_url,
               'url': users.create_logout_url('/', '/'),
               'has_credentials': decorator.has_credentials()
            }
            self.response.out.write(template.render(path, variables))
        except AccessTokenRefreshError:
            variables = {
                'url': decorator.authorize_url(),
                'has_credentials': decorator.has_credentials()
            }
            self.response.out.write(template.render(path, variables))
            
            
class RedirectHomeHandler(webapp2.RequestHandler):
    def post(self):
        self.redirect("/")            
            
            
class ServiceHandler(webapp2.RequestHandler):

    @decorator.oauth_aware
    def post(self):
        path = os.path.join(os.path.dirname(__file__), 'response.html')
  
        http = decorator.http()
        mePerson = service.people().get(userId='me').execute(http=http)
        user_name = '%s' % mePerson['displayName']
        user_image_url = '%s' % mePerson['image']['url'];
        variables = {
               'user_name': user_name ,
               'user_image_url' : user_image_url,
               'url': users.create_logout_url('/', '/'),
               'has_credentials': decorator.has_credentials(),
               'message' : cgi.escape(self.request.get('content')),
               'user_agent' : self.request.headers['User-Agent'],
               'version' : os.environ['SERVER_SOFTWARE']
        }
        self.response.out.write(template.render(path, variables))
             

app = webapp2.WSGIApplication([
                               ('/', MainHandler),
                               ('/response', ServiceHandler),
                               ('/main', MainHandler),
                               ('/home', RedirectHomeHandler),
                               (decorator.callback_path, decorator.callback_handler()),
                               ], debug=True)
