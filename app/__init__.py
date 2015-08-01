from flask import Flask

#from flask_login import LoginManager 

#def register_blueprint(app):
#    print "start create_app %s" % __name__
#    app.register_blueprint(index_page, prefix='/')
#    app.register_blueprint(account_page, prefix='/account')
#    app.register_blueprint(session_page, prefix='/session')

def init_db(app):
    print "start init db %s" % __name__
    db.init_app(app)
    app.db = db

print "start create_app %s" % __name__
app = Flask(__name__)
app.config.from_pyfile('config.py')

#register_blueprint(app)
#init_db(app)

#lm = LoginManager()
#lm.init_app(app)

from views import * 
from models import * 
