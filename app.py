from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import random
import string
import os

# Generate a random secret key
secret_key = os.urandom(24)


app = Flask(__name__)
app.secret_key = secret_key

# Function to generate a random license key
def generate_license_key(company_name, contact_name, contact_email, num_users):
    characters = string.ascii_letters + string.digits
    license_key = ''.join(random.choice(characters) for _ in range(20))  # Adjust length as needed
    obscured_license_key = f'{license_key}{num_users}'

    return obscured_license_key

# Function to save data to MySQL
def save_data_to_mysql(company_name, contact_name, contact_email, num_users, license_key):
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
        data = (company_name, contact_name, contact_email, num_users, license_key)

        cursor.execute(insert_query, data)
        connection.commit()
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash("An error occurred while saving data.", "error")

@app.route("/", methods=["GET", "POST"])
def generate_license():
    if request.method == "POST":
        company_name = request.form["company_name"]
        contact_name = request.form["technical_contact"]
        contact_email = request.form["contact_email"]
        num_users = request.form["num_users"]

        license_key = generate_license_key(company_name, contact_name, contact_email, num_users)

        save_data_to_mysql(company_name, contact_name, contact_email, num_users, license_key)

        flash(f"License Key: {license_key}", "success")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
