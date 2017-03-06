#!venv/bin/python
#coding:utf-8
import os
import sys
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template, session, flash
from flask_script import Manager
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
from wtforms import StringField, SubmitField
from wtforms.validators import Required
# from database import init_db, db_session
# from models import User


UPLOAD_FOLDER = sys.path[0] + '/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'c', 'cpp'])
basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['SECRET_KEY'] = 'This is a hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
manager = Manager(app)
moment = Moment(app)
bootstrap = Bootstrap(app)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role % r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User % r>' % self.username




class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')



@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Look like you have changed your name')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['submit'] == 'Sign in':
            # 用户登录验证
            return redirect(url_for('index'))
        elif request.form['submit'] == 'Sign up':
            # 用户注册
            print('用户注册')
            pass
            return redirect(url_for('join'))
        else:
            pass
    return render_template('login.html')


@app.route('/join', methods=['GET', 'POST'])
def join():
    return render_template('join.html')


# @app.route('/add/<name>/<email>')
# def add(name, email):
#     u = User(name=name, email=email)
#     try:
#         db_session.add(u)
#         db_session.commit()
#     except Exception:
#         return 'wrong'
#     return 'Add %s user successfully' % name


# @app.route('/get/<name>')
# def get(name):
#     try:
#         u = User.query.filter(User.name==name).first()
#         return 'hello %s' % u.name
#     except Exception:
#         return 'there isnot %s' % name


@app.route('/user')
def user():
    return render_template('user.html', name='wangxingyao', current_time=datetime.utcnow())



def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return '''
                上传成功
            '''
            return redirect(url_for('uploaded_file',filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
    <p><input type=file name=file>
    <input type=submit value=Upload>
    </form>
    '''

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    # init_db()
    manager.run()
    # app.run(debug=True, host='0.0.0.0')
