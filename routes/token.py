from flask import Blueprint, request, render_template, redirect
from prisma.models import User
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

@oauth_blueprint.route('/authorize?clientid=<client_id>&redirect_uri=<redirect_uri>&state<state>', methods=['GET','POST'])
def oauth(client_id, redirect_uri, state):
  if request.method == 'GET':
    # if current_user.is_authenticated:
    #   return redirect('/dashboard')
    if not current_user.is_authenticated:
      return redirect('/login')
    return render_template('oauth.html')
  if request.method == 'POST':
    data = request.form
    
