from flask_login import UserMixin, login_manager
from prisma.models import User

def get_user(email):
    user = User.prisma().find_first(where={'email': email})
    return user
class UserModel(UserMixin):
    def __init__(self, user):
        self.id = user.id
        self.email = user.email
        self.password = user.password
        self.name = user.username
        self.is_admin = user.admin
        self.active = user.active
        #1. Make this AttributeError: 'User' object has no attribute 'is_authenticated' go away
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.email)
    @property
    def is_active(self):
        return self.active
    @property
    def is_authenticated(self):
        return True
    @property
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.id
    @staticmethod
    def get(user_id):
        user = User.prisma().find_first(where={'id': user_id})
        if user is not None:
            return UserModel(user)
        return None
    

from prisma.models import AuthCode

class AuthCodeModel():
    @staticmethod
    def create(client_id, redirect_uri, user_id, code, expires_at, state):
        auth_code = AuthCode.prisma().create(data={'client_id': str(client_id),
                                                   'redirect_uri': redirect_uri,
                                                   'user_id': user_id,
                                                   'state': state,
                                                   'code': code,
                                                   'expires_at': expires_at})
        return auth_code
    @staticmethod
    def get(code):
        auth_code = AuthCode.find_first(where={'code': code})
        return auth_code
