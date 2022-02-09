# Todo:
# RECREATE DATABASE WITH SIGNULAR NAME FOR EACH TABLE, GET TABLE CREATION SCRIPT FROM MYSQL 
# UH OH I CAN NOT DO THAT
# ADD ANOTHER ROW TO THE CATEGORIES CONSTANT (SUCKS I KNOW) WITH TABLE NAMES

import constants

import os
import sys
from datetime import datetime
from tempfile import mkdtemp

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, send_from_directory
from flask_session import Session

import mysql.connector

from werkzeug.utils import secure_filename
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

from dotenv import load_dotenv

# Initialize Constants 
load_dotenv()
DATABASE_NAME = os.environ.get("databaseName")
HOST = os.environ.get("host")
USER = os.environ.get("user")
PASSWORD = os.environ.get("password")

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "uploads/"
#app.config["SERVER_NAME"] = "cvhsrocketry.org"

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database 
db = mysql.connector.connect(
    host=HOST,
    user=USER,
    password=PASSWORD,
    database=DATABASE_NAME
)
cursor = db.cursor()

def extractColumn(matrix, i):
    return [row[i] for row in matrix]

def checkFields(elementNames):
    for elementName in elementNames:
        if not request.form.get(elementName):
            print("attempting to print error", flush=True)
            return apology(f"must provide {elementName}")

def addPart(tableName, elementNames, columnNames):
    # Check if all fields are filled 
    result = checkFields(elementNames[:-1])
    if result != None:
        return result
    
    # Get the value of all fields 
    elementValues = []
    for elementName in elementNames[:-1]:
        elementValues.append(request.form.get(elementName))
    if not request.form.get(elementNames[-1]):
        elementValues.append(0)
    else:
        elementValues.append(request.form.get(elementNames[-1]))
    
    # Create and execute query to get all matching entries 
    query = f"SELECT * FROM {tableName} WHERE {columnNames[0]} = %s"
    for i in range(1, len(columnNames[:-1])):
        query += f" AND {columnNames[i]} = %s"
    print(query, flush=True)
    print(elementValues, flush=True)
    cursor.execute(query, tuple(elementValues[:-1]))
    entries = cursor.fetchall()
 
    if len(entries) != 0:
        # elementValues[-1] is the quantity to be added
        newQuantity = int(entries[0][len(columnNames)-1]) + int(elementValues[-1])

        # Create and execute query to update entry with newQuantity 
        query = f"UPDATE {tableName} SET quantity = %s WHERE {columnNames[0]} = %s"
        for i in range(1, len(columnNames[:-1])):
            query += f"AND {columnNames[i]} = %s"
        cursor.execute(query, tuple(newQuantity, *elementValues[:-1]))
        entries = cursor.fetchall()

        updateLogs(entries[0]['id'], "tubes", newQuantity)
    else:
        # Create and execute query to insert new entry 
        query = f"INSERT INTO {tableName} ({columnNames[0]}"
        for i in range(1, len(columnNames)):
            query += f", {columnNames[i]}"
        query += f") VALUES({(len(columnNames[:-1]) * f'%s, ')}%s)"
        cursor.execute(query, tuple(elementValues))
        db.commit()

        # Get the id of the last inserted entry 
        cursor.execute("SELECT LAST_INSERT_ID()")
        entryID = cursor.fetchone()[0]

        updateLogs(entryID, tableName, elementValues[-1])
    return redirect(url_for('parts'))

def updatePart(part, name, columnNames, tableName):
    change = request.form.get(f"{name}_{str(part[0])}_change")
    if change == "":
        change = "0"
    # use len(columnNames) instead of len(columnNames) - 1 because columnNames does not include the id column 
    new_quantity = int(part[len(columnNames)]) + int(change)
    print(f"Current quant: {part[len(columnNames)]} | Change: {change} | New quant: {new_quantity}", flush=True)
    if new_quantity < 0:
        new_quantity = 0
    cursor.execute(f"UPDATE {tableName} SET quantity = %s WHERE id = %s", (new_quantity, part[0]))
    db.commit()
    return redirect(url_for('parts'))

def deletePart(part, tableName, redirectLocation):
    cursor.execute(f"DELETE FROM {tableName} WHERE id = %s", (part[0],))
    db.commit()
    updateLogs(part[0], "part_requests", 404)
    return redirect(url_for(redirectLocation))

def addRequest(partName, elementNames):
    result = checkFields(elementNames[:-1])
    if result != None:
        return result

    # Set variables
    dateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    category = request.form.get("category")
    if not request.form.get(elementNames[-1]):
        quantity = 0
    else:
        quantity = request.form.get(elementNames[-1])

    cursor.execute("INSERT INTO part_requests (user, datetime, category, name, quantity) VALUES(%s, %s, %s, %s, %s)",
                (getUsername(), dateTime, category, partName, quantity))
    db.commit()

    # Get the id of the last inserted entry
    cursor.execute("SELECT LAST_INSERT_ID()")
    entryID = cursor.fetchone()[0]

    updateLogs(entryID, "part_requests", quantity)
    return redirect(url_for('requests'))

def getUsername():
    cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
    username = cursor.fetchone()[0]
    print("username: " + username, flush=True)
    return username

def updateLogs(entryID, table, quantityChange):
    dateTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO logs (datetime, username, entry_id, quantity_change, table_name) VALUES(%s, %s, %s, %s, %s)",
            (dateTime, getUsername(), entryID, quantityChange, table))
    db.commit()

@app.route("/")
@login_required
def index():
    print(session['user_id'], flush=True)
    cursor.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],))
    username = cursor.fetchone()[0]
    return render_template("index.html", username=username)

@app.route("/parts", methods=["GET", "POST"])
@login_required
def parts():

    tables = []
    for i in range(len(constants.CATEGORIES)):
        cursor.execute(f"SELECT * FROM {constants.CATEGORIES[i][constants.TABLE_NAME_INDEX]}")
        rows = cursor.fetchall()
        tables.append(rows)

    if request.method == "POST":
        # Add parts 
        if request.form.get("submit"):
            for category in constants.CATEGORIES:
                if request.form.get("category") == category[constants.TABLE_NAME_INDEX]:

                    # REMOVE FOR GITHUB
                    if request.form.get("category") == "Motors":
                        if len(request.form.get("motor_class")) != 1:
                            return apology("motor class must be a single character", 400)

                    return addPart(category[constants.TABLE_NAME_INDEX], category[constants.ELEMENT_INDEX], category[constants.COLUMN_INDEX])
            return apology("an error occurred while adding a part", 500)

        # TODO: ADD lOGS FOR UPDATING PARTS
        # Update parts 
        for i in range(len(tables)):
            for entry in tables[i]:
                if request.form.get(f"{constants.CATEGORIES[i][constants.NAME_INDEX]}_{str(entry[0])}_update"):
                    return updatePart(entry, constants.CATEGORIES[i][constants.NAME_INDEX], constants.CATEGORIES[i][constants.COLUMN_INDEX], constants.CATEGORIES[i][constants.TABLE_NAME_INDEX])
                elif request.form.get(f"{constants.CATEGORIES[i][constants.NAME_INDEX]}_{str(entry[0])}_remove"):
                    return deletePart(entry, constants.CATEGORIES[i][constants.TABLE_NAME_INDEX], "parts")
        return apology("an error occured while updating an entry", 500)
    # If method is get 
    else:
        # Give only the arrays with column names
        names = extractColumn(constants.CATEGORIES, constants.NAME_INDEX)
        tableNames = extractColumn(constants.CATEGORIES, constants.TABLE_NAME_INDEX)
        columns = extractColumn(constants.CATEGORIES, constants.COLUMN_INDEX) 
        unifData = []
        for i in range(len(tables)):
            unifData.append([tables[i], names[i], tableNames[i], columns[i]])
        return render_template("parts.html", data=unifData)

@app.route("/requests", methods=["GET", "POST"])
@login_required
def requests():
    if request.method == "POST":
        if request.form.get("part_submit"):
            for category in constants.CATEGORIES:
                if request.form.get("category") == category[constants.NAME_INDEX]:
                    partName = constants.processRequest(category[constants.NAME_INDEX])
                    return addRequest(partName, category[constants.REQUEST_ELEMENTS_INDEX])
            return apology("an error occured while adding a part request", 500)

        cursor.execute("SELECT * FROM part_requests")
        part_requests = cursor.fetchall()
        for part_request in part_requests:
            request_id = str(part_request[0])
            if request.form.get("request_" + request_id + "_update"):
                newStatus = request.form.get("request_" + request_id + "_status")
                cursor.execute("UPDATE part_requests SET status = %s WHERE id = %s", (newStatus, request_id))
                db.commit()
                return redirect(url_for('requests'))
            elif request.form.get("request_" + request_id + "_remove"):
                return deletePart(part_request, "part_requests", "requests")

        cursor.execute("SELECT * FROM creation_requests")
        creation_requests = cursor.fetchall()
        for creation_request in creation_requests:
            request_id = str(creation_request[0])
            if request.form.get("c_request_" + request_id + "_update"):
                newStatus = request.form.get("c_request_" + request_id + "_status")
                cursor.execute("UPDATE creation_requests SET status = %s WHERE id = %s", (newStatus, request_id))
                db.commit()
                return redirect(url_for('requests'))
            elif request.form.get("c_request_" + request_id + "_remove"):
                return deletePart(creation_request, "creation_requests", "requests")
        return apology("an error occurred while updating a request entry", 500)
    else:
        # Give only the arrays with column names
        names = extractColumn(constants.CATEGORIES, constants.NAME_INDEX)
        tableNames = extractColumn(constants.CATEGORIES, constants.TABLE_NAME_INDEX)
        elements = extractColumn(constants.CATEGORIES, constants.REQUEST_ELEMENTS_INDEX) 
        unifData = []
        for i in range(len(names)):
            unifData.append([names[i], tableNames[i], elements[i]])

        cursor.execute("SELECT * FROM part_requests")
        part_requests = cursor.fetchall()
        cursor.execute("SELECT * FROM creation_requests")
        creation_requests = cursor.fetchall()
        return render_template("requests.html", p_requests=part_requests, c_requests=creation_requests, uploadCats=constants.UPLOAD_CATEGORY, data=unifData)

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        f = request.files['file']
        if os.path.exists("uploads/" + f.filename):
            return apology("that file already exists. Please rename it and try again", 403)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        # Create log 
        cursor.execute("INSERT INTO creation_requests (category, name) VALUES(%s, %s)",
                    (request.form.get("upload_category"), f.filename))
        db.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        creation_id = cursor.fetchone()[0]
        updateLogs(creation_id, "creation_requests", 1)
        return redirect(url_for('requests'))

@app.route("/download", methods=["GET", "POST"])
@login_required
def download():
    cursor.execute("SELECT * FROM creation_requests")
    creation_requests = cursor.fetchall()
    for c_request in creation_requests:
        request_id = str(c_request[0])
        if request.form.get("c_request_" + request_id + "_download"):
            folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            return send_from_directory(directory = folder, path = secure_filename(c_request[2]), as_attachment=True)
    return apology("an error occured while downloading a file", 500)

@app.route("/logs")
@login_required
def logs():
    cursor.execute("SELECT * FROM logs ORDER BY datetime DESC")
    logs = cursor.fetchall()
    return render_template("logs.html", logs=logs)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        result = checkFields(['username', 'password', 'passwordComf', 'registration_code'])
        if result != None:
            return result
        if request.form.get("password") != request.form.get("passwordComf"):
            return apology("passwords must match", 403)

        cursor.execute("SELECT hash FROM registration_codes")
        registrationCodeEntries = cursor.fetchall()
        valid = False
        for entry in registrationCodeEntries:
            if check_password_hash(entry[0], request.form.get("registration_code")):
                valid = True
                cursor.execute("DELETE FROM registration_codes WHERE hash = %s", (entry[0],))
                db.commit()
        if valid == False:
            return apology("registration code is invalid", 403)

        cursor.execute("SELECT * FROM users WHERE username = %s",
                          (request.form.get("username"),))
        usernameEntries = cursor.fetchall() 
        if len(usernameEntries) != 0:
            return apology("account with username already exists", 403)

        cursor.execute("INSERT INTO users (username, hash) VALUES(%s, %s)",
                    (request.form.get("username"), generate_password_hash(request.form.get("password"))))
        db.commit()
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        cursor.execute("SELECT * FROM users WHERE username = %s",
                          (request.form.get("username"),))
        entries = cursor.fetchall()
        if len(entries) != 1 or not check_password_hash(entries[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        session["user_id"] = entries[0][0]
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    # Configure SQL tables, create them if they do not exist 
    tables = constants.CATEGORIES
    for i in range(len(tables)):
        cursor.execute("SELECT * FROM information_schema.tables WHERE table_name = %s", (tables[i][constants.TABLE_NAME_INDEX],))
        if len(cursor.fetchall()) != 1:
            cursor.execute(tables[i][constants.QUERY_INDEX])
            db.commit()
    #app.run(host= '0.0.0.0', port="4823")
    app.run(debug=True)

