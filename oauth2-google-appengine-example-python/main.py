import webapp2
import httplib2
import os

from apiclient.discovery import build
from oauth2client.appengine import oauth2decorator_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError
from google.appengine.api import memcache
from google.appengine.ext.webapp import template


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
        variables = {
                     'url': decorator.authorize_url(),
                     'has_credentials': decorator.has_credentials()
                     }
        self.response.out.write(template.render(path, variables))


class AboutHandler(webapp2.RequestHandler):

    @decorator.oauth_required
    def get(self):
        try:
            http = decorator.http()
            user = service.people().get(userId='me').execute(http=http)
            user_name = '%s' % user['displayName']
            image_url = 'https://lh5.googleusercontent.com/-HmfAHy7_IAs/AAAAAAAAAAI/AAAAAAAAAnc/da5MUQMGjYo/photo.jpg';

            path = os.path.join(os.path.dirname(__file__), 'main.html')
            self.response.out.write(template.render(path, {
                                                           'user_name': user_name , 
                                                           'image_url' : image_url,   
                                                           'url': decorator.authorize_url(),
                                                           'has_credentials': decorator.has_credentials()
                                                           }))
        except AccessTokenRefreshError:
            self.redirect('/')



app = webapp2.WSGIApplication([
                               ('/', MainHandler),
                               ('/about', AboutHandler),
                               (decorator.callback_path, decorator.callback_handler()),
                               ], debug=True)
