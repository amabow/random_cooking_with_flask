from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import random

app = Flask(__name__)
print("input psql user name")
user = input()
print("input psql password")
passwd = input()
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://{0}:{1}@localhost/meal".format(user, passwd)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Meal(db.Model):
    __tablename__ = 'meal'
    id = db.Column(db.Integer, primary_key = True, unique = True)
    name = db.Column(db.String(20), index = True, unique = True)
    def __repr__(self):
        return '<name %r >' % self.name

@app.route("/")
def index():
    meal = Meal.query.all()
    ids = []
    for m in meal:
        ids.append(m.id)
    i = random.randint(0, len(ids)-1)
    return render_template("index.html", meal = meal[ids[i]-1].name)

@app.route('/register', methods=["GET"])
def login():
   return render_template("register.html")

@app.route('/register', methods=["POST"])
def check():
    if request.form["meal"]:
        all_menu = Meal.query.all()
        i = 0
        while True:
            used = 0
            for m in all_menu:
                if(m.id == i):
                    used = 1
            if not used:
                break    
            i += 1
        id = i
        newMeal = Meal(id = id, name = request.form['meal'])
        for m in all_menu:
            if(m.name == request.form['meal']):
                return render_template("duplication.html", meal=newMeal.name)
        db.session.add(newMeal)
        db.session.commit()
        return render_template("check.html", meal=newMeal.name)
    else:
        return render_template("error.html")

@app.route('/list', methods=["GET"])
def show_list():
    all_meal = Meal.query.all()
    return render_template("list.html", all_meal=all_meal)

@app.route('/list', methods=["POST"])
def deleted():
    meal_li = request.form.getlist("meal")
    all_meal = Meal.query.all()
    for m in meal_li:
        target = db.session.query(Meal).filter_by(name=m).first()
        print("target.id, target.name: " + str(target.id) + " "  + str(target.name))
        db.session.delete(target)
    db.session.commit()
    return render_template("deleted.html", all_meal=meal_li)

@app.route('/about')
def about():
   return render_template("about.html")
