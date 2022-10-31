import os
import dotenv
import flask
import jwt
import time
import bcrypt
import sqlite3
import string

import validation

DATABASE = "subete.db"

app = flask.Flask(__name__)
dotenv.load_dotenv("config.env")

class User:
    def __init__(self, _id=None, username=None, hash=None, salt=None, first_name=None, last_name=None):
        self._id = _id
        self.username = username
        self.hash = hash
        self.salt = salt
        self.first_name = first_name
        self.last_name = last_name

class Student:
    def __init__(self, _id=None, class_id=None, first_name=None, last_name=None, hash=None, salt=None):
        self._id = _id
        self.hash = hash
        self.salt = salt
        self.first_name = first_name 
        self.last_name = last_name

class StudentClass:
    def __init__(self, _id=None, teacher_id=None, name=None):
        self._id = _id
        self.teacher_id = teacher_id
        self.name = name



def get_db():
    db = getattr(flask.g, '_database', None)
    if db is None:
        db = flask.g._database = sqlite3.connect(DATABASE)
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def check_credentials(username, password):
    user = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)

    if user is None:
        return False

    hash = user[4]
    return bcrypt.checkpw(password.encode("utf-8"), hash), user
    
def check_credentials_student(first_name, password, class_id):
    db = get_db()
    student = query_db("SELECT * FROM students WHERE first_name = ? AND class_id = ?", (first_name, class_id), one=True)

    if student is None:
        return False

    hash = student[3]
    return bcrypt.checkpw(password.encode("utf-8"), hash), student

def create_session_token(user_id, is_student=False):
    payload = {"uid": user_id, "student": is_student, "exp": int(time.time()) + int(os.getenv("SESSION_DURATION"))}
    token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
    return token

def parse_session_token(token):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return False

    return payload

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()


@app.route("/api/register", methods=["POST"])
def register():
    data = flask.request.get_json()
    
    if not validation.verify_form(data, ["first_name", "last_name", "username", "password"]):
        return flask.jsonify({"error": "missing required fields"}), 400

    if not (validation.verify_name(data["first_name"]) and validation.verify_name(data["last_name"]) and validation.verify_username(data["username"]) and validation.verify_password(data["password"])): 
        return flask.jsonify({"error": "invalid or malformed request"}), 400
    
    # check if username already exists
    if query_db("SELECT * FROM users WHERE username = ?", (data["username"],)):
        return flask.jsonify({"error": "username already exists"}), 401

    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(data["password"].encode('utf-8'), salt)
    
    db = get_db()
    db.execute(
        "INSERT INTO users (username, first_name, last_name, password, salt, is_admin, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (data["username"], data["first_name"], data["last_name"], hash, salt, 0, int(time.time()))
    )
    db.commit()
    
    return flask.jsonify({"success": True}), 200
    
@app.route("/api/register/student", methods=["POST"])
def register_student():
    data = flask.request.get_json()

    if not validation.verify_form(data, ["first_name", "password", "class_id"]):
        return flask.jsonify({"error": "missing required fields"}), 400

    if not validation.verify_name(data["first_name"]) or not validation.verify_password(data["password"]):
        return flask.jsonify({"error": "invalid or malformed request"}), 400

    
    db = get_db()
    # check classid exists
    class_exists = query_db("SELECT * FROM classes WHERE id = ?", (data["class_id"],), one=True)
    if not class_exists:
        return flask.jsonify({"error": "class not found"}), 404
    
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(data["password"].encode('utf-8'), salt)
    
    db.execute(
                "INSERT INTO students (first_name, password, salt, class_id) VALUES (?, ?, ?, ?)",
                (data["first_name"], hash, salt, data["class_id"])
    )
    db.commit()

    # get student id and create session token
    student_id = query_db("SELECT id FROM students WHERE first_name = ? AND class_id = ?",(data["first_name"], data["class_id"]), one=True)[0]
    
    token = create_session_token(student_id, is_student=True)
    response = flask.make_response(flask.jsonify({"success": True}))
    response.set_cookie("session", token)

    return response, 200

@app.route("/api/login", methods=["POST"])
def login():
    data = flask.request.get_json()
    
    # data validation
    if not validation.verify_form(data, ["username", "password"]):
        return flask.jsonify({"error": "missing required fields"}), 400
    if not (validation.verify_username(data["username"]) and validation.verify_password(data["password"])):
        return flask.jsonify({"error": "invalid or malformed request"}), 400

    # query user
    success, user = check_credentials(data["username"], data["password"])

    # if successful login, create jwt token and send as cookie
    if success:
        token = create_session_token(user[0])
        response = flask.make_response(flask.jsonify({"success": True}))
        response.set_cookie("session", token)
        
        return response, 200
    else:
        return flask.jsonify({"error": "invalid username and/or password"}), 401
    
@app.route("/api/login/student", methods=["POST"])
def login_student():
    data = flask.request.get_json()

    if not validation.verify_form(data, ["class_id", "first_name", "password"]):
        return flask.jsonify({"error": "missing required fields"}), 400
    if not (validation.verify_name(data["first_name"]) and validation.verify_password(data["password"])):
        return flask.jsonify({"error": "invalid or malformed request"}), 400

    success, student = check_credentials_student(data["first_name"], data["password"], data["class_id"])

    if success:
        token = create_session_token(student[0], is_student=True)
        response = flask.make_response(flask.jsonify({"success": True}))
        response.set_cookie("session", token)

        return response, 200

    else:
        return flask.jsonify({"error": "invalid username and/or password"}), 401

@app.route("/api/actions/create_class", methods=["POST"]) 
def create_class():
    token = flask.request.cookies.get("session")
    if not token:
        return flask.jsonify({"error": "unauthorized"}), 401
    
    payload = parse_session_token(token)
    if not payload:
        return flask.jsonify({"error": "unauthorized"}), 401

    if payload["student"]:
        return flask.jsonify({"error": "unauthorized"}), 401

    data = flask.request.get_json()
    if not validation.verify_form(data, ["name"]):
        return flask.jsonify({"error": "missing required fields"}), 400

    if not validation.verify_username(data["name"]):
        return flask.jsonify({"error": "invalid or malformed request"}), 400

    # check for class with same name under same teacher id
    if query_db("SELECT * FROM classes WHERE teacher_id = ? AND name = ?", (payload["uid"], data["name"])):
        return flask.jsonify({"error": "class with that name already exists"}), 400
    
    db = get_db()
    db.execute("INSERT INTO classes (teacher_id, name) VALUES (?, ?)", (payload["uid"], data["name"]))
    db.commit()

    class_id = query_db("SELECT id FROM classes WHERE teacher_id = ? AND name = ?", (payload["uid"], data["name"]), one=True)[0]

    return flask.jsonify({"success": True, "class_id": class_id}), 200

@app.route("/api/actions/submit", methods=["POST"])
def submit_score():
    token = flask.request.cookies.get("session")
    if not token:
        return flask.jsonify({"error": "unauthorized"}), 401

    payload = parse_session_token(token)
    if not payload:
        return flask.jsonify({"error": "unauthorized"}), 401

    if not payload["student"]:
        return flask.jsonify({"error": "unauthorized"}), 401

    data = flask.request.get_json()

    if not validation.verify_form(data, ["score", "elapsed"]):
        return flask.jsonify({"error": "invalid or malformed request"})

    student_id = payload["uid"]

    # check for valid student_id 
    if not query_db("SELECT * FROM students WHERE id = ?", (student_id,), one=True):
        return flask.jsonify({"error": "unauthorized"}), 401

    db = get_db()
    db.execute(
        "INSERT INTO score (student_id, score, elapsed, created_at) VALUES (?, ?, ?, ?)",
        (student_id, data["score"], data["elapsed"], int(time.time()))
    )
    db.commit()

    return flask.jsonify({"success": True}), 200

if __name__ == '__main__':
    app.run(debug=True)