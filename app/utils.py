import md5
from flask import session
from models import User
def login_user(user):
    session['id'] = user.id
    m = md5.new()
    m.update(str(user.id))
    m.update(user.password)
    session['token'] = m.digest() 

def logout_user(user):
    session.pop('id')
    session.pop('token')

def current_user():
    if session.get('id'):
        user = User.query.get(session['id'])
        if user is None:
            return None
        else:
            m = md5.new()
            m.update(str(user.id))
            m.update(user.password)
            if session['token'] == m.digest() : 
                return user
            else:
                return None

    return None
