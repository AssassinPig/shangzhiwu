from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from . import app
db = SQLAlchemy()
db.init_app(app)

class Mixin:
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

class User(db.Model, Mixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    #nick = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tel = db.Column(db.String(30),  nullable=False)

    def __repr__(self):
        return 'User %r' % self.name

#basicinfo
class BasicInfo(db.Model, Mixin):
    __tablename__ = 'basicinfo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    intro = db.Column(db.Text)
    mainpic_url = db.Column(db.Text)

#about  1
#course  2
#coach  3 elegant  4
#charge  5
#news  6 industry 7 visited_times  
#video  url keyword   8
# title_pic_url  2 3 4 5 8 has   1 6 7 has not
class MetaInfo(db.Model, Mixin):
    __tablename__ = 'metainfo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), default='default', nullable=False)
    title_pic_url = db.Column(db.Text)
    module_no = db.Column(db.Integer, default=0)
    order_no = db.Column(db.Integer, default=1, nullable=False)
    content = db.Column(db.Text)
    visited_times = db.Column(db.Integer, default=1, nullable=False)
    url = db.Column(db.Text)
    keyword = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @staticmethod
    def getMetaInfo(module_no):
        return MetaInfo.query.filter(MetaInfo.module_no == module_no)

    @staticmethod
    def getAbout():
        return MetaInfo.getMetaInfo(1)

    @staticmethod
    def  getCourse():
        return MetaInfo.getMetaInfo(2)

    @staticmethod
    def  getCoach():
        return MetaInfo.getMetaInfo(3)

    @staticmethod
    def  getElegant():
        return MetaInfo.getMetaInfo(4)

    @staticmethod
    def  getCharge():
        return MetaInfo.getMetaInfo(5)
    @staticmethod
    def  getNews():
        return MetaInfo.getMetaInfo(6)
    @staticmethod
    def  getIndustry():
        return MetaInfo.getMetaInfo(7)
    @staticmethod
    def  getVideo():
        return MetaInfo.getMetaInfo(8)

    def saveCommon(self, title, module_no,  title_pic_url="", order_no=1, content="",  visited_times=1, url="", keyword=""):
        self.title = title
        self.module_no = module_no
        self.order_no = order_no
        self.content = content
        self.visited_times = visited_times
        self.url = url
        self.keyword = keyword
        self.title_pic_url = title_pic_url
        self.save()

class  Branch(db.Model, Mixin):
    __tablename__ = 'branch'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), default='default', nullable=False)
    order_no = db.Column(db.Integer, default=1, nullable=False)
    url = db.Column(db.Text)
    tel = db.Column(db.String(30),  nullable=False)
    address = db.Column(db.Text)
    content = db.Column(db.Text)
    logo_pic = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class  Signup(db.Model, Mixin):
    __tablename__ = 'signup'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), default='default', nullable=False)
    sex = db.Column(db.Integer, default=0, nullable=False)
    mobile = db.Column(db.String(30),  nullable=False)
    email = db.Column(db.String(64),  nullable=False)
    tel = db.Column(db.String(30))
    address = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)
    now_situation = db.Column(db.Integer, default=0)
    has_asked = db.Column(db.Integer, default=0)
    plan_course = db.Column(db.Integer, default=1)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)