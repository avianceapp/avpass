from flask import Blueprint, request, render_template, redirect, jsonify, abort
from prisma.models import User, application
from flask_login import login_user, logout_user, login_required, current_user
from libraries.db.models import UserModel, get_user
import hashlib


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
                AuthCodeModel.create(
                    code=auth_code,
                    user_id=user.id,
                    client_id=client_id,
                    redirect_uri=redirect_uri,
                    state=state,
                    expires_at = datetime.now() + timedelta(days=4)
                )
                return redirect(f'{redirect_uri}?code={auth_code}&state={state}')
            else:
                return {'error': 'redirectURI is invalid.'}
        else:
            return {'error': 'ClientID is invalid.'}
import jwt
import time



@oauth_blueprint.route('/token', methods=['POST'])
def token():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''

    if auth_token and verify_token(auth_token):
        auth_code = request.form['code']
        state = request.form['state']
        auth_code_obj = AuthCodeModel.get(where={'auth_code': auth_code})
        if auth_code_obj and auth_code_obj.state == state:
            access_token = generate_token(auth_code_obj.user_id)
            AuthCodeModel.prisma().delete(where={'id': auth_code_obj.id})
            return jsonify({'access_token': access_token})
        else:
            return jsonify({'error': 'invalid_request'}), 400
    else:
        return jsonify({'error': 'invalid_grant'}), 400


from libraries.db.models import get_user, AuthCodeModel

def verify_auth_code(code):
    # Lookup the authorization code in the database
    auth_code = AuthCodeModel.get_or_none(code=code)
    if auth_code:
        # Check that the code hasn't expired
        if time.time() <= auth_code.expires_at:
            client_id = auth_code.client_id
            redirect_uri = auth_code.redirect_uri
            user_id = auth_code.user_id
            # Delete the authorization code from the database
            auth_code.delete()
            return client_id, redirect_uri, user_id
    return None, None, None

from datetime import datetime, timedelta
from jwt import encode
from prisma.models import AuthCode
from libraries.db.models import UserModel, get_user

def generate_token(user_id, client_id, secret_key, algorithm='HS256', expires_in=3600):
    # Create the payload for the token
    now = datetime.utcnow()
    expires = now + timedelta(seconds=expires_in)
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
    auth_code = AuthCodeModel.create(client_id, None, user_id, refresh_token, expires)
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
