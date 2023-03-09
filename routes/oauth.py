from flask import Blueprint, request, render_template, redirect
from prisma.models import User
from flask_login import login_user, logout_user, login_required, current_user
from libraries.db.models import UserModel, get_user
import hashlib

oauth_blueprint = Blueprint('oauth', __name__ , template_folder='../pages/', static_folder='../assets/')

@oauth_blueprint.route('/', methods=['GET','POST'])
def oauth():
  if request.method == 'GET':
    if current_user.is_authenticated:
      return redirect('/dashboard')
    return render_template('oauth.html')

  if request.method == 'POST':
    data = request.form
    dk = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
    data = {'email': data['email'], 'password': dk}
    if data is None:
      return render_template('login.html')
    user = get_user(data['email'])
    if user is None:
      return render_template('login.html')
    if user.password != dk:
      print('error')
      return render_template('login.html')
    login_user(UserModel(user))
    return redirect('/dashboard')