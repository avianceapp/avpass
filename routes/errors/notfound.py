from flask import Blueprint, request, render_template, redirect
from prisma.models import User
from flask_login import login_user, logout_user, current_user
from libraries.db.models import UserModel, get_user

notfound_blueprint = Blueprint('404', __name__ , template_folder='../pages/',static_folder='../assets/')

@notfound_blueprint.route('/', methods=['GET','POST'])
def notfound():
    if request.method == 'GET':
        return render_template('/errors/404.html')