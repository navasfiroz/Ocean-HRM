from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    personal_info = db.Column(db.Boolean)
    jan_to_dec_leave_cycle = db.Column(db.Boolean)

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

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_by = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String, nullable=False)
    status = db.Column(db.String)
    action_by = db.Column(db.String)

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


# db.create_all()
# finance = Team(name="Finance")
# db.session.add(finance)
# db.session.commit()
# navas = User(name="Navas",email="navasfiroz@gmail.com",team_id=1)
# db.session.add(navas)
# db.session.commit()

# for user in User.query.all():
#     print(user.team.name)

@app.route('/employees/', methods=["GET","POST"])
def employees():
    all_team= Team.query.all()
    all_users = User.query.all()
    if request.method == "GET":
        return render_template("profile.html", teams=all_team, users=all_users)
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

app.run(debug=True)

