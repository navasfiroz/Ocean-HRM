from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return "Organization id :"+str(self.id)

db.create_all()
new_org = Organization(name="Tawook Nation")
db.session.add(new_org)
print(Organization.query.get(1).name)


# @app.route('/')
# def index_page():
#     return render_template("index.html")

# app.run(debug=True)

