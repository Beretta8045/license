from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from passlib.hash import sha256_crypt
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
import random
import string
from datetime import timedelta
import mysql.connector

app = Flask(__name__)
secret_key = os.urandom(24)
app.secret_key = secret_key  # Replace with your secret key

# Configure MySQL databases
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://gtguser:tQ7V<=u86={n$rqW2H.]@gtglicensedb.eastus.cloudapp.azure.com:3306/authentication'
app.config['SQLALCHEMY_BINDS'] = {
    'license_db': 'mysql+mysqlconnector://gtguser:tQ7V<=u86={n$rqW2H.]@gtglicensedb.eastus.cloudapp.azure.com:3306/license'
}
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User model for authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Form for generating license
class LicenseForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired()])
    contact_name = StringField('Contact Name', validators=[DataRequired()])
    contact_email = StringField('Contact Email', validators=[DataRequired()])
    num_users = IntegerField('Number of Users', validators=[DataRequired()])
    generate_license = SubmitField('Generate License')

# Define the database structure for storing licenses
class License(db.Model):
    __bind_key__ = 'license_db'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    num_users = db.Column(db.Integer, nullable=False)
    license_key = db.Column(db.String(50), nullable=False)

# Function to generate a random license key
def generate_license_key(length=20):
    characters = string.ascii_letters + string.digits
    license_key = ''.join(random.choice(characters) for _ in range(length))
    return license_key

# Function to save license data to the database
def save_license_data(company_name, contact_name, contact_email, num_users, license_key):
    license_data = License(
        company_name=company_name,
        contact_name=contact_name,
        contact_email=contact_email,
        num_users=num_users,
        license_key=license_key
    )
    db.session.add(license_data, bind='license_db')
    db.session.commit()

# Set session timeout to 15 minutes (900 seconds)
app.permanent_session_lifetime = timedelta(seconds=900)

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/generate_license", methods=["GET", "POST"])
@login_required
def generate_license():
    form = LicenseForm()

    if form.validate_on_submit():
        company_name = form.company_name.data
        contact_name = form.contact_name.data
        contact_email = form.contact_email.data
        num_users = form.num_users.data

        license_key = generate_license_key()
        save_license_data(company_name, contact_name, contact_email, num_users, license_key)

        flash(f"Generated License Key: {license_key}", "success")

    return render_template("generate_license.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and sha256_crypt.verify(password, user.password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
