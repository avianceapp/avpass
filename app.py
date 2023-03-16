# Import essential imports.
from flask import Flask, render_template, redirect
from flask_login import LoginManager
from prisma import Prisma, register
from prisma.models import User
import uuid, hashlib

# Import routes
from routes.register import user_blueprint
from routes.login import login_blueprint
from routes.logout import logout_blueprint
from routes.dashboard import dashboard_blueprint
from routes.admin import admin_blueprint
from routes.errors.notfound import notfound_blueprint
from routes.oauth import oauth_blueprint

# Connect to the database and register it.
db = Prisma()
db.connect()
register(db)

# Define app
app = Flask(__name__,template_folder='pages/',static_folder='./assets/')

# Setup login manager and secret_key.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = hashlib.sha3_256(str(uuid.uuid4()).encode()).hexdigest()
@app.login_manager.user_loader
def load_user(_id):
    if _id is not None:
      user = User.prisma().find_first(where={'id': _id})
      return user
    else:
      return None
    
# render home
@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')

@app.route('/docs', methods=['GET'])
def documentation():
  return redirect('https://docs.aviance.app/')

# Return 404 page if 404 error recieved.
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html')

# Blueprint Registration
app.register_blueprint(logout_blueprint, url_prefix='/logout')
app.register_blueprint(user_blueprint, url_prefix='/register')
app.register_blueprint(login_blueprint, url_prefix='/login')
app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(notfound_blueprint, url_prefix='/404')
app.register_blueprint(oauth_blueprint, url_prefix='/oauth')

#oauth_blueprint


# Run App
if __name__ == "__main__":
  app.run(debug=True, port=3000, threaded=True)
