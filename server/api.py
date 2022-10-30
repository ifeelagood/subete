import os
import dotenv
import flask
import jwt
import time
import bcrypt
import sqlite3

DATABASE = "subete.db"

app = flask.Flask(__name__)
dotenv.load_dotenv("config.env")


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

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()
        

@app.route("/api/register", methods=["POST"])
def register():
    data = flask.request.get_json()
    
    try:
        first_name = data["first_name"]
        last_name = data["last_name"]
        username = data["username"]
        password = data["password"]
    except KeyError:
        return flask.jsonify({"error": "Missing required fields"}), 400
        
    if not first_name or not last_name:
        return flask.jsonfiy({"error": "First and last name are required."}), 400
    if not password:
        return flask.jsonfiy({"error": "Password is required."}), 400
    
    if len(password) < 10:
        return flask.jsonfiy({"error": "Password must be at least 10 characters."}), 400
    if len(password) > 100:
        return flask.jsonfiy({"error": "Password must be less than 100 characters."}), 400
    
    if len(first_name) > 50:
        return flask.jsonify({"error": "First name is too long."}), 400
    
    if len(last_name) > 50:
        return flask.jsonify({"error": "Last name is too long."}), 400
    
    
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    db = get_db()
    db.execute("INSERT INTO users (username, first_name, last_name, password, salt, is_admin, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (username, first_name, last_name, hash, salt, 0, time.time()))
    db.commit()
    
    return flask.jsonify({"success": True}), 200


@app.route("/api/login", methods=["POST"])
def login():
    data = flask.request.get_json()
    
    try:
        username = data["username"]
        password = data["password"]
    except KeyError:
        return flask.jsonify({"error": "Missing required fields"}), 400
    
    if not username or not password:
        return flask.jsonify({"error": "Missing required fields"}), 400

    db = get_db()

    user = query_db("SELECT * FROM users WHERE username = ?", (username,), one=True)
    if not user:
        return flask.jsonify({"error": "Invalid username or password"}), 400

    print(user)


    salt = user[5]
    computed_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    actual_hash = user[4]
    
    if computed_hash != actual_hash:
        return flask.jsonify({"error": "Invalid username or password"}), 400
    else:
        payload = {
            "uid": user[0],
            "is_admin": user[6],
            "exp": time.time() + int(os.getenv("SESSION_DURATION"))
        }
        
        token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")
        response = flask.make_response(flask.jsonify({"success": True}))
        response.set_cookie("session", token)
        
        return response, 200
    
    
@app.route ("/api/protected", methods=["GET"])
def protected():
    token = flask.request.cookies.get("session")
    if not token:
        return flask.jsonify({"error": "unauthorized"}), 401
    
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return flask.jsonify({"error": "Session expired"}), 401
    except jwt.InvalidTokenError:
        return flask.jsonify({"error": "Invalid session token"}), 401
    
    return flask.jsonify({"success": payload}), 200
    
if __name__ == '__main__':
    app.run(debug=True)