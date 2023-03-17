from flask import Blueprint, request, render_template, redirect
from prisma.models import User
from flask_login import login_user, logout_user, login_required, current_user
from libraries.db.models import UserModel, get_user
import hashlib

login_blueprint = Blueprint('login', __name__ , template_folder='../pages/', static_folder='../assets/')

@login_blueprint.route('/', methods=['GET','POST'])
def login():
  redirecttion = request.args.get('redirect')
  redirectstate = request.args.get('state')
  redirecturi = request.args.get('redirect_uri')

  if redirectstate is not None and redirectstate is not None and redirecturi is not None:
    redirecttion = f"{redirecttion}&redirect_uri={redirecturi}&state={redirectstate}"

  if redirecttion is None or redirectstate is None or redirecturi is None:
    redirecttion = '/dashboard'

  redirect_register = f'/register?redirect={redirecttion}'

  if request.method == 'GET':
    if current_user.is_authenticated:
      return redirect('/dashboard')
    return render_template('login.html', redirect_register=redirect_register)
  
  if request.method == 'POST':
    data = request.form
    dk = hashlib.sha3_256(data['password'].encode('utf-8')).hexdigest()
    data = {'email': data['email'], 'password': dk}
    if data is None:
      return render_template('login.html', redirect_register=redirect_register)
    user = get_user(data['email'])
    if user is None:
      return render_template('login.html', redirect_register=redirect_register)
    if user.password != dk:
      print('error')
      return render_template('login.html', redirect_register=redirect_register)
    login_user(UserModel(user))

    return redirect(redirecttion)
