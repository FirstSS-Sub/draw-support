# coding: UTF-8
from flask import (
    Flask, render_template,
    redirect, url_for, request,
    session, flash, make_response
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager, logout_user
from werkzeug.security import *
import numpy as np
import cv2
from datetime import *

# ファイル名をチェックする関数
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = "draw2019"

# 画像のアップロード先のディレクトリ
UPLOAD_FOLDER = './static/images/'

# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL') or 'sqlite:///draw.db'  # or "postgresql://localhost/k-on"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

"""
CRUD操作

----create----
    user = User('shinzo', 'shinzo.abe@example.com')
    db.session.add(user)
    db.session.commit()

----read all----
    users = User.query.all()

----read, delete----
    user = db.session.query(User).filter_by(name='shinzo').first()
    db.session.delete(user)
    db.session.commit()

----read, update----
    user = db.session.query(User).filter_by(name='shinzo').first()
    user.email = 'shinzo.abe@google.com'
    db.session.add(user)
    db.session.commit()
"""

"""
class UserList(db.Model):
    __tablename__ = "UserList"
    id = db.Column(db.Integer(), primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    thu = db.Column(db.String(8), nullable=False, default="00000000")
    fri = db.Column(db.String(8), nullable=False, default="00000000")
    sat = db.Column(db.String(5), nullable=False, default="00000")
    sun = db.Column(db.String(5), nullable=False, default="00000")
    mon = db.Column(db.String(8), nullable=False, default="00000000")
    tue = db.Column(db.String(8), nullable=False, default="00000000")
    wed = db.Column(db.String(8), nullable=False, default="00000000")
    update = db.Column(db.Integer(), nullable=False, default=0)
    comment = db.Column(db.String(255), nullable=False, default="")

    def __repr__(self):
        return "UserList<{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}>".format(
            self.id, self.user_name, self.password, self.thu, self.fri, self.sat, self.sun, self.mon, self.tue, self.wed, self.update, self.comment)
"""


class Article(db.Model):
    #__tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pub_date = db.Column(db.DateTime, nullable=False,
                         default=datetime.utcnow)
    name = db.Column(db.String(80))
    #name = db.Column(db.Text(80))
    article = db.Column(db.Text())
    img_name = db.Column(db.String(100))
    img_path = db.Column(db.String(200))
    thread_id = db.Column(db.Integer, db.ForeignKey(
        'thread.id'), nullable=False)

    def __init__(self, pub_date, name, article, img_name, img_path, thread_id):
        self.pub_date = pub_date
        self.name = name
        self.article = article
        self.img_name = img_name
        self.img_path = img_path
        self.thread_id = thread_id


class Thread(db.Model):
    #__tablename__ = "threads"
    id = db.Column(db.Integer, primary_key=True)
    threadname = db.Column(db.String(80), unique=True)
    #threadname = db.Column(db.Text(80), unique=True)
    articles = db.relationship('Article', backref='thread', lazy=True)

    def __init__(self, threadname, articles=[]):
        self.threadname = threadname
        self.articles = articles


db.create_all()


@app.route("/")
def index():
    threads = Thread.query.all()
    # print("\n---------------------------------------------")
    # print(text)
    # print(type(text))
    # print("---------------------------------------------\n")
    return render_template("index.html", threads=threads)


@app.route("/thread", methods=["POST"])
def thread():
    thread_get = request.form["thread"]
    threads = Thread.query.all()
    #articles = Article.query.all()
    thread_list = []
    threads = Thread.query.all()
    for th in threads:
        thread_list.append(th.threadname)
        #print("----" + th.threadname + "----")
    if thread_get in thread_list:
        thread = Thread.query.filter_by(threadname=thread_get).first()
        articles = Article.query.filter_by(thread_id=thread.id).all()
        return render_template("thread.html",
                               articles=articles,
                               thread=thread_get)
    else:
        thread_new = Thread(thread_get)
        db.session.add(thread_new)
        db.session.commit()
        articles = Article.query.filter_by(thread_id=thread_new.id).all()
        return render_template("thread.html",
                               articles=articles,
                               thread=thread_get)


@app.route("/result", methods=["POST"])
def result():
    date = datetime.now()
    article = request.form["article"]
    name = request.form["name"]
    thread = request.form["thread"]
    app.logger.info(request.files)
    if request.files["pic"].filename is not "":
        # データの取り出し
        file = request.files["pic"]

        # 危険な文字を削除（サニタイズ処理）
        temp_name = secure_filename(file.filename)

        # 日時.拡張子 例:2019-12-13_14:13:41.jpg
        img_name = date.strftime("%Y-%m-%d_%H:%M") + \
            '.' + temp_name.rsplit('.', 1)[1].lower()

        # .があるかどうかのチェックと、拡張子の確認
        # OKなら１、だめなら0
        if '.' in img_name and img_name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            # if False:
            app.logger.info(type(file))
            # img_name = "{}.jpg".format(date)
            # img_path = "./static/images/{}".format(img_name)

            # ファイルの保存
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
        else:
            app.logger.info("AAAAAAAAAAAAAAAAAAA")
            app.logger.info(img_name)
            flash('拡張子は png, jpg, gif のみ対応しています',
                  category='alert alert-danger')
            return redirect(url_for('index'))
    else:
        app.logger.info("BBBBBBBBBBBBBBBB")
        img_name = ""
    # print(article)
    # print(name)
    # print("------------------------------------------------------------")
    # print(thread)
    # print("------------------------------------------------------------")
    thread = Thread.query.filter_by(threadname=thread).first()
    # print(thread)
    # print("------------------------------------------------------------")

    # 1つ上の階層を参照するために最初にドット
    img_path = '.' + UPLOAD_FOLDER + img_name

    admin = Article(pub_date=date, name=name,
                    article=article, thread_id=thread.id, img_name=img_name, img_path=img_path)
    db.session.add(admin)
    db.session.commit()

    app.logger.info(img_path)
    app.logger.info(img_name)

    return render_template("bbs_result.html", article=article, name=name, now=date, img_name=img_name)


if __name__ == "__main__":
    app.run(debug=True)
