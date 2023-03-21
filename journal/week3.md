# Week 3 — Decentralized Authentication


&nbsp;
# Requirements

## Update `backend-flask/requirements.txt`
Add the following line to `backend-flask/requirements.txt`

```
Flask-AWSCognito
```
&nbsp;
# Docker

## Update `docker-compose.yml`
### backend-flask:
Add the following environment variables to the docker-compose file.
```
AWS_COGNITO_USER_POOL_ID: "us-east-1_..."
AWS_COGNITO_USER_POOL_CLIENT_ID: "..."
```

### frontend-react-js:
Add the following environment variables to the docker-compose file.
```
REACT_APP_AWS_PROJECT_REGION: "${AWS_DEFAULT_REGION}"
REACT_APP_AWS_COGNITO_REGION: "${AWS_DEFAULT_REGION}"
REACT_APP_AWS_USER_POOLS_ID: "us-east-1_..."
REACT_APP_CLIENT_ID: "..."
```
&nbsp;
# Cognito

## Create `backend-flask/lib/cognito_jwt_token.py`:

```python
import time
import requests
from jose import jwk, jwt
from jose.exceptions import JOSEError
from jose.utils import base64url_decode

class FlaskAWSCognitoError(Exception):
    pass

class TokenVerifyError(Exception):
    pass

class CognitoJwtToken:
    def __init__(self, user_pool_id, user_pool_client_id, region, request_client=None):
        ...
    def extract_access_token(self, request_headers):
        ...
    def _load_jwk_keys(self):
        ...
    def _extract_headers(token):
        ...
    def _find_pkey(self, headers):
        ...
    def _verify_signature(token, pkey_data):
        ...
    def _extract_claims(token):
        ...
    def _check_expiration(claims, current_time):
        ...
    def _check_audience(self, claims):
        ...
    def verify(self, token, current_time=None):
        ...
```

## Update `backend-flask/app.py`:

First, import the following classes
```python
from lib.cognito_jwt_token import CognitoJwtToken, FlaskAWSCognitoError, TokenVerifyError
```

Below the Flask app add the following lines of code
```python
cognito_jwt_token = CognitoJwtToken(
  user_pool_id = os.getenv("AWS_COGNITO_USER_POOL_ID"), 
  user_pool_client_id = os.getenv("AWS_COGNITO_USER_POOL_CLIENT_ID"), 
  region = os.getenv("AWS_DEFAULT_REGION")
)
```

Next, update the CORS headers like this

```python
cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  headers=['Content-Type', 'Authorization'], 
  expose_headers='Authorization',
  methods="OPTIONS,GET,HEAD,POST"
)
```

Finally, modify the data_home() method
```python
def data_home():
  access_token = cognito_jwt_token.extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    app.logger.debug(claims)
    app.logger.debug("authenticated user")
    data = HomeActivities.run(cognito_user_id=claims['username'])
  except TokenVerifyError as e:
    app.logger.debug("unauthenticated user")
    data = HomeActivities.run()
  
  return data, 200
```

## Update `backend-flask/services/home_activities.py`:

We can now change the run() method to accept a cognito_user_id and will show different dummy data if the user is authenticated.
```python
class HomeActivities:
  def run(cognito_user_id=None):
    
    ...

    if cognito_user_id != None:
        new_crud = {
        'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
        'handle':  'jeff',
        'message': 'blablabal, I am balbalar',
        'created_at': (now - timedelta(hours=1)).isoformat(),
        'expires_at': (now + timedelta(hours=12)).isoformat(),
        'likes': 90,
        'replies': []
        }

        results.insert(0, new_crud)

      return results


```

## Update `frontend-react-js/package.json`:
Now let's add aws-amplify (needed for cognito) to our project in `frontend-react-js/package.json`

```json
"aws-amplify": "^5.0.20",
```

## Update `frontend-react-js/src/App.js`:
Next let's configure aws-amplify in our frontend. Import the following into `frontend-react-js/src/App.js`
```python
import { Amplify } from 'aws-amplify';
```

Then add the following configuration
```javascript
Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
  "oauth": {},
  Auth: {
    region: process.env.REACT_APP_AWS_PROJECT_REGION,
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,
    userPoolWebClientId: process.env.REACT_APP_CLIENT_ID,
  }
});
```
Now we can use Auth methods in our components and pages simple by importing it. This way, we can implement a sign out button, a password recovery page, an email confirmation page, a sign in page and a sign up page. We can also "lock" the home feed until a user is authenticated. Here's how this was done in `frontend-react-js/src/pages/HomeFeedPage.js`.

## Update `frontend-react-js/src/pages/HomeFeedPage.js`:

```javascript
import { Auth } from 'aws-amplify';
```
 Add this header in loadData().res
 
```javascript
const res = await fetch(backend_url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`
        },
        method: "GET"
      });
```
Finally we can add code that checks if we are authenticated
```javascript
  const checkAuth = async () => {
    Auth.currentAuthenticatedUser({
      bypassCache: false 
    })
    .then((user) => {
      console.log('user',user);
      return Auth.currentAuthenticatedUser()
    }).then((cognito_user) => {
        setUser({
          display_name: cognito_user.attributes.name,
          handle: cognito_user.attributes.preferred_username
        })
    })
    .catch((err) => console.log(err));
  };
```


&nbsp;
# CSS

## Update `frontend-react-js/src/index.css`:

At the top of the file add the following code. This is where the theme will be defined. We can define variables for common css attributes that we want to keep consistent across the application. 

```css
:root {
  --bg: rgb(61,13,123);
  --fg: rgb(8,1,14);

  --field-border: rgba(255,255,255,0.29);
  --field-bg: rgb(31,31,31);
  --field-border-focus: rgb(149,0,255);
}
```

We can call those variables in css code as follows

```css
background: var(--bg)
```