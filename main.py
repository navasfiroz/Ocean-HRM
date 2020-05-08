from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


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
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String,nullable=False)
    phone = db.Column(db.String)
    whatsapp = db.Column(db.Boolean)
    title = db.Column(db.String)
    role = db.Column(db.String)
    annual_leaves = db.Column(db.String)
    team = db.Column(db.Integer)
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


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

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
# new_org = User(name="Azeez",email="navasfiroz@gmail.com")
# db.session.add(new_org)
# db.session.commit()
# for name in User.query.all():
#     print(name.name)


@app.route('/')
def index_page():
    return render_template("template.html")

app.run(debug=True)

