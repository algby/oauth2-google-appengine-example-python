oauth2-google-appengine-example-python
======================================

How to get User Information with OAuth2 in a Google AppEngine Python Application?

n the following article the use of OAuth2 in a Google AppEngine Python application to get user information like name, gender, picture, nickname, e-mail is described. 

The following example application http://oaae-sample-python.appspot.com/ demonstrates the implementation of login and display the name and picture of Google account at the right top corner of the window.

This small Google AppEngine application implements the same functionality and almost the same UI as the GWT & Java implementation http://oaae-sample.appspot.com/. So, you may directly compare the difference between Python and Java & GWT for Google AppEngine.  

Expected Result
In picture 1 the name of the logged on user name and profile picture have been marked in red. 

Picture 1: Screen shot of OAuth2 Google AppEngine
Example Code
The full code and used libraries are stored on GitHub (see link below).

// File #01: main.py

'''



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



'''

// File #02: app.yaml

'''
application: oaae-sample-python
version: 5
runtime: python27
api_version: 1

threadsafe: true

handlers:
- url: /static
  static_dir: static
  
- url: /.*
  script: main.app  

'''



// File #03: main.html

'''



<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<link type="text/css" rel="stylesheet"
href="./static/OAuthAppEngineSample.css">
<title>oauth2-google-appengine-example</title>
<link rel="stylesheet" href="./static/clean.css">
</head>
<body>

<div class="login-banner" align="right">
<table cellspacing="0" cellpadding="0">
<tbody>
<tr>

{% if has_credentials %}
<td align="left" style="vertical-align: top;"><a
class="login-area" href="{{ url }}" title="Sign out">{{ user_name }}</a></td>
<td align="left" style="vertical-align: top;"><img
class="login-area" src="{{ user_image_url }}" style="width: 24px;"
aria-hidden="false" /></td> {% else %}
<td align="left" style="vertical-align: top;"><a
class="login-area" href="{{ url }}" title="Sign in">Please, sign in with your
Google Account</a></td> {% endif %}

</tr>
</tbody>
</table>
</div>

<br></br>
<table align="center">
<tbody>
<tr>
<td>
<h2 align="center">OAuth2 Google AppEngine Example from
Software Engineering Candies</h2>
<h2 align="center">
<a href="http://www.sw-engineering-candies.com"> How to get
User Information with OAuth2 in a Google AppEngine Python
Application? </a>
</h2>
<h2 align="center">
You can <a
href="https://www.google.com/accounts/b/0/IssuedAuthSubTokens">
revoke</a> permission at any time.
</h2>
</td>
</tr>
</tbody>
</table>

<br></br>
<table align="center">
<tbody>
<tr>
<td colspan="2" style="font-weight: bold;">Please enter your
name:</td>
</tr>
<tr>
{% if has_credentials %}
<form action="/response" method="post">
<td><input type="text" name="content" class="gwt-TextBox"
value="{{ user_name }}"></input></td>
<td><button type="submit" class="gwt-Button sendButton">Send</button></td>
</form>
{% else %}
<td><input type="text" class="gwt-TextBox" disabled=""></td>
<td><button type="button" class="gwt-Button sendButton"
disabled="">Send</button></td> {% endif %}
</tr>
<tr>
<td colspan="2" style="color: red;" id="errorLabelContainer"><div
class="gwt-Label"></div></td>
</tr>
</tbody>
</table>
</body>
</html>


'''


// File #04: response.html


'''



<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<link type="text/css" rel="stylesheet"
href="../static/OAuthAppEngineSample.css">
<title>OAuth2 Python</title>
<link rel="stylesheet" href="../static/clean.css">
</head>
<body>

<div class="login-banner" align="right">
<table cellspacing="0" cellpadding="0">
<tbody>
<tr>

{% if has_credentials %}
<td align="left" style="vertical-align: top;"><a
class="login-area" href="{{ url }}" title="Sign out">{{ user_name }}</a></td>
<td align="left" style="vertical-align: top;"><img
class="login-area" src="{{ user_image_url }}" style="width: 24px;"
aria-hidden="false" /></td> {% else %}
<td align="left" style="vertical-align: top;"><a
class="login-area" href="{{ url }}" title="Sign in">Please, sign in with your
Google Account</a></td> {% endif %}

</tr>
</tbody>
</table>
</div>

<br></br>
<table align="center">
<tbody>
<tr>
<td align="left" style="vertical-align: top;">
<div class="gwt-HTML">
<b>Sending name to the server:</b>
</div>
</td>
</tr>
<tr>
<td align="left" style="vertical-align: top;">
<div class="gwt-Label">{{ message }}</div>
</td>
</tr>
<tr>
<td align="left" style="vertical-align: top;"><div
class="gwt-HTML">
<br> <b>Server replies:</b>
</div></td>
</tr>
<tr>
<td align="left" style="vertical-align: top;"><div
class="gwt-HTML">
Hello, {{ message }} ! <br> <br>I am running {{ version }}.<br> <br>It looks
like you are using:<br>{{ user_agent }}
</div></td>
</tr>
<tr>
<form action="/home" method="post">
<td align="right" style="vertical-align: top;"><button
type="submit" class="gwt-Button" id="closeButton">Back</button></td>
</form>
</tr>
</tbody>
</table>

</body>
</html>

'''


Test Expected Result

1) Press sign in link in the top dark bar.


2) Agree access. You can withdraw the access rights in Google Dashboard (see link below).


3) The name and picture should appear at the right top corner. Now you may press the Send button to send a message to the server.


4) Press Back button to return to main page


5) You may now revoke the permission.


Please, do not hesitate to contact me if you have any ideas for improvement and/or you find a bug in the example code.
Further Reading
1) Google AppEngine; 
https://developers.google.com/appengine/docs/python/gettingstartedpython27/
2) Google Dashboard (Authorized Access to your Google Account); http://www.google.com/dashboard
3) Using OAuth 2.0 to Access Google APIs; http://developers.google.com/accounts/docs/OAuth2
4) Google AppEngine (Sign up); http://developers.google.com/appengine
5) Google APIs; http://code.google.com/apis/console 
Find Code on GitHub

    https://github.com/MarkusSprunck/oauth2-google-appengine-example-python.git

