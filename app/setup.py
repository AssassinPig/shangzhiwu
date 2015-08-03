# coding=utf-8
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/shangzhiwu'
db = SQLAlchemy(app)
#db.init_app(app)

#import MySQLdb as mdb
#con = None


class Mixin:
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

class MetaInfo(db.Model, Mixin):
    __tablename__ = 'metainfo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), default='default', nullable=False)
    title_pic_url = db.Column(db.Text)
    module_no = db.Column(db.Integer, default=0)
    submodule_no = db.Column(db.Integer, default=0)
    order_no = db.Column(db.Integer, default=1, nullable=False)
    content = db.Column(db.Text)
    visited_times = db.Column(db.Integer, default=1, nullable=False)
    url = db.Column(db.Text)
    keyword = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


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



class BasicInfo(db.Model, Mixin):
    __tablename__ = 'basicinfo'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    intro = db.Column(db.Text)
    mainpic_url = db.Column(db.Text)

class User(db.Model, Mixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    #nick = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tel = db.Column(db.String(30),  nullable=False)


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

def convertUTF8():
    try:
        # 连接mysql的方法：connect('ip','user','password','dbname')
        con = mdb.connect('localhost', 'root',
            '6528e7f8d4', 'shangzhiwu');

        # 所有的查询，都在连接con的一个模块cursor上面运行的
        cur = con.cursor()
        cur.execute('ALTER TABLE metainfo CONVERT TO CHARACTER SET utf8;')
        cur.execute('ALTER TABLE branch CONVERT TO CHARACTER SET utf8;')
        cur.execute('ALTER TABLE signup CONVERT TO CHARACTER SET utf8;')
        cur.execute('ALTER TABLE basicinfo CONVERT TO CHARACTER SET utf8;')
        cur.execute('ALTER TABLE user CONVERT TO CHARACTER SET utf8;')
        
        #insert into user values(1, 'admin', 'abc@gmail.com', '123456', '18616991234' )
        cur.execute('insert into user values(1, \'admin\', \'abc@gmail.com\', \'123456\', \'18616991234\' )')
        data = cur.fetchone()

        #insert into basicinfo values(1, 'shangzhiwu', 'introduction', 'http://www.abc.com/pic' )
        cur.execute('insert into basicinfo values(1, \'shangzhiwu\', \'introduction\', \'http://www.abc.com/pic\' )')
	cur.close()
	con.commit()

        print "Database version : %s " % data
    finally:
        if con:
            # 无论如何，连接记得关闭
            con.close()    

if __name__ == '__main__':
    #db.drop_all()
    db.create_all()
    #convertUTF8()
