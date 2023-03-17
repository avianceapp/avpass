from flask import Blueprint, url_for,request,abort,jsonify, render_template, redirect
from datetime import datetime
from prisma.models import resetKey, User
reset_blueprint = Blueprint('reset_password', __name__ , template_folder='../pages/', static_folder='../assets/')
import hashlib, random
import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from libraries.essentials.getenv import get_env

username = get_env('email_username')
password = get_env('email_password')


def send_reset_email(you, token):
  try: 
    smtp = smtplib.SMTP('mail.smtp2go.com', 2525) 
    smtp.starttls() 
    smtp.login(username, password)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your password reset request"
    msg['From'] = 'noreply@aviance.app'
    msg['To'] = you
    text = f"aviance.\n\n Hi there,\nA password reset request has been sent to us for this email. \nPlease visit the https://aviance.app/reset_password/verification?token_id={token} site to reset your password. If you didn't make this request, then you can safely ignore this emai.\n\nSincerely regards,\ndf.\nDirector of Software Engineering @aviance."
    html = f"""\
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap" rel="stylesheet">
    </head>
    <body>
    	<h1 style="text-align: center; font-family: 'Poppins', sans-serif; font-size: 50px;">aviance.</h1>
        <br>
        Hi there,
        A password reset request has been sent to us for this email.
        Please visit the <a href="https://aviance.app/reset_password/verification?token_id={token}">link</a> to reset your password. If this wasn't you who made this request, please ignore this email. <br><br>Sincerely regards,
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


def generate_random_code():
    letters = 'abcdefghijklmnopqrstuvwxyz'
    random_email = ''.join(random.choice(letters) for i in range(10)) + "@" + ''.join(random.choice(letters) for i in range(7)) + ".com"
    return hashlib.sha256(random_email.encode('utf-8')).hexdigest()


@reset_blueprint.route('/', methods=['GET','POST'])
def reset_pass():
  if request.method == 'GET':
    return render_template('reset_password.html')

  if request.method == 'POST':
    r = request.form
    code = generate_random_code()
    resetKey.prisma().create(
      data= {
        'token': code,
        'email': r['reset_email']
      }
    )
    
    send_reset_email(r['reset_email'], code)
    return render_template('reset_passwordconf.html')

@reset_blueprint.route('/verification', methods=['GET', 'POST'])
def reset_pass_key(token_id):
  token_id = request.args.get('token_id')
  if request.method == 'GET':
    reset_checker = resetKey.prisma().find_first(where={'token': token_id})
    if reset_checker is None or reset_checker.expired == True:
      return redirect('/login')
    return render_template('reset_password_forms.html', emails = reset_checker.email)
  if request.method == 'POST':
    data = request.form
    new_email = data['email']
    
    new_password = data['password']
    new_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
    User.prisma().update(
      where={
        'email': new_email,
      },
      data= {
        'password': new_password,
      }
    )
    
    reset_checker2 = resetKey.prisma().find_first(where={'token': token_id})

    resetKey.prisma().delete(where = {
      'id': reset_checker2.id,
    }
    )
    return redirect('/login')