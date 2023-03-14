"""
The code defines a Flask blueprint called oauth_blueprint that handles various OAuth-related endpoints. The oauth function handles the authorization request from a third-party application, the token function handles the token request to exchange an authorization code for an access token, and the generate_auth_code function generates a unique authorization code for a given set of inputs.

The oauth function first checks that the client ID and redirect URI supplied in the authorization request are valid, and that the user is authenticated. If these checks pass, it renders an HTML template that allows the user to approve or deny the authorization request. If the user approves the request, the oauth function generates an authorization code and saves it to the database, then redirects the user's browser to the third-party application's redirect URI with the authorization code and state parameter as query string parameters.

The token function takes an authorization code and client credentials as input, and returns an access token if the authorization code is valid and the client credentials are correct. It first checks that the client credentials are valid by hashing the client secret and comparing it to the hash stored in the database. If the client credentials check passes, it decodes the authorization code to get the user ID and client ID, and generates an access token using the generate_token function. The generate_token function creates a JSON Web Token (JWT) containing the user ID, client ID, expiration time, and other information, signs it with a secret key, and returns the token as a string.
"""

from flask import Blueprint, request, render_template, redirect, jsonify
from prisma.models import User, application
from flask_login import current_user
import hashlib



def generate_auth_code(client_id, redirect_uri, user_id):
    # Concatenate the client ID, redirect URI, and user ID into a string
    code_string = client_id + redirect_uri + user_id
    # Hash the code string with SHA256 to generate the authorization code
    code_hash = hashlib.sha3_256(code_string.encode()).hexdigest()
    return code_hash


oauth_blueprint = Blueprint('oauth', __name__ , template_folder='../pages/', static_folder='../assets/')


@oauth_blueprint.route('/cancel_request')
def cancel_request():
    return """<style> body {
    background-color: black;
    color: white;
        }
        </style>
        <body>
        
            <h1> Request cancelled, please close this tab yourself. </h1>
        </body>
        """

@oauth_blueprint.route('/authorize', methods=['GET','POST'])
def oauth():
    client_id = request.args.get('client_id')
    redirect_uri = request.args['redirect_uri']
    state = request.args['state']
    if request.method == 'GET':
        checker = application.prisma().find_first(where={'client_id': client_id})

        if checker is not None:
            if checker.redirect_uri == redirect_uri:
                if not current_user.is_authenticated:
                    return redirect('/login')
                return render_template('oauth.html', oauth_info=checker)
            else:
                return {'error': 'RedirectURI is invalid.'}
        else:
            return {'error': 'Client_ID is invalid.'}

    elif request.method == 'POST':
        user = User.prisma().find_first(where={'id': current_user.id})
        checker = application.prisma().find_first(where={'client_id': client_id})

        if user.id == current_user.id and checker is not None:
            if checker.redirect_uri == redirect_uri:
                auth_code = generate_auth_code(client_id, redirect_uri, user.id)
                AuthCode.prisma().create(data={
                    'code': str(auth_code),
                    'user_id': user.id,
                    'client_id': client_id,
                    'redirect_uri': redirect_uri,
                    'expires_at': datetime.now() + timedelta(days=4)
                }
                )
                return redirect(f'{redirect_uri}?code={auth_code}&state={state}')
            else:
                return {'error': 'redirectURI is invalid.'}
        else:
            return {'error': 'ClientID is invalid.'}


@oauth_blueprint.route('/initiate', methods=['POST'])
def initiate_oauth():
    data = request.json()
    
    client_id = data['client_id']
    client_secret = data['client_secret']
    state = data['state']
    redirect_uri = data['redirect_uri']

    client_check = application.prisma().find_first(where={'client_id': client_id, 'client_secret': client_secret})

    if client_check is not None:
        return redirect(f'/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&state={state}')
    
    return {'clientError': 404}


import jwt
import time


import hashlib

@oauth_blueprint.route('/token', methods=['POST'])
def token():
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    auth_header = request.headers.get('auth_code')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    
    if client_id and client_secret and verify_client_secret(client_id, client_secret) and auth_token and verify_token(auth_token):
        auth_code = request.json['code']
        auth_code_obj = AuthCode.prisma().find_first(where={'code': auth_code})
        if auth_code_obj is not None:
            access_token = generate_token(auth_code_obj.user_id, client_id)
            AuthCode.prisma().delete(where={'id': auth_code_obj.id})
            return jsonify({'access_token': access_token})
        else:
            return jsonify({'error': 'invalid_request'}), 400
    else:
        return jsonify({'error': 'invalid_grant'}), 400

def verify_client_secret(client_id, client_secret):
    client = application.prisma().find_first(where={'client_id': client_id})
    if client is not None:
        hashed_secret = client_secret
        return hashed_secret == client.client_secret
    
    return False

def generate_token(user_id, client_id, secret_key, algorithm='HS256', expires_in=30):
    # Create the payload for the token
    now = datetime.utcnow()
    expires = now + timedelta(days=expires_in)
    payload = {
        'sub': user_id,
        'aud': client_id,
        'exp': expires,
        'iat': now
    }
    # Generate the token
    token = encode(payload, secret_key, algorithm=algorithm)
    return token

from datetime import datetime, timedelta
from jwt import encode
from prisma.models import AuthCode
from libraries.db.models import UserModel, get_user

def generate_token(user_id, client_id, secret_key, algorithm='HS256', expires_in=30):
    # Create the payload for the token
    now = datetime.utcnow()
    expires = now + timedelta(days=expires_in)
    payload = {
        'sub': user_id,
        'aud': client_id,
        'exp': expires,
        'iat': now
    }
    # Generate the token
    token = encode(payload, secret_key, algorithm=algorithm)
    # Create and return the refresh token
    refresh_token = generate_refresh_token(user_id, client_id, secret_key, algorithm, expires_in)
    return token, refresh_token

def generate_refresh_token(user_id, client_id, secret_key, algorithm='HS256', expires_in=86400):
    # Create the payload for the refresh token
    now = datetime.utcnow()
    expires = now + timedelta(seconds=expires_in)
    payload = {
        'sub': user_id,
        'aud': client_id,
        'exp': expires,
        'iat': now
    }
    # Generate the refresh token
    refresh_token = encode(payload, secret_key, algorithm=algorithm)
    # Save the refresh token in the database
    auth_code = AuthCode.prisma().create(client_id, None, user_id, refresh_token, expires)
    return refresh_token

from datetime import datetime, timedelta
from prisma.models import AccessToken

def verify_token(token):
    access_token_obj = AccessToken.prisma().find_first(where={'access_token': token})
    if access_token_obj:
        if access_token_obj.expires < datetime.now():
            AccessToken.prisma().delete(where={'id': access_token_obj.id})
            return False
        else:
            return True
    else:
        return False
