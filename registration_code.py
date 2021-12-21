#import os

import mysql.connector
import os

from werkzeug.utils import secure_filename
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from dotenv import load_dotenv

load_dotenv()
databaseName = os.environ.get("databaseName")
host = os.environ.get("host")
user = os.environ.get("user")
password = os.environ.get("password")
db = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=databaseName
)
cursor = db.cursor()

code = input("Enter registration code: ")
while code != "exit":
    hash = generate_password_hash(code)
    cursor.execute("INSERT INTO registration_codes (hash) VALUES(%s)", (hash,))
    db.commit()
    code = input("Enter registration code or enter 'exit' to stop: ")
