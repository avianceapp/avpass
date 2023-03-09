from flask import Blueprint, request, render_template, redirect
from prisma.models import User
import hashlib

user_blueprint = Blueprint('register', __name__ , template_folder='../pages/', static_folder='../assets/')

@user_blueprint.route('/', methods=['GET','POST'])
def list_create():
  if request.method == 'POST':
    data = request.form
    print(data)
    if data is None:
      return

    name = data.get('username')
    email = data.get('email')
    password = data.get('password')
    password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    if name is None or email is None:
      return {"error": "You need to provide name and email"}
    try:
      check = User.prisma().find_first(where={'email':email})
      if check.email == email:
        return render_template('register.html')
    except:
      user = User.prisma().create(data={'email': email, 'username': name, 'password': password, 'admin': True})

    return redirect('/login')
  return render_template('register.html')
