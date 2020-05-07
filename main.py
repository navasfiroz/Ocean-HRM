from flask import Flask, render_template
from objects import Organization

# app = Flask(__name__)

# @app.route('/')
# def index_page():
#     return render_template("index.html")

# app.run(debug=True)

jp = Organization("JustProperty")

print(jp)