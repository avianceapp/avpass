from flask import Blueprint, request, render_template, redirect, flash
from prisma.models import application
from flask_login import login_user, logout_user, current_user
from libraries.db.models import UserModel, get_user
import uuid, hashlib


dashboard_blueprint = Blueprint('dashboard', __name__ , template_folder='../pages/',static_folder='../assets/')

@dashboard_blueprint.route('/', methods=['GET','POST'])
def dashboard():
  if request.method == 'GET':
    if not current_user.is_authenticated:
      return redirect('/login')
    
    if not current_user.admin:
      return render_template('working.html')   
     
    return render_template('dashboard.html',admin_access='Admin Dashboard' if current_user.admin else 'Dashboard', admin_redirect='/admin' if current_user.admin else '/dashboard', admin_icon='fa fa-user-secret' if current_user.admin else 'fa fa-user')
  
@dashboard_blueprint.route('/develop', methods=['GET','POST'])
def application_dev():
  app_created = request.args.get('app_created')

  if request.method == 'GET':
    if not current_user.admin:
      return render_template('working.html')    
    
    if not current_user.is_authenticated:
      return redirect('/login')
    applications = application.prisma().find_many(where={'ownerID': current_user.id})

    for app in applications:
      print(app)

    if not current_user.is_authenticated:
      return redirect('/login')

    if app_created is not None:
      flash("Application has been created successfully!")
      app_info = 'success'
      app_info_icon = 'fa-solid fa-check'
    
    elif app_created is None:
      flash("Welcome to avPass!")
      app_info = 'primary'
      app_info_icon = 'fa-solid fa-circle-info'
    

    if not applications:
      return render_template('develop.html', admin_access='Admin Dashboard' if current_user.admin else 'Dashboard', admin_redirect='/admin' if current_user.admin else '/dashboard', admin_icon='fa fa-user-secret' if current_user.admin else 'fa fa-user')
    
    return render_template('develop.html', admin_access='Admin Dashboard' if current_user.admin else 'Dashboard', admin_redirect='/admin' if current_user.admin else '/dashboard', admin_icon='fa fa-user-secret' if current_user.admin else 'fa fa-user', app_info=app_info, app_info_icon=app_info_icon, applications=applications)


  if request.method == 'POST':

    if not current_user.is_authenticated:
      return redirect('/login')

    if not current_user.admin:
      return render_template('working.html')    
    
    data = request.form
    app_name = data['app']
    description = data['description']
    client_sec = str(hashlib.sha3_256(str(uuid.uuid4()).encode('utf-8')).hexdigest())
    client_id = str(uuid.uuid4())
    e = application.prisma().create(
      data= {
      'ownerID': current_user.id,
      'name': app_name,
      'client_id': client_id,
      'client_secret': hashlib.sha3_256(client_sec.encode('utf-8')).hexdigest(),
      'description': description
      }
    )
    return redirect(f'/dashboard/develop/app?app_id={e.id}&client_secret={client_sec}')


@dashboard_blueprint.route('/app/key_management/', methods=['GET','POST'])
def resetsecretkey():
  app_id = request.args.get('app_id')

  if request.method == 'GET':

    if not current_user.admin:
      return render_template('working.html')    
    
    if not current_user.is_authenticated:
      return redirect('/login')
    
    app = application.prisma().find_first(where={'id': app_id, 'ownerID': current_user.id})

    if app is None:
      return redirect(f'/dashboard/app?app_id={app_id}')

    client_sec = hashlib.sha3_256(str(uuid.uuid4()).encode('utf-8')).hexdigest()
    application.prisma().update(where={'id': app_id}, data={'client_secret': hashlib.sha3_256(client_sec.encode('utf-8')).hexdigest()})
    return redirect(f'/dashboard/develop/app?app_id={app_id}&client_secret={client_sec}')

@dashboard_blueprint.route('/develop/app', methods=['GET','POST'])
def appl_id():
  app_id = request.args.get('app_id')
  client_secret = request.args.get('client_secret')
  client_seccopy = ''
  client_secmessage = 'For security reasons, this code will not be shown again. Make sure you copy the key before you lose it!'
  if client_secret is None:
    client_secret = '*****************'
    client_secmessage = 'For security reasons, this code will not be shown. Press the reset key button to reset the key.'
    client_seccopy = 'disabled'

  if request.method == 'GET':
    if not current_user.admin:
      return render_template('working.html')    
    
    if not current_user.is_authenticated:
      return redirect('/login')
    # try:
    app = application.prisma().find_first(where={'id': app_id, 'ownerID': current_user.id})
    
    if app is None:
      return render_template('errors/404.html')

    if not current_user.is_authenticated:
      return redirect('/login')

    redirect_forreset = '/dashboard/app/key_management?app_id=' + app_id

    return render_template('application.html',admin_access='Admin Dashboard' if current_user.admin else 'Dashboard', admin_redirect='/admin' if current_user.admin else '/dashboard', admin_icon='fa fa-user-secret' if current_user.admin else 'fa fa-user', app=app, redirect_forreset=redirect_forreset, client_secret=client_secret, client_seccopy=client_seccopy, client_secmessage=client_secmessage)
    # except:
    #   return render_template('errors/404.html')


  if request.method == 'POST':
    if not current_user.admin:
      return render_template('working.html')    
    
    data = request.form
    redirect_uri = data['redirect_uri']

    if not current_user.is_authenticated:
      return redirect('/login')
    
    try:
      application.prisma().update(where={'id': app_id}, data={'redirect_uri': redirect_uri})
      return redirect(f'/dashboard/develop/app?app_id={app_id}')
    except:
      return render_template('errors/404.html')