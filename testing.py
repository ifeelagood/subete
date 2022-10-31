import requests
import json

URL = "http://localhost:5000"

TEACHER_USERNAME = "bigbaz123"
TEACHER_FIRSTNAME = "Jerry"
TEACHER_LASTNAME = "Jackson"
TEACHER_PASSWORD = "j3rryj4cks0n!!!"
CLASS_NAME = "class123"

STUDENT_FIRSTNAME = "Bobby"
STUDENT_PASSWORD = "i_like_eggs"

def teacher_test():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    
    # REGISTER
    data={"username": TEACHER_USERNAME, "password": TEACHER_PASSWORD, "first_name": TEACHER_FIRSTNAME, "last_name": TEACHER_LASTNAME}
    r = s.post(URL + "/api/register", json=data)

    if r.status_code == 200:
        print("Registered teacher user successfully.")
    else:
        print("failure registering teacher: ", r.text, r.status_code)

    # LOGIN FAILURE
    data = {"username": TEACHER_USERNAME + "asdaca", "password": TEACHER_PASSWORD}
    r = s.post(URL + "/api/login", json=data)
    if r.status_code != 200:
        print("Failed login successfully (invalid username)")
    else:
        print("Failed login unsuccessfully (invalid username)", r.text, r.status_code)

    data = {"username": TEACHER_USERNAME, "password": TEACHER_PASSWORD + "asdaca"}
    r = s.post(URL + "/api/login", json=data)
    if r.status_code != 200:
        print("Failed login successfully (invalid password)")
    else:
        print("Failed login unsuccessfully (invalid password)", r.text, r.status_code)

    # LOGIN
    data = {"username": TEACHER_USERNAME, "password": TEACHER_PASSWORD}
    r = s.post(URL + "/api/login", json=data)
    if r.status_code == 200:
        print("teacher login success")
    else:
        print("teacher login failure", r.text, r.status_code)


    # CREATE CLASS
    data = {"name": CLASS_NAME}
    r = s.post(URL + "/api/actions/create_class", json=data)

    if r.status_code == 200:
        print("Successfully created class")
        print("class_id:", json.loads(r.text)["class_id"])
    else:
        print("Failed to create class", r.text, r.status_code)

def student_test():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})

    # REGISTER
    data = {"first_name": STUDENT_FIRSTNAME, "password": STUDENT_PASSWORD, "class_id": 4}
    r = s.post(URL + "/api/register/student", json=data)

    if r.status_code == 200:
        print("successfully registered student")
    else:
        print("failed to register student", r.text, r.status_code)

    # LOGIN 
    data = {"first_name": STUDENT_FIRSTNAME, "password": STUDENT_PASSWORD, "class_id": 4}
    r = s.post(URL + "/api/login/student", json=data)

    if r.status_code == 200:
        print("successfully logged in as student")
    else:
        print("failure logging in as student", r.text, r.status_code)

    # SUBMIT SCORE

    data = {"score": 8, "elapsed": 23}
    r = s.post(URL + "/api/actions/submit", json=data)

    if r.status_code == 200:
        print("successfully submitted scores")
    else:
        print("failure submitting scores", r.text, r.status_code)

if __name__ == '__main__':
    student_test()