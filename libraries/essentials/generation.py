import random
import string

def randomString(stringLength=32):
    """Generate a random string of fixed length """
    letters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(letters) for i in range(stringLength))

with open('.env', 'w') as f:
    f.write('SECRET_KEY = ' + randomString())
    f.close()

with open('.env', 'r') as f:
    print(f.read())
    f.close()