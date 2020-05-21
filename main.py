from flask import Flask, render_template,request,redirect,session,url_for,g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, date, timedelta
import os
from werkzeug.utils import secure_filename
import secrets
from flask_mail import Mail, Message
from responses import *


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

app.config["SECRET_KEY"] = "dQOBHR4Gi5UVg8BB-EITNA"
app.config['UPLOAD_FOLDER'] = "static/img/users/"
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

app.config['MAIL_SERVER'] = 'in-v3.mailjet.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'c897cb0eac91180c139a6700b4baabb0'
app.config['MAIL_PASSWORD'] = '3a189e06a85e1c87e4e6800a66bb3995'
app.config['MAIL_MAX_EMAILS'] = 5
app.config['MAIL_DEFAULT_SENDER'] = "tripeagle2019@gmail.com"
mail = Mail(app)


@app.before_request
def before_request():
    g.user = None
    if "uid" in session:
        login_user = User.query.get(session["uid"])
        if login_user and bcrypt.check_password_hash(session["sk"], login_user.name):
            g.user = login_user

"""
Starting of user models
"""
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    personal_info = db.Column(db.Boolean)
    leave_calender = db.Column(db.Integer)
    currency = db.Column(db.String)
    week_start = db.Column(db.Integer)
    week_off = db.Column(db.String)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    members = db.relationship("Team_members", cascade="all,delete", backref="team")
    leads = db.relationship("Team_leads", cascade="all,delete", backref="team")

class Team_leads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))

class Team_members(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    
class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    #Category -> 1=Holiday, 2=Sick
    category = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.Date)
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)
    message = db.Column(db.String)
    
class Leave_action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    leave_id = db.Column(db.Integer, db.ForeignKey("leave.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    #Status 1=Approve, 2=Decline, 3=Cancelled 
    status = db.Column(db.Integer)
    leaves = db.relationship("Leave", cascade="all,delete", backref="action")

class Activity_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    description = db.Column(db.String, nullable=False)

class Access_token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.Date)
    key = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Holiday(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    name = db.Column(db.String)
    description = db.Column(db.String)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String,nullable=False)
    phone = db.Column(db.String)
    whatsapp = db.Column(db.Boolean)
    title = db.Column(db.String)
    #User roles -> 1=Employee, 2=Manager, 3=Admin
    role = db.Column(db.Integer)
    annual_leaves = db.Column(db.Integer)
    password = db.Column(db.String)
    dob = db.Column(db.Date)
    blood_group = db.Column(db.String)
    doj = db.Column(db.Date)
    pay = db.Column(db.Integer)
    address = db.Column(db.String)
    secondary_contact_name = db.Column(db.String)
    secondary_contact_relation = db.Column(db.String)
    secondary_contact_phone = db.Column(db.String)
    origin_country = db.Column(db.String)
    #Diet type -> 1=Non-vegan, 2=Eggetarian, 3=Vegan
    diet_type = db.Column(db.Integer)
    drinking = db.Column(db.Boolean)
    #Marital status -> 1=Single, 2=Married
    marital_status = db.Column(db.Integer)
    dp = db.Column(db.String)
    leaves = db.relationship("Leave", cascade="all,delete", backref="requested_by")
    leading = db.relationship("Team_leads", cascade="all,delete", backref="manager")
    member_of = db.relationship("Team_members", cascade="all,delete", backref="members")
    actioned_leaves = db.relationship("Leave_action", cascade="all,delete", backref="actioned_by")
    logs = db.relationship("Activity_log",backref="activity_by")
    token = db.relationship("Access_token", cascade="all,delete", backref="user")

db.create_all()


"""
Starting Routes here
"""
@app.route('/')
def overview():
    if g.user:
        summary = this_week_summary()
        dicto = get_approved_leaves(date.today(), 10)
        high = max(dicto.values())+3
        if g.user:
            days = (date.today() - g.user.doj)
            days = days.days+1
        else:
            days = 0
        return render_template("overview.html", days=days, summary=summary, key=json.dumps(list(dicto.keys())), val=json.dumps(list(dicto.values())),high=json.dumps(high))
    else:
        return render_template("login.html")

@app.route('/calendar/', methods=["GET","POST"])
def calendar():
    if g.user:
        events = calender_events()
        if request.method == "GET":
            return render_template("calendar.html", events=json.dumps(events))
        else:
            name = request.form['name']
            start = datetime.strptime(request.form['from'],'%Y-%m-%d').date()
            end = datetime.strptime(request.form['end'],'%Y-%m-%d').date()
            message =request.form['message']
            announce =request.form.get('announce')
            holiday = Holiday(name=name,start_date=start,end_date=end,description=message)
            db.session.add(holiday)
            db.session.commit()
            if announce:
                users = User.query.filter(User.password.isnot(None)).all()
                for user in users:
                    send_holiday_announcement(name, start, end, user)
            update_log(g.user.id,name+" holiday created")
            return render_template("calendar.html", events=json.dumps(events),response=response("s2"))
    else:
        return render_template("login.html")


@app.route('/sign-in/', methods=["GET","POST"])
def sign_in(**kwargs):
    if request.method == "POST":
        req = request.form
        email = request.form['email']
        password = req['password']
        next_url = req['next-url']

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            set_session_cookie(user)
            if next_url:
                return redirect(next_url)
            return redirect(url_for("overview"))
        else:
            return render_template("login.html",response=response("e1"))
    else:
        url_req = kwargs.get('nextURL',None)
        if url_req:
            return render_template("login.html", nextURL=url_req)
        return render_template("login.html")

@app.route('/sign-out/')
def sign_out():
    clear_session_cookie()
    return redirect(url_for("sign_in"))

@app.route('/update-password/', methods=["GET","POST"])
def update_password():
    if g.user:
        if request.method == "GET":
            return render_template("password-update.html")
        else:
            password = request.form['c-password']
            new_password = request.form['password']
            if new_password != "" and bcrypt.check_password_hash(g.user.password, password):
                user = User.query.get(g.user.id)
                user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
                db.session.commit()
                update_log(g.user.id,"Password changed")
                clear_session_cookie()
                return render_template("login.html",response=response("s3"))
            else:
                return render_template("password-update.html",response=response("e2"))
    else:
        return render_template("login.html")

@app.route('/forgot-password/', methods=["GET","POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")
    else:
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = create_token(email)
            link = "http://127.0.0.1:5000/reset/"+str(user.id)+"/"+token+"/"
            subject = user.name+", reset your password"
            send_reset_mail(subject,user,link)
            update_log(user.id,"Requested for password reset")
            return render_template("forgot_password.html", response=response("s7"))
        else:
            return render_template("forgot_password.html", response=response("e4"))

@app.route('/start/',methods=["GET","POST"])
def start():
    if request.method == "POST":
        user_name = request.form['user_name']
        user_email = request.form['email']
        user_password = bcrypt.generate_password_hash(request.form['password']).decode("utf-8")
        org_name = request.form['name']
        org_currency = request.form['currency']
        org_leave_policy = request.form['leave_calender']

        db.session.add(Team(name="Administration", description="Group of all admins"))
        db.session.commit()
        admin = User(name=user_name,email=user_email,password=user_password,role=3)
        db.session.add(admin)
        db.session.commit()

        user = User.query.filter_by(email=user_email).first()

        team = Team_members(user_id=user.id, team_id=1)
        leads = Team_leads(user_id=user.id, team_id=1)
        db.session.add(team)
        db.session.add(leads)
        db.session.commit()


        org = Organization(name=org_name,currency=org_currency,leave_calender=org_leave_policy)
        db.session.add(org)
        db.session.commit()
        update_log(user.id,org_name+" created")
        return redirect(url_for("sign_in",nextURL="/company/settings/"))

    else:
        return render_template("org_register.html")

@app.route('/employees/', methods=["GET","POST"])
def employees():
    if g.user:
        all_team= Team.query.all()
        all_users = User.query.all()
        if request.method == "GET":
            return render_template("employees.html", teams=all_team, users=all_users)
        else:
            email = request.form['email']
            if is_email_unique(email):
                name = request.form['name']
                team = request.form['team']
                title = request.form['title']
                role = request.form['role']
                leaves = request.form['leaves']
                doj = datetime.strptime(request.form['doj'],'%Y-%m-%d').date()
                pay = request.form['pay']
                new_user = User(name=name,email=email,role=role,annual_leaves=leaves,doj=doj,pay=pay,title=title)
                db.session.add(new_user)
                db.session.commit()

                user = User.query.filter_by(email=email).first()
                member = Team_members(user_id=user.id,team_id=team)
                db.session.add(member)
                db.session.commit()

                token = create_token(email)
                link = "http://127.0.0.1:5000/reset/"+str(user.id)+"/"+token+"/"
                subject = user.name+", your invitation to Hexa HRM"
                send_activation_mail(subject,g.user,user,link)
                update_log(g.user.id,email+" profile created")
                return render_template("employees.html", teams=all_team, users=all_users, response=response("s2"))
            else:
                return render_template("employees.html", teams=all_team, users=all_users, response=response("e3"))
    else:
        return render_template("login.html")

@app.route('/reset/<user_id>/<token>/', methods=["GET","POST"])
def check_token(user_id,token):
    user = User.query.get(user_id)
    if user and user.token:
        key = user.token[0].key
        if key == token:
            clear_session_cookie()
            if request.method == "GET":
                return render_template("password-reset.html", id=user_id, token=token, user=user)
            else:
                password = request.form['password']
                if password != "":
                    user.password = bcrypt.generate_password_hash(password).decode("utf-8")
                    db.session.delete(user.token[0])
                    db.session.commit()
                else:
                    return redirect(url_for("check_token",user_id=user_id,token=token))
                update_log(user.id,user.email+" profile activated")
                return redirect(url_for("sign_in",nextURL="/edit-profile/"+str(user.id)+"/"))
        else:
            return render_template("lost.html")
    else:
        return render_template("lost.html")

@app.route('/teams/', methods=["GET","POST"])
def teams():
    if g.user:
        all_team= Team.query.all()
        users = User.query.all()
        if request.method == "GET":
            return render_template("teams.html", teams=all_team, users=users)
        else:
            name = request.form['name']
            description = request.form['description']
            lead = request.form['lead']
            db.session.add(Team(name=name, description=description))
            db.session.commit()
            team_id = Team.query.filter_by(name=name).first().id
            team_lead = Team_leads(user_id=lead,team_id=team_id)
            team_member = Team_members(user_id=lead,team_id=team_id)
            db.session.add(team_lead)
            db.session.add(team_member)
            db.session.commit()
            update_log(g.user.id,name+" team created")
            return render_template("teams.html", teams=all_team, response=response("s2"))
    else:
        return render_template("login.html")

@app.route('/teams/<team_id>/', methods=["GET","POST"])
def team_profile(team_id):
    if g.user:
        if request.method == "GET":
            team = Team.query.get(team_id)
            users = User.query.all()
            if team:
                return render_template("team_profile.html", team=team, users=users)
            else:
                return redirect(url_for("teams"))
        else:
            user_id = request.form["user"]
            if user_id:
                team_lead = Team_leads(user_id=user_id,team_id=team_id)
                db.session.add(team_lead)
                db.session.commit()
                update_log(g.user.id,user_id+" assigned as lead to group id "+team_id)
            return redirect(url_for("team_profile",team_id=team_id))
    else:
        return render_template("login.html")


@app.route('/delete-team/', methods=["POST"])
def delete_team():
    if g.user.role == 3:
        password = request.form["password"]
        team_id = request.form["team-id"]
        if bcrypt.check_password_hash(g.user.password, password):
            team = Team.query.get(team_id)
            db.session.delete(team)
            db.session.commit()
            update_log(g.user.id,"Deleted team id "+team_id)
            all_team= Team.query.all()
            all_users = User.query.all()
            return render_template("teams.html", teams=all_team, users=all_users, response=response("s4"))
    all_team= Team.query.all()
    all_users = User.query.all()
    return render_template("teams.html", teams=all_team, users=all_users, response=response("e2"))


@app.route('/profile/<user_id>/')
def profile(user_id):
    if g.user:
        user = User.query.get(user_id)
        if user:
            return render_template("user_profile.html", user=user)
        else:
            return redirect(url_for("employees"))
    else:
        return render_template("login.html")

@app.route('/edit-profile/<user_id>/', methods=["GET","POST"])
def edit_profile(user_id):
    user = User.query.get(user_id)
    if g.user.role == 3 or g.user.id == user.id: 
        if request.method == "POST":

            #Check for DP update and upload to FTP
            image = request.files['image']
            if image.filename != "" and image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                hash_token = secrets.token_urlsafe(16)
                extn = filename.rsplit('.', 1)[1].lower()
                current_dp = hash_token+"."+extn
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], current_dp))
                if user.dp:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.dp))
                user.dp = current_dp
                db.session.commit()

            user = User.query.get(user_id)
            user.name = request.form["name"]
            user.email = request.form["email"]
            user.phone = request.form["phone"]
            user.whatsapp = bool(request.form.get("whatsapp"))
            user.dob = datetime.strptime(request.form['dob'],'%Y-%m-%d').date()
            user.blood_group = request.form["blood_group"]
            user.address = request.form["address"]
            user.origin_country = request.form["country"]
            user.secondary_contact_name = request.form["s_name"]
            user.secondary_contact_relation = request.form["s_relate"]
            user.secondary_contact_phone = request.form["s_phone"]
            user.diet_type = request.form["diet"]
            user.drinking = bool(request.form.get("drink"))
            user.marital_status = request.form["marital"]
            if g.user.role ==3:
                user.title = request.form["title"]
                user.role = request.form["role"]
                user.doj = datetime.strptime(request.form["doj"],'%Y-%m-%d').date()
                user.pay = request.form["pay"]
                user.annual_leaves = request.form["leave"]
            db.session.commit()
            update_log(g.user.id,"Updated user pfrofile "+str(user.id))
            return render_template("edit_profile.html", user=user, response=response("s3"))
        else:
            return render_template("edit_profile.html", user=user)
    else:
        return redirect(url_for("employees"))

@app.route('/delete-profile/', methods=["POST"])
def delete_user():
    if g.user.role == 3:
        password = request.form["password"]
        user_id = request.form["user-id"]
        if bcrypt.check_password_hash(g.user.password, password):
            user = User.query.get(user_id)
            db.session.delete(user)
            db.session.commit()
            update_log(g.user.id,"Deleted user pfrofile "+str(user.id))
            all_team= Team.query.all()
            all_users = User.query.all()
            return render_template("employees.html", teams=all_team, users=all_users, response=response("s4"))
    all_team= Team.query.all()
    all_users = User.query.all()
    return render_template("employees.html", teams=all_team, users=all_users, response=response("e2"))

@app.route('/leaves/', methods=["GET","POST"])
def leaves():
    if g.user:
        if request.method == "POST":
            from_date = datetime.strptime(request.form['from'],'%Y-%m-%d').date()
            to_date = datetime.strptime(request.form['to'],'%Y-%m-%d').date()
            category = request.form['category']
            message = request.form['message']
            created_date = date.today()

            leave_req = Leave(user_id=g.user.id,category=category,created_date=created_date,from_date=from_date,to_date=to_date,message=message)
            db.session.add(leave_req)
            db.session.commit()

            length = count_leaves(from_date,to_date)
            user = User.query.get(g.user.id)
            user.annual_leaves = user.annual_leaves - length
            db.session.commit()

            #Get all team leads that session user member of
            team_leads = get_team_leads(user.id)

            #Send email notification all admins and team leads
            admins = User.query.filter_by(role=3).all()
            for user in admins:
                send_request_mail(from_date,to_date,category,user)
            for lead in team_leads:
                if not lead in admins:
                    send_request_mail(from_date,to_date,category,lead)
            update_log(g.user.id,"Requested new leave")
            return render_template("leaves.html", response=response("s1"))

        else:
            return render_template("leaves.html")
    else:
        return render_template("login.html")

@app.route('/leaves/action/<action>/<id>')
def leave_action(action,id):
    leave = Leave.query.get(id)
    team_leads = get_team_leads(leave.requested_by.id)
    if g.user.role == 3 or g.user in team_leads:
        if action == "d" and not leave.action:
            action = Leave_action(leave_id=leave.id,user_id=g.user.id,status=2)
            length = count_leaves(leave.from_date,leave.to_date)
            user = leave.requested_by
            user.annual_leaves = user.annual_leaves + length
            db.session.add(action)
            db.session.commit()
            send_action_mail(leave)
            update_log(g.user.id,"Declined leave request id "+str(leave.id))
            return redirect(url_for("requests"))
        elif action == "a" and not leave.action:
            action = Leave_action(leave_id=leave.id,user_id=g.user.id,status=1)
            db.session.add(action)
            db.session.commit()
            send_action_mail(leave)
            update_log(g.user.id,"Approved leave request id "+str(leave.id))
            return redirect(url_for("requests"))
    elif g.user.id == leave.requested_by.id and action == "c" and not leave.action:
        action = Leave_action(leave_id=leave.id,user_id=g.user.id,status=3)
        db.session.add(action)
        db.session.commit()
        update_log(g.user.id,"Cancelled leave request id "+str(leave.id))
        return redirect(url_for("leaves"))
    return render_template("lost.html")

@app.route('/requests/')
def requests():
    if g.user:
        if g.user.role == 3 or g.user.leading:
            dicto = get_approved_leaves(date.today(), 40)
            high = max(dicto.values())+2
            if g.user.role == 3:
                all_leaves = Leave.query.all()
            else:
                all_leaves = get_myteam_leaves(g.user.id)
            return render_template("requests.html", leaves=all_leaves,key=json.dumps(list(dicto.keys())), val=json.dumps(list(dicto.values())),high=json.dumps(high))
        else:
            return redirect(url_for("overview"))
    else:
        return render_template("login.html")

@app.route('/company/settings/', methods=["GET","POST"])
def company_set():
    if g.user.role == 3:
        if request.method == "POST":
            #Update company logo
            image = request.files['image']
            if image.filename != "" and image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], "company.jpg"))
            name = request.form['name']
            leave_calender = request.form['leave_calender']
            week_start = request.form['week_start']
            currency = request.form['currency']
            day_list = []
            day_list.append(request.form.get('sunday'))
            day_list.append(request.form.get("monday"))
            day_list.append(request.form.get("tuesday"))
            day_list.append(request.form.get("wednesday"))
            day_list.append(request.form.get("thursday"))
            day_list.append(request.form.get("friday"))
            day_list.append(request.form.get("saturday"))
            off_days = ""
            for day in day_list:
                if day:
                    off_days += day+","

            company = Organization.query.get(1)
            company.name = name
            company.leave_calender = leave_calender
            company.week_start = week_start
            company.week_off = off_days.rstrip(',')
            company.currency = currency
            db.session.commit()
            update_log(g.user.id,"Updated company settings")
            return redirect("/edit-profile/"+str(g.user.id))
        company = Organization.query.first()
        if company.week_off:
            weekends = list(map(int, company.week_off.split(",")))
        else:
            weekends =[]
        return render_template("company_settings.html",company=company,weekends=weekends)
    else:
        return redirect(url_for(overview))

@app.route('/logs/')
def get_logs():
    if g.user:
        if g.user.role == 3:
            logs = Activity_log.query.all()
            return render_template("log.html", logs=logs)
        else:
            return redirect(url_for(overview))
    else:
        return render_template("login.html")


"""
Starting of functions
"""
#Set session browser cookie with 3 layer security
def set_session_cookie(user):
    session["uid"] = user.id
    session["sk"] = bcrypt.generate_password_hash(user.name).decode("utf-8")

def clear_session_cookie():
    session.pop("uid", None)
    session.pop("sk", None)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_token(email):
    user = User.query.filter_by(email=email).first()
    if user:
        if user.token:
            db.session.delete(user.token[0])
            db.session.commit()
        token = secrets.token_urlsafe(20)
        created_date = date.today()
        access_token = Access_token(key=token,user_id=user.id,created_date=created_date)
        db.session.add(access_token)
        db.session.commit()
        return token

def is_email_unique(email_id):
    result = True
    users = User.query.all()
    for user in users:
        if user.email == email_id:
            result = False
    return result

def update_log(user_id,text):
    time = datetime.now()
    activity = Activity_log(time=time, user_id=user_id, description=text)
    db.session.add(activity)
    db.session.commit()

def get_myteam_leaves(user_id):
    leaves = []
    user = User.query.get(user_id)
    for team in user.leading:
        for member in team.team.members:
            for leave in member.members.leaves:
                leaves.append(leave)
    return leaves

def get_team_leads(user_id):
    team_leads = []
    user = User.query.get(user_id)
    for team in user.member_of:
        for admin in team.team.leads:
            team_leads.append(admin.manager)
    return team_leads

def this_week_summary():
    dic=[]
    week = week_range()
    from_d = week["start"]
    to_date = week["end"]
    leaves = get_leaves(from_d,to_date)
    birthday = get_birthdays(from_d,to_date)
    holidays = get_holidays(from_d,to_date)
    dic.append(leaves)
    dic.append(birthday)
    dic.append(holidays)
    return dic

def get_leaves(from_d,to_date):
    dic = [] 
    leaves = Leave.query.filter(Leave.to_date >= from_d).filter(Leave.from_date <= to_date).filter(Leave.action.any(status=1)).all()
    for leave in leaves:
        item = {}
        user = leave.requested_by
        item["user_id"] = user.id
        item["user_dp"] = user.dp
        item["user_name"] = user.name
        item["leave_category"] = leave.category
        item["leave_till"] = leave.to_date
        dic.append(item)
    return dic

def get_birthdays(from_d,to_date):
    dic = []
    users = User.query.filter(User.password.isnot(None)).all()
    for user in users:
        if user.dob:
            if user.dob >= from_d.replace(year=user.dob.year) and user.dob <= to_date.replace(year=user.dob.year):
                item = {}
                item["user_id"] = user.id
                item["user_dp"] = user.dp
                item["user_name"] = user.name
                item["dob"] = user.dob
                dic.append(item)
    return dic

def get_holidays(from_d,to_date):
    dic = []
    holidays = Holiday.query.filter(Holiday.end_date >= from_d).filter(Holiday.start_date <= to_date).all()
    for holiday in holidays:
        item = {}
        item["name"] = holiday.name
        item["from"] = holiday.start_date
        item["to"] = holiday.end_date
        dic.append(item)
    return dic

def week_range():
    today = date.today()
    today += timedelta(days=6)
    idx = (today.weekday() + 1) % 7
    #Sun =0, Sat =6, Fri =5, Thu =4, Wed =3, Tue =2, Mon=1
    start = today - timedelta(7+idx-1)
    end = start + timedelta(days=6)
    days = {"start":start,"end":end}
    return days

def count_leaves(from_date,end_date):
    week_off = Organization.query.get(1).week_off
    weekends = list(map(int, week_off.split(",")))
    #weekday -> Monday=0, Tuesday=1 etc.
    count = 0
    starting = from_date
    while from_date <= end_date:
        if from_date.weekday() in weekends:
            count +=1
        elif Holiday.query.filter(Holiday.start_date <= from_date).filter(Holiday.end_date >= from_date).scalar():
            count +=1
        from_date += timedelta(days=1)
    date_range = end_date - starting
    leave_length = (date_range.days +1) - count
    return leave_length

def calender_events():
    #daysOfWeek -> Sunday=0, Monday=1 etc.
    holiday_list = []
    week_off = Organization.query.get(1).week_off
    weekends = list(map(int, week_off.split(",")))
    for day in weekends:
        if day == 6:
            day_id = 0
        else:
            day_id = day+1
        item  ={}
        item["daysOfWeek"] = [day_id]
        item["title"] = "Weekend"
        item["classNames"] = 'week-holiday'
        holiday_list.append(item)
    holidays = Holiday.query.all()
    for holiday in holidays:
        item = {}
        item["title"] = holiday.name
        item["start"] = holiday.start_date.strftime("%Y-%m-%d")
        end = holiday.end_date+ timedelta(days=1)
        item["end"] = end.strftime("%Y-%m-%d")
        holiday_list.append(item)
    return holiday_list

def get_approved_leaves(from_d, length):
    dic = {}
    to_d = date.today() + timedelta(days=length)
    leaves = Leave.query.filter(Leave.to_date >= from_d).filter(Leave.from_date <= to_d).filter(Leave.action.any(status=1)).all()
    
    while from_d <= to_d:
        count = 0
        for leave in leaves:
            if leave.from_date <= from_d and leave.to_date >= from_d:
                count+=1
        dic[from_d.strftime("%d %b")] = count
        from_d += timedelta(days=1)

    return dic

def send_activation_mail(subject,sender,reciever,link):
    msg = Message(subject,
                  recipients=[reciever.email])
    msg.body = "" 
    msg.html = render_template('emails/activation.html', sender=sender,reciever=reciever,link=link)       
    mail.send(msg)
    return True

def send_reset_mail(subject,reciever,link):
    msg = Message(subject,
                  recipients=[reciever.email])
    msg.body = "" 
    msg.html = render_template('emails/password_reset.html', reciever=reciever,link=link)       
    mail.send(msg)
    return True

def send_action_mail(leave):
    if leave.action[0].status == 1:
        status = "Approved"
    elif leave.action[0].status == 2:
        status = "Declined"

    receiver = leave.requested_by
    sender = leave.action[0].actioned_by

    subject = receiver.name+", Your Leave Got "+status
    msg = Message(subject,
                  recipients=[receiver.email])
    msg.body = "" 
    msg.html = render_template('emails/leave_action.html', sender=sender, receiver=receiver, status=status)       
    mail.send(msg)
    return True

def send_request_mail(from_date,to_date,category,user):

    sender = g.user
    subject = "New leave request from "+sender.name
    msg = Message(subject,
                  recipients=[user.email])
    msg.body = "" 
    msg.html = render_template('emails/leave_request.html', sender=sender, user=user, from_date=from_date, to_date=to_date, category=category)       
    mail.send(msg)
    return True

def send_holiday_announcement(name, from_date, to_date, reciever):
    sender = g.user
    if from_date == to_date:
        duration = "on "+from_date.strftime('%d %b %Y')
    else:
        duration = "from "+from_date.strftime('%d %b')+" to "+to_date.strftime('%d %b %Y')
    subject = name+" holiday announced"
    msg = Message(subject,
                recipients=[reciever.email])
    msg.body = ""
    msg.html = render_template("emails/holiday_announce.html", sender=sender, name=name, duration=duration)
    mail.send(msg)
    return True

"""
Starting of error handles
"""
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404



if __name__ == "__main__":
    app.run(debug=True)