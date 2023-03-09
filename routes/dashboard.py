from flask import Blueprint, request, render_template, redirect
from prisma.models import User
from flask_login import login_user, logout_user, current_user
from libraries.db.models import UserModel, get_user

dashboard_blueprint = Blueprint('dashboard', __name__ , template_folder='../pages/',static_folder='../assets/')

@dashboard_blueprint.route('/', methods=['GET','POST'])
def dashboard():
  if request.method == 'GET':
    if not current_user.is_authenticated:
      return redirect('/login')
    return render_template('dashboard.html',admin_access='Admin Dashboard' if current_user.admin else 'Dashboard', admin_redirect='/admin' if current_user.admin else '/dashboard', admin_icon='fa fa-user-secret' if current_user.admin else 'fa fa-user')