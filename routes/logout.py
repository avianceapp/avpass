from flask import Blueprint, request, redirect
from prisma.models import User
from flask_login import logout_user
logout_blueprint = Blueprint('logout', __name__ , template_folder='../pages/')

@logout_blueprint.route('/', methods=['GET','POST'])
def logout():
  logout_user()
  return redirect('/login')