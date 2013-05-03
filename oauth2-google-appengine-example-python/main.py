# Copyright (C) 2013, Markus Sprunck
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided
#   with the distribution.
#
# - The name of its contributor may be used to endorse or promote
#   products derived from this software without specific prior
#   written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 

import os
import cgi
import webapp2
import httplib2

from apiclient.discovery import build
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from oauth2client.appengine import oauth2decorator_from_clientsecrets
from oauth2client.client import AccessTokenRefreshError

# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which may be downloaded 
# from API Access tab on the Google APIs Console <http://code.google.com/apis/console>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Helpful message to display in the browser if the CLIENT_SECRETS file
# is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
<h1>Warning: Please configure OAuth 2.0</h1><p>
To make this sample run you will need to populate the client_secrets.json file
found at:</p><code>%s</code>.<p>with information found on the 
<a href="https://code.google.com/apis/console">APIs Console</a>.</p>
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
        path = os.path.join(os.path.dirname(__file__), 'templates/main.html')  
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
         
            
class ServiceHandler(webapp2.RequestHandler):

    @decorator.oauth_aware
    def post(self):
        path = os.path.join(os.path.dirname(__file__), 'templates/response.html')
  
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
        
                    
class RedirectHomeHandler(webapp2.RequestHandler):
   
    def post(self):
        self.redirect("/")      
             

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/response', ServiceHandler),
                               ('/home', RedirectHomeHandler),
                               (decorator.callback_path, decorator.callback_handler())],
                                debug=True)
