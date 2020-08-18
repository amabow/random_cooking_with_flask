from flask import Flask, render_template, request, session, redirect, abort, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user

import os
import random

app = Flask(__name__)
print("input psql user name")
user = input()
print("input psql password")
passwd = input()
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{0}:{1}@localhost/meal".format(user, passwd)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Meal(db.Model):
    __tablename__ = 'meal'
    id = db.Column(db.Integer, primary_key = True, unique = True)
    name = db.Column(db.String(20), index = True, unique = True)
    uid = db.Column(db.Integer, index = True)
    def __repr__(self):
        return '<name %r >' % self.name

class User(UserMixin, db.Model):
    __tablename__ = 'member'
    id = db.Column(db.Integer, primary_key = True, unique = True)
    name = db.Column(db.String(32), index = True, unique = True)
    email = db.Column(db.String(64), index = True, unique = True)
    def __repr__(self):
        return '<name %r >' % self.name

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

############################################################################################
@app.route("/")
def index():
    meal = Meal.query.all()
    ids = []
    for m in meal:
        ids.append(m.id)
    i = random.randint(0, len(ids)-1)
    return render_template("index.html", meal = meal[ids[i]-1].name)
############################################################################################
@app.route('/login', methods=["GET"])
def form():
    return render_template("login.html")

@app.route('/login', methods=["POST"])
def login():
    all_user = User.query.all()
    name = request.form['name']
    email = request.form['email']
    for u in all_user:
        print("u.name, u.email: ", u.name, u.email)
        if u.name==name and u.email==email:
            user = u
            session["logged_in"] = True
            login_user(user, True)
            return redirect(url_for('index'))
    return render_template("login_error.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("login.html")
############################################################################################
@app.route('/register', methods=["GET"])
def register():
   return render_template("register.html")

@app.route('/register', methods=["POST"])
def method_name():
    name = request.form["name"]
    email = request.form["email"]
    if name and email:
        all_user = User.query.all()
        id = 0
        for u in all_user:
            if u.name==name and u.email==email:
                return render_template("duplication_user.html")
            if id != u.id:
                break
            id += 1
        new_user = User(id=id, name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return render_template("registration_check.html", user=new_user)
    else:
        return render_template("registration_error.html")
############################################################################################
@app.route('/add_meal', methods=["GET"])
@login_required
def add_meal():
   return render_template("add_meal.html")

@app.route('/add_meal', methods=["POST"])
@login_required
def check():
    if request.form["meal"]:
        all_menu = Meal.query.filter_by(uid=current_user.id).all()
        i = 0
        while True:
            used = 0
            for m in all_menu:
                if(m.id == i):
                    used = 1
            if not used:
                break    
            i += 1
        new_meal = Meal(id = i, name = request.form['meal'], uid=current_user.id)
        for m in all_menu:
            if(m.name == request.form['meal']):
                return render_template("duplication.html", meal=new_meal.name)
        db.session.add(new_meal)
        db.session.commit()
        return render_template("check.html", meal=new_meal.name)
    else:
        return render_template("error.html")
############################################################################################
@app.route('/meal')
@login_required
def meal():
   return render_template("meal.html")
############################################################################################
@app.route('/list', methods=["GET"])
@login_required
def show_list():
    all_meal = Meal.query.filter_by(uid=current_user.id).all()
    return render_template("list.html", all_meal=all_meal)

@app.route('/list', methods=["POST"])
@login_required
def deleted():
    meal_li = request.form.getlist("meal")
    all_meal = Meal.query.filter_by(uid=current_user.id).all()
    for m in meal_li:
        target = db.session.query(Meal).filter_by(name=m).first()
        print("target.id, target.name: " + str(target.id) + " "  + str(target.name))
        db.session.delete(target)
    db.session.commit()
    return render_template("deleted.html", all_meal=meal_li)
############################################################################################
@app.route('/about')
def about():
   return render_template("about.html")
############################################################################################
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
