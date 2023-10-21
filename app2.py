from flask import Flask, render_template, request, redirect, url_for, flash
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
import random
import string
import os

app = Flask(__name)
app.secret_key = os.urandom(24)  # Replace with a secret key

# Configure authentication database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://gtguser:tQ7V<=u86={n$rqW2H.]@gtglicensedb.eastus.cloudapp.azure.com:3306/authentication'
db_auth = SQLAlchemy(app)

# Configure license keys database
app.config['SQLALCHEMY_LICENSES_DATABASE_URI'] = 'gtguser:tQ7V<=u86={n$rqW2H.]@gtglicensedb.eastus.cloudapp.azure.com:3306/license'
db_licenses = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# User model for authentication
class User(db_auth.Model, UserMixin):
    id = db_auth.Column(db_auth.Integer, primary_key=True)
    username = db_auth.Column(db_auth.String(50), unique=True, nullable=False)
    password = db_auth.Column(db_auth.String(128), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# License Key Generation and MySQL Storage
def generate_license_key(company_name, contact_name, contact_email, num_users):
    characters = string.ascii_letters + string.digits
    license_key = ''.join(random.choice(characters) for _ in range(20))  # Adjust length as needed
    obscured_license_key = f'{license_key}{num_users}'

    # Save data to MySQL for licenses
    db_config = {
        'host': 'gtglicensedb.eastus.cloudapp.azure.com',
        'user': 'gtguser',
        'password': 'tQ7V<=u86={n$rqW2H.]',
        'database': 'license',
    }

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        insert_query = "INSERT INTO licenses (company_name, contact_name, contact_email, num_users, license_key) VALUES (%s, %s, %s, %s, %s)"
        data = (company_name, contact_name, contact_email, num_users, obscured_license_key)

        cursor.execute(insert_query, data)
        connection.commit()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash("An error occurred while saving data.", "error")

@app.route("/", methods=["GET", "POST"])
def login_and_generate_license():
    if request.method == "POST":
        if 'generate_license' in request.form:
            company_name = request.form["company_name"]
            contact_name = request.form["technical_contact"]
            contact_email = request.form["contact_email"]
            num_users = request.form["num_users"]

            license_key = generate_license_key(company_name, contact_name, contact_email, num_users)

            flash(f"License Key: {license_key}", "success")
        elif 'login' in request.form:
            username = request.form["username"]
            password = request.form["password"]

            user = User.query.filter_by(username=username).first()
            if user and sha256_crypt.verify(password, user.password):
                login_user(user)
                flash("You are now logged in", "success")
                return redirect(url_for("index"))
            else:
                flash("Invalid username or password", "danger")

    return render_template("combined.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_and_generate_license"))

@app.route("/index")
@login_required
def index():
    return "Welcome to the dashboard. You are logged in!"

if __name__ == "__main__":
    app.run(debug=True)
