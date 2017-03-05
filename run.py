#!venv/bin/python
#coding:utf-8
import os
import sys
from flask import Flask, request, redirect, url_for, render_template
from werkzeug import secure_filename
from flask_bootstrap import Bootstrap
from database import init_db, db_session
from models import User


UPLOAD_FOLDER = sys.path[0] + '/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'c', 'cpp'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

bootstrap = Bootstrap(app)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form['username'])
        print(request.form['password'])
        return render_template('index.html')
    return render_template('login.html')


@app.route('/add/<name>/<email>')
def add(name, email):
    u = User(name=name, email=email)
    try:
        db_session.add(u)
        db_session.commit()
    except Exception:
        return 'wrong'
    return 'Add %s user successfully' % name


@app.route('/get/<name>')
def get(name):
    try:
        u = User.query.filter(User.name==name).first()
        return 'hello %s' % u.name
    except Exception:
        return 'there isnot %s' % name


@app.route('/user')
def user():
    return render_template('user.html', name='wangxingyao')



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



if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
