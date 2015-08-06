# coding=utf-8
from flask import render_template, Blueprint, abort
from flask import g, request, flash, current_app, redirect, url_for
from flask import Flask, request, render_template, url_for, make_response
from flask import jsonify

from app import app 
from models import *

from utils import current_user, login_user, logout_user

from uploader import Uploader

from werkzeug import secure_filename

import json
import os
import re

from sqlalchemy import update

@app.before_request
def before_request():
    g.user = current_user()


def getRedirectUrl(module_no):
    redirect_url = ''
    if module_no == 1:
        redirect_url  =  '/admin/about/'
    if module_no == 2:
        redirect_url  =  '/admin/course/'
    if module_no == 3:
        redirect_url  =  '/admin/coach/'
    if module_no == 4:
        redirect_url  =  '/admin/elegant/'
    if module_no == 5:
        redirect_url  =  '/admin/charge/'
    if module_no == 6:
        redirect_url  =  '/admin/news/'
    if module_no == 7:
        redirect_url  =  '/admin/industry/'
    if module_no == 8:
        redirect_url  =  '/admin/video/'
    
    return redirect_url

@app.route('/admin/')
def admin_index():
    user = current_user()
    if user is None:
        error = 'no login'
        return render_template('admin/login.html')
    else:
        return redirect('/admin/basicinfo')

@app.route('/admin/login/', methods=['GET', 'POST'])
def login():
    error = None 
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(name=username).first()  
        if user is None:
            error = 'username invalidate'
        else:
            if user.password == password:
                login_user(user)
            else:
                error = 'password invalidate'
            return redirect('/admin/')
    else:
        return render_template('admin/login.html')

@app.route('/admin/logout', methods=['GET', 'POST'])
def logout():
    error = None 
    if request.method == 'POST':
        logout_user(g.user)
        g.user = None
    else:
        logout_user(g.user)
        g.user = None
        error = 'validation failed' 
    return redirect('/admin')

@app.route('/admin/user/')
def user():
    if g.user == None:
        return redirect('/admin/')

    users = User.query.all()
    return render_template('admin/user.html', users = users)

@app.route('/admin/user_new', methods=['GET', 'POST'])
def user_new():
    if g.user == None:
        return redirect('/admin/')

    if request.method == 'POST':
        user = User()
        user.name = request.form['name']
        user.email = request.form['email']
        user.tel = request.form['tel']
        user.password = request.form['password']
        user.confirm = request.form['confirm']
        user.save()
        return redirect('/admin/user/')
    else:
        user = None
        return render_template('admin/user_form.html', user=user)

@app.route('/admin/user_delete/<user_id>', methods=['GET', 'DELETE'])
def user_delete(user_id):
    if g.user == None:
        return redirect('/admin/')

    user = User.query.filter_by(id=user_id).first()
    if user != None:
        user.delete()
    return redirect('/admin/user/')

@app.route('/admin/user_edit/<user_id>', methods=['GET', 'POST']) 
def user_edit(user_id):
    if g.user == None:
        return redirect('/admin/')

    user = User.query.filter_by(id=user_id).first()
    if user != None:
        if  request.method == 'POST':
            user.name = request.form['name']
            user.email = request.form['email']
            user.tel = request.form['tel']
            user.password = request.form['password']
            user.confirm = request.form['confirm']
            user.save()
            return redirect('/admin/user')
        else:
            return render_template('admin/user_form.html', user=user)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    if g.user == None:
        return redirect('/admin/')

    mimetype = 'application/json'
    result = {}
    action = request.args.get('action')

    # 解析JSON格式的配置文件
    with open(os.path.join(app.static_folder, 'ueditor', 'php',
                           'config.json')) as fp:
        try:
            # 删除 `/**/` 之间的注释
            CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
        except:
            CONFIG = {}

    if action == 'config':
        # 初始化时，返回配置文件给客户端
        result = CONFIG

    elif action in ('uploadimage', 'uploadfile', 'uploadvideo'):
        # 图片、文件、视频上传
        if action == 'uploadimage':
            fieldName = CONFIG.get('imageFieldName')
            config = {
                "pathFormat": CONFIG['imagePathFormat'],
                "maxSize": CONFIG['imageMaxSize'],
                "allowFiles": CONFIG['imageAllowFiles']
            }
        elif action == 'uploadvideo':
            fieldName = CONFIG.get('videoFieldName')
            config = {
                "pathFormat": CONFIG['videoPathFormat'],
                "maxSize": CONFIG['videoMaxSize'],
                "allowFiles": CONFIG['videoAllowFiles']
            }
        else:
            fieldName = CONFIG.get('fileFieldName')
            config = {
                "pathFormat": CONFIG['filePathFormat'],
                "maxSize": CONFIG['fileMaxSize'],
                "allowFiles": CONFIG['fileAllowFiles']
            }

        if fieldName in request.files:
            field = request.files[fieldName]
            uploader = Uploader(field, config, app.static_folder)
            result = uploader.getFileInfo()
        else:
            result['state'] = '上传接口出错'

    elif action in ('uploadscrawl'):
        # 涂鸦上传
        fieldName = CONFIG.get('scrawlFieldName')
        config = {
            "pathFormat": CONFIG.get('scrawlPathFormat'),
            "maxSize": CONFIG.get('scrawlMaxSize'),
            "allowFiles": CONFIG.get('scrawlAllowFiles'),
            "oriName": "scrawl.png"
        }
        if fieldName in request.form:
            field = request.form[fieldName]
            uploader = Uploader(field, config, app.static_folder, 'base64')
            result = uploader.getFileInfo()
        else:
            result['state'] = '上传接口出错'

    elif action in ('catchimage'):
        config = {
            "pathFormat": CONFIG['catcherPathFormat'],
            "maxSize": CONFIG['catcherMaxSize'],
            "allowFiles": CONFIG['catcherAllowFiles'],
            "oriName": "remote.png"
        }
        fieldName = CONFIG['catcherFieldName']

        if fieldName in request.form:
            # 这里比较奇怪，远程抓图提交的表单名称不是这个
            source = []
        elif '%s[]' % fieldName in request.form:
            # 而是这个
            source = request.form.getlist('%s[]' % fieldName)

        _list = []
        for imgurl in source:
            uploader = Uploader(imgurl, config, app.static_folder, 'remote')
            info = uploader.getFileInfo()
            _list.append({
                'state': info['state'],
                'url': info['url'],
                'original': info['original'],
                'source': imgurl,
            })

        result['state'] = 'SUCCESS' if len(_list) > 0 else 'ERROR'
        result['list'] = _list

    else:
        result['state'] = '请求地址出错'

    result = json.dumps(result)

    if 'callback' in request.args:
        callback = request.args.get('callback')
        if re.match(r'^[\w_]+$', callback):
            result = '%s(%s)' % (callback, result)
            mimetype = 'application/javascript'
        else:
            result = json.dumps({'state': 'callback参数不合法'})

    res = make_response(result)
    res.mimetype = mimetype
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
    return res

@app.route('/admin/about/')
def admin_about():
    if g.user == None:
        return redirect('/admin/')

    metainfos = MetaInfo.getAbout()
    return render_template('admin/metainfo.html', metainfos=metainfos, module_no=1)

@app.route('/admin/course/')
def admin_course():
    if g.user == None:
        return redirect('/admin/')

    metainfos = MetaInfo.getCourse()
    return render_template('admin/metainfo.html', metainfos=metainfos, module_no=2)

@app.route('/admin/coach/')
def admin_coach():
    if g.user == None:
        return redirect('/admin/')    
    metainfos = MetaInfo.getCoach()
    return render_template('admin/metainfo.html', metainfos=metainfos, module_no=3)

@app.route('/admin/elegant/')
def admin_elegant():
    if g.user == None:
        return redirect('/admin/')    
    metainfos = MetaInfo.getElegant()
    return render_template('admin/metainfo.html', metainfos=metainfos, module_no=4)

@app.route('/admin/charge/')
def admin_charge():
    if g.user == None:
        return redirect('/admin/')
    metainfos = MetaInfo.getCharge()
    return render_template('admin/metainfo.html', metainfos=metainfos, module_no=5)

@app.route('/admin/news/')
def admin_news():
    if g.user == None:
        return redirect('/admin/')    
    metainfos = MetaInfo.getNews()
    return render_template('admin/metainfo.html', metainfos=metainfos, module_no=6)

@app.route('/admin/industry/')
def admin_industry():
    if g.user == None:
        return redirect('/admin/')    
    metainfos = MetaInfo.getIndustry()
    return render_template('admin/metainfo.html', metainfos=metainfos, module_no=7)

@app.route('/admin/video/')
def admin_video():
    if g.user == None:
        return redirect('/admin/')    
    metainfos = MetaInfo.getVideo()
    return render_template('admin/metainfo.html', metainfos=metainfos, module_no=8)

@app.route('/admin/metainfo_new/<int:module_no>', methods=['GET', 'POST'])
def metainfo_new(module_no):
    if g.user == None:
        return redirect('/admin/')    
    if request.method == 'POST':
        title = request.form['title']
        order_no = request.form['order_no']
        content = request.form['content']
        visited_times = 1
        url = ""
        keyword = ""
        title_pic_url = ""

        if module_no == 6 or module_no == 7:
            visited_times = request.form['visited_times']
        if module_no == 8:
            url = request.form['url']
            keyword = request.form['keyword']

        file = request.files['file']
        if module_no != 1 and module_no != 6 and module_no != 7:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filename)
                title_pic_url = filename
                title_pic_url = title_pic_url[3:]

        metainfo = MetaInfo()
        metainfo.saveCommon(title=title, title_pic_url=title_pic_url, module_no=module_no, order_no=order_no, content=content, visited_times=visited_times, url=url, keyword=keyword)
        metainfo.save()

        redirectUrl = getRedirectUrl(module_no)
        return redirect(redirectUrl)
    else:
        metainfo = None
        return render_template('admin/metainfo_form.html', metainfo=metainfo, module_no=module_no)

@app.route('/admin/metainfo_delete/<int:metainfo_id>', methods=['GET', 'DELETE'])
def  metainfo_delete(metainfo_id):
    if g.user == None:
        return redirect('/admin/')    
    metainfo = MetaInfo.query.filter_by(id=metainfo_id).first()
    redirectUrl = getRedirectUrl(metainfo.module_no)

    if metainfo  != None:
        metainfo.delete()
    return redirect(redirectUrl)

@app.route('/admin/metainfo_edit/<int:metainfo_id>', methods=['GET', 'POST']) 
def metainfo_edit(metainfo_id):
    if g.user == None:
        return redirect('/admin/')    
    metainfo = MetaInfo.query.filter_by(id=metainfo_id).first()
    if metainfo != None:
        if  request.method == 'POST':

            title = request.form['title']
            order_no = request.form['order_no']
            content = request.form['content']

            visited_times = 1
            url = ""
            keyword = ""
            title_pic_url = metainfo.title_pic_url 

            module_no = metainfo.module_no 
            if module_no == 6 or module_no == 7:
                visited_times = request.form['visited_times']
            if module_no == 8:
                url = request.form['url']
                keyword = request.form['keyword']

            if module_no != 1 and module_no != 6 and module_no != 7:
                file = request.files['file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filename)
                    title_pic_url = filename
                    title_pic_url = title_pic_url[3:]

            metainfo.saveCommon(title=title, title_pic_url=title_pic_url, module_no=module_no, order_no=order_no, content=content, visited_times=visited_times, url=url, keyword=keyword)
            metainfo.save()

            redirectUrl = getRedirectUrl(module_no)
            return redirect(redirectUrl)
        else:
            return render_template('admin/metainfo_form.html', metainfo=metainfo)

@app.route('/admin/basicinfo/')
def basicinfo():
    if g.user == None:
        return redirect('/admin/')    
    basicinfos = BasicInfo.query.all()
    if basicinfos != None:
        return render_template('/admin/basicinfo.html', basicinfos=basicinfos)
    else:
        redirect('/admin/basicinfo_new')

@app.route('/admin/basicinfo_new', methods=['GET', 'POST'])
def basicinfo_new():
    if g.user == None:
        return redirect('/admin/')    
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filename)
            basicinfo = BasicInfo()
            basicinfo.title = request.form['title']
            basicinfo.intro = request.form['intro']
            basicinfo.mainpic_url = filename[3:]
            basicinfo.save()
        return redirect('/admin/basicinfo/')
    else:
        basicinfo = None
        return render_template('/admin/basicinfo_form.html', basicinfo=basicinfo)

@app.route('/admin/basicinfo_edit/<basicinfo_id>', methods=['GET', 'POST'])
def basic_edit(basicinfo_id):
    if g.user == None:
        return redirect('/admin/')    
    basicinfo = BasicInfo.query.filter_by(id=basicinfo_id).first()
    if request.method == 'POST':
        #if module_no != 1 and module_no != 6 and module_no != 7:
	file = request.files['file']
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(filename)

		basicinfo.title = request.form['title']
		basicinfo.intro = request.form['intro']
		basicinfo.mainpic_url = filename[3:]
		basicinfo.save()
        return redirect('/admin/')
    else:
        return render_template('/admin/basicinfo_form.html', basicinfo=basicinfo)

@app.route('/admin/branch')
def admin_branch():
    if g.user == None:
        return redirect('/admin/')    
    branches = Branch.query.all()
    return render_template('/admin/branch.html', branches = branches)

@app.route('/admin/branch_new', methods=['GET', 'POST'])
def branch_new():
    if g.user == None:
        return redirect('/admin/')    
    if request.method == 'POST':
        branch = Branch()
        branch.title            = request.form['title']
        branch.order_no = request.form['order_no']
        branch.url = request.form['url']
        branch.tel = request.form['tel']
        branch.address = request.form['address']
        branch.content = request.form['content']
        branch.logo_pic = request.form['logo_pic']
        branch.save()
        return redirect('/admin/branch')
    else:
        branch = None
        return render_template('/admin/branch_form.html', branch=branch)

@app.route('/admin/branch_edit/<branch_id>',  methods=['GET', 'POST'])
def branch_edit(branch_id):
    if g.user == None:
        return redirect('/admin/')    
    branch = Branch.query.filter_by(id = branch_id).first()
    if branch != None:
        if request.method == 'POST':
            branch.title            = request.form['title']
            branch.order_no = request.form['order_no']
            branch.url = request.form['url']
            branch.tel = request.form['tel']
            branch.address = request.form['address']
            branch.content = request.form['content']
            branch.logo_pic = request.form['logo_pic']
            branch.save()
            return redirect('/admin/branch')
        else:
            return render_template('/admin/branch_form.html', branch=branch)
    else:
        redirect('/admin/branch')
    
@app.route('/admin/branch_delete/<branch_id>', methods=['GET', 'POST'])
def branch_delete(branch_id):
    if g.user == None:
        return redirect('/admin/')    
    branch = Branch.query.filter_by(id = branch_id).first()
    if branch != None:
        branch.delete()
    return redirect('/admin/branch')

@app.route('/admin/signup/')
def admin_signup():
    if g.user == None:
        return redirect('/admin/')    
    signups = Signup.query.all()
    courses = []

    for s in signups:
        c = MetaInfo.query.filter_by(id = s.plan_course).first()
        s.plan_course = c

    return render_template('/admin/signup.html', signups = signups)

@app.route('/signup_new/', methods=['GET', 'POST'])
def signup_new():
    #if g.user == None:
    #    return redirect('/admin/')    
    if request.method == 'POST':
        #print request.form
        signup = Signup()
        signup.name = request.form['name']
        signup.sex = request.form['sex']
        signup.mobile = request.form['mobile']
        signup.email = request.form['email']
        signup.tel = request.form['tel']
        signup.address = request.form['address']
        signup.content = request.form['content']
        signup.now_situation = request.form['now_situation']
        signup.has_asked = request.form['has_asked']
        signup.plan_course = request.form['plan_course']
        signup.save()
        return redirect('/')
    else:
        signup = None
        course = MetaInfo.getCourse()
    return render_template('/admin/signup_form.html', signup = signup, course=course)

@app.route('/admin/signup_edit/<signup_id>', methods=['GET', 'POST'])
def signup_edit(signup_id):
    if g.user == None:
        return redirect('/admin/')    
    signup = Signup.query.filter_by(id=signup_id).first()
    if signup != None:
        if request.method == 'POST':
            signup.name = request.form['name']
            signup.sex = request.form['sex']
            signup.tel = request.form['tel']
            signup.address = request.form['address']
            signup.content = request.form['content']
            signup.now_situation = request.form['now_situation']
            signup.has_asked = request.form['has_asked']
            signup.plan_course = request.form['plan_course']
            signup.save()
            return redirect('/admin/signup')
        else:
            course = MetaInfo.getCourse()
            return render_template('/admin/signup_form.html', signup = signup, course=course)
    else:
        return redirect('/admin/signup')

@app.route('/admin/signup_delete/<signup_id>', methods=['GET', 'DELETE'])
def signup_delete(signup_id):
    if g.user == None:
        return redirect('/admin/')    
    signup = Signup.query.filter_by(id=signup_id).first()
    if signup != None:
        signup.delete()
    return redirect('/admin/signup')

@app.route('/')
@app.route('/index/')
def home():
    basicinfo = BasicInfo.query.one()
    courses = MetaInfo.getCourse()
    news = MetaInfo.getNews().limit(5)
    industrys = MetaInfo.getIndustry().limit(5)
    videos = MetaInfo.getVideo()
    charges = MetaInfo.getCharge()
    coaches = MetaInfo.getCoach()
    elegants = MetaInfo.getElegant()
    branches = Branch.query.all()
    return render_template('index.html', 
        basicinfo= basicinfo, courses=courses, news=news, industrys=industrys, 
        videos=videos, charges=charges, coaches=coaches, 
        elegants=elegants, branches=branches)

@app.route('/about/')
def about():
    abouts = MetaInfo.getAbout()
    return render_template('about.html', abouts=abouts)

@app.route('/news/')
def news():
    news = MetaInfo.getNews()
    return render_template('news.html', news=news)

@app.route('/news_content/<news_id>')
def news_content(news_id):
    news = MetaInfo.query.filter_by(id=news_id).first()
    return render_template('news_content.html', news=news)

@app.route('/industry/')
def industry():
    industrys = MetaInfo.getIndustry()
    return render_template('industry.html', industrys=industrys)

@app.route('/industry_content/<industry_id>')
def industry_content(industry_id):
    industry = MetaInfo.query.filter_by(id=industry_id).first()
    return render_template('industry_content.html', industry=industry)

@app.route('/courses/<course_id>')
def courses(course_id):
    courses = MetaInfo.getCourse()
    c = MetaInfo.query.filter_by(id=course_id).first()

    return render_template('course.html', courses=courses, c=c)

@app.route('/course/')
def course():
    courses = MetaInfo.getCourse()
    c = None
    return render_template('course.html', courses=courses, c=c)

@app.route('/branch/')
def branch():
    branches = Branch.query.all()
    return render_template('branch.html', branches=branches) 

@app.route('/charge/')   
def charge():
    charges = MetaInfo.getCharge()
    return render_template('charge.html', charges=charges)

@app.route('/charge_table/')
def charge_table():
    return render_template('charge_table.html')

@app.route('/video')
def video():
    videos = MetaInfo.getVideo()
    return render_template('video.html', videos=videos)

@app.route('/team/')
def team():
    coaches = MetaInfo.getCoach()
    return render_template('team.html', coaches=coaches)

@app.route('/coach/<coach_id>')
def coach(coach_id):
    coach = MetaInfo.query.filter_by(id=coach_id).first()
    return render_template('coach.html', coach=coach)

@app.route('/elegant/')
def elegant():
    elegants = MetaInfo.getElegant()
    return render_template('elegant.html', elegants=elegants)

@app.route('/elegant_student/<elegant_id>')
def elegant_student(elegant_id):
    elegant = MetaInfo.query.filter_by(id=elegant_id).first()
    return render_template('elegant_student.html', elegant=elegant)

@app.route('/signup/')
def signup():
    courses = MetaInfo.getCourse()
    return render_template( 'signup.html', courses=courses)

@app.route('/comunication/')
def comunication():
    return render_template('comunication.html')
