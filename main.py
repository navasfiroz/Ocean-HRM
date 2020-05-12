from flask import Flask, render_template,request,redirect,session,url_for,g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config["SECRET_KEY"] = "dQOBHR4Gi5UVg8BB-EITNA"

@app.before_request
def before_request():
    g.user = None
    if "uid" in session:
        login_user = User.query.get(session["uid"])
        if login_user and login_user.team_id == session["td"] and bcrypt.check_password_hash(session["sk"], login_user.name):
            g.user = login_user

# Bcrypt syntax for generating and checking hash
# passw = bcrypt.generate_password_hash("kl2h4448").decode("utf-8")
# print(bcrypt.check_password_hash(passw,"kl2h4448"))

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    personal_info = db.Column(db.Boolean)
    leave_calender = db.Column(db.Integer)
    currency = db.Column(db.String)

#Need to check the email ID uniqueness, now skipping that part
#Password treating as string, need to slat it later
#User role need backend validation as well
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    users = db.relationship("User",backref="team")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String,nullable=False)
    phone = db.Column(db.String)
    whatsapp = db.Column(db.Boolean)
    title = db.Column(db.String)
    role = db.Column(db.String)
    annual_leaves = db.Column(db.String)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    admin_to_team = db.Column(db.Integer)
    line_manager = db.Column(db.Integer)
    password = db.Column(db.String)
    dob = db.Column(db.DateTime)
    blood_group = db.Column(db.String)
    doj = db.Column(db.DateTime)
    pay = db.Column(db.Integer)
    address = db.Column(db.String)
    secondary_contact_name = db.Column(db.String)
    secondary_contact_relation = db.Column(db.String)
    secondary_contact_phone = db.Column(db.String)
    origin_country = db.Column(db.String)
    diet_type = db.Column(db.String)
    drinking = db.Column(db.Boolean)
    marital_status = db.Column(db.String)
    dp = db.Column(db.String)

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_by = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String, nullable=False)
    status = db.Column(db.String)
    action_by = db.Column(db.String, default="default.png")

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer, nullable=False)
    receiver = db.Column(db.Integer, nullable=False)
    is_group = db.Column(db.Boolean, nullable=False)
    content = db.Column(db.String, nullable=False)

class Activity_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    action_by = db.Column(db.Integer, nullable=False)
    action_type = db.Column(db.String, nullable=False)

#Set session browser cookie with 3 layer security
def set_session_cookie(user):
    session["uid"] = user.id
    session["sk"] = bcrypt.generate_password_hash(user.name).decode("utf-8")
    session["td"] = user.team_id

def clear_session_cookie():
    session.pop("uid", None)
    session.pop("sk", None)
    session.pop("td", None)


db.create_all()
# finance = Team(name="Finance")
# db.session.add(finance)
# db.session.commit()
# navas = User(name="Navas",email="navasfiroz@gmail.com",team_id=1)
# db.session.add(navas)
# db.session.commit()

# for user in User.query.all():
#     print(user.team.name)


@app.route('/sign-in/', methods=["GET","POST"])
def sign_in():
    if request.method == "POST":
        req = request.form
        email = request.form['email']
        password = req['password']

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            set_session_cookie(user)
            return redirect(url_for("teams"))
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/sign-out/')
def sign_out():
    clear_session_cookie()
    return redirect(url_for("sign_in"))

@app.route('/start/',methods=["GET","POST"])
def start():
    if request.method == "POST":
        user_name = request.form['user_name']
        user_email = request.form['email']
        user_password = bcrypt.generate_password_hash(request.form['password']).decode("utf-8")
        org_name = request.form['name']
        org_currency = request.form['currency']
        org_leave_policy = request.form['leave_calender']

        db.session.add(Team(name="Administration"))
        db.session.commit()
        admin = User(name=user_name,email=user_email,password=user_password,role=4,team_id=1)
        db.session.add(admin)
        db.session.commit()

        user = User.query.filter_by(email=user_email).first()
        set_session_cookie(user)

        org = Organization(name=org_name,currency=org_currency,leave_calender=org_leave_policy)
        db.session.add(org)
        db.session.commit()

        return redirect("/teams/")

    else:
        return render_template("org_register.html")

@app.route('/employees/', methods=["GET","POST"])
def employees():
    all_team= Team.query.all()
    all_users = User.query.all()
    if request.method == "GET":
        return render_template("employees.html", teams=all_team, users=all_users)
    else:
        name = request.form['name']
        email = request.form['email']
        team = request.form['team']
        title = request.form['title']
        role = request.form['role']
        leaves = request.form['leaves']
        doj = datetime.strptime(request.form['doj'],'%Y-%m-%d')
        pay = request.form['pay']
        new_user = User(name=name,email=email,team_id=team,role=role,annual_leaves=leaves,doj=doj,pay=pay)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/employees/")


@app.route('/teams/', methods=["GET","POST"])
def teams():
    all_team= Team.query.all()
    if request.method == "GET":
        return render_template("teams.html", teams=all_team)
    else:
        name = request.form['team-name']
        db.session.add(Team(name=name))
        db.session.commit()
        return redirect("/teams/")


@app.route('/profile/<user_id>')
def profile(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template("user_profile.html", user=user)
    else:
        return redirect(url_for("employees"))

@app.route('/edit-profile/')
def edit_profile():
    return render_template("edit_profile.html")

app.run(debug=True)


