from flask import Blueprint, request, render_template, redirect
from prisma.models import User, registrationVerificationService
from flask_login import login_user, logout_user, login_required, current_user
from libraries.db.models import UserModel, get_user
import hashlib
import smtplib, random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from libraries.essentials.getenv import get_env

admin = True
email = get_env('email_username')
password = get_env('email_password')

def generate_random_code():
    letters = 'abcdefghijklmnopqrstuvwxyz'
    random_email = ''.join(random.choice(letters) for i in range(10)) + "@" + ''.join(random.choice(letters) for i in range(7)) + ".com"
    return hashlib.sha256(random_email.encode('utf-8')).hexdigest()

def send_confirmation_email(you, code, redirect):
  try: 
      abcd = """
      body {
          background-color: #000000;
          color: white;
          margin: auto property;
          text-decoration: none;
          font-family: 'Roboto', sans-serif;
        }
      """
      smtp = smtplib.SMTP('mail.smtp2go.com', 2525) 
      smtp.starttls() 
      smtp.login(email, password)
      msg = MIMEMultipart('alternative')
      msg['Subject'] = "Account verification needed."
      msg['From'] = 'noreply@aviance.app'
      msg['To'] = you
      text = f"aviance.\n\n Please click on the following link for your account to be verified. https://aviance.app/register/confirmation/code={code}/redirect={redirect}\n\nSincerely regards,\ndf.\nDirector of Software Engineering @aviance."
      html = f"""\
      <html>
      <head>
          <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap" rel="stylesheet">
          <style>
            {abcd}
          </style>
      </head>
      <body>
        <h1 style="text-align: center; font-family: 'Poppins', sans-serif; font-size: 50px;">aviance.</h1>
          <p style="text-align: center;">Please click on the following account for your account to be verified.<br>
          Visit the <a href="https://aviance.app/register/confirmation/code={code}/redirect={redirect}">confirmation site</a> to confirm your registration.<br><br>Sincerely regards,
          <br>df.
          <br>Director of Software Engineering @aviance.
          </p>
      </body>
      </html>
      """

      # Record the MIME types of both parts - text/plain and text/html.
      part1 = MIMEText(text, 'plain')
      part2 = MIMEText(html, 'html')

      # Attach parts into message container.
      # According to RFC 2046, the last part of a multipart message, in this case
      # the HTML message, is best and preferred.
      msg.attach(part1)
      msg.attach(part2)
      smtp.sendmail("noreply@aviance.app", you,msg.as_string()) 
      smtp.quit() 


  except Exception as ex: 
      pass


def send_email(you, username):
  try: 
      smtp = smtplib.SMTP('mail.smtp2go.com', 2525) 
      smtp.starttls() 
      smtp.login(email, password)
      msg = MIMEMultipart('alternative')
      msg['Subject'] = "Welcome to aviance! 🥳"
      msg['From'] = 'noreply@aviance.app'
      msg['To'] = you
      text = f"aviance.\n\n Welcome to aviance {username}! 🥳\nWe are so excited for you to join us!\nVisit the \nhttps://aviance.app site to manage aviance services & more.\n\nSincerely regards,\ndf.\nDirector of Software Engineering @aviance."
      html = """\
      <html>
      <head>
          <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap" rel="stylesheet">
          <style>
        body {
          background-color: #000000;
          color: white;
          margin: auto property;
          text-decoration: none;
          font-family: 'Roboto', sans-serif;
        }
          </style>
      </head>
      <body>
        <h1 style="text-align: center; font-family: 'Poppins', sans-serif; font-size: 50px;">aviance.</h1>
          <p style="text-align: center;">Welcome to aviance! 🥳<br>
          We are so excited for you to join us!<br>
          Visit the <a href="https://aviance.app">aviance site</a> to manage aviance services & more.<br><br>Sincerely regards,
          <br>df.
          <br>Director of Software Engineering @aviance.
          </p>
      </body>
      </html>
      """

      # Record the MIME types of both parts - text/plain and text/html.
      part1 = MIMEText(text, 'plain')
      part2 = MIMEText(html, 'html')

      # Attach parts into message container.
      # According to RFC 2046, the last part of a multipart message, in this case
      # the HTML message, is best and preferred.
      msg.attach(part1)
      msg.attach(part2)
      smtp.sendmail("noreply@aviance.app", you,msg.as_string()) 
      smtp.quit() 

  except Exception as ex: 
    pass


user_blueprint = Blueprint('register', __name__ , template_folder='../pages/', static_folder='../assets/')

@user_blueprint.route('/', methods=['GET','POST'])
def register():
  redirecttion = request.args.get('redirect')
  redirectstate = request.args.get('state')
  redirecturi = request.args.get('redirect_uri')

  if redirectstate is not None and redirectstate is not None and redirecturi is not None:
    redirecttion = f"{redirecttion}&redirect_uri={redirecturi}&state={redirectstate}"

  if redirecttion is None or redirectstate is None or redirecturi is None:
    redirecttion = '/login'
  
  if request.method == 'GET':
    redirect_login = f'/login/?redirect={redirecttion}'

    return render_template('register.html', redirect_login=redirect_login)

  if request.method == 'POST':
    data = request.form
    if data is None:
      return

    name = data.get('username')
    email = data.get('email')
    password = data.get('password')
    password = hashlib.sha3_256(password.encode('utf-8')).hexdigest()
    if name is None or email is None:
      return {"error": "You need to provide name and email"}
    try:
      check = User.prisma().find_first(where={'email':email})
      if check.email == email:
        return render_template('register.html')
    except:
      # try:
      code = generate_random_code()
      registrationVerificationService.prisma().create(data={'email': email, 'code': code, 'password': password, 'username': name})
      send_confirmation_email(email, code, redirecttion)
      return render_template('registration_email.html')
      # except:
      #   return redirect('/register')

@user_blueprint.route('/confirmation', methods=['GET', 'POST'])
def verify_code():
  token_id = request.args.get('code')
  redirect_uri = request.args.get('redirect')
  redirectstate = request.args.get('state')
  redirecturi = request.args.get('redirect_uri')
  
  if redirectstate is not None and redirectstate is not None and redirecturi is not None:
    redirecttion = f"{redirecttion}&redirect_uri={redirecturi}&state={redirectstate}"

  if redirecttion is None or redirectstate is None or redirecturi is None:
    redirecttion = redirect_uri

  # try:
  abcd = registrationVerificationService.prisma().find_first(where={'code': token_id})
  if abcd is None:
    return redirect('/register')
  else:
    User.prisma().create(data={'email': abcd.email, 'username': abcd.username, 'password': abcd.password, 'admin': admin})
    send_email(abcd.email, abcd.username)
    user = get_user(abcd.email)
    login_user(UserModel(user))
    registrationVerificationService.prisma().delete_many(where={'code': token_id})
    return redirect(redirecttion)
  # except:
  #   return redirect('/register')