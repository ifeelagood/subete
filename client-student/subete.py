import sys
import requests
import numpy as np

from OpenGL import GL
from PySide6.QtWidgets import QMainWindow, QGridLayout, QVBoxLayout, QHBoxLayout, QApplication, QWidget, QLabel, QLineEdit, QPushButton, QErrorMessage
from PySide6.QtOpenGLWidgets import QOpenGLWidget

URL = "http://localhost:5000"

class SubeteAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def login(self, first_name, password, class_id):
        r = self.session.post(URL + "/api/login/student", json={"first_name": first_name, "password": password, "class_id": class_id})
        return r.status_code == 200
        

class SubeteWidgetGL(QOpenGLWidget):
    def __init__(self):
        super().__init__()

    def initializeGL(self):
        vertices = np.array([0.0, 1.0, -1.0, -1.0, 1.0, -1.0], dtype=np.float32)

        bufferId = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, bufferId)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, None)

    def paintGL(self):
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("subete")
        
        self.api = SubeteAPI()

        # WIDGETS


        self.q_label_login = QLabel("Login")
        self.q_line_name = QLineEdit()
        self.q_line_pass = QLineEdit()
        self.q_line_class = QLineEdit()
        self.q_pushbutton_login = QPushButton("Submit")

        self.q_pushbutton_login.clicked.connect(self.submit_login)

        self.q_label_name = QLabel("First Name")
        self.q_label_pass = QLabel("Password")
        self.q_label_class = QLabel("Class ID")


        self.layout_login = QGridLayout()
        self.layout_login.addWidget(self.q_label_login,      0, 1)
        self.layout_login.addWidget(self.q_line_name,        1, 1)
        self.layout_login.addWidget(self.q_line_pass,        2, 1)
        self.layout_login.addWidget(self.q_line_class,       3, 1)
        self.layout_login.addWidget(self.q_pushbutton_login, 4, 1)

        self.layout_login.addWidget(self.q_label_name,       1, 0)
        self.layout_login.addWidget(self.q_label_pass,       2, 0)
        self.layout_login.addWidget(self.q_label_class,      3, 0)

        self.centre_widget = QWidget()
        self.centre_widget.setLayout(self.layout_login)
        self.setCentralWidget(self.centre_widget)

        self.show()

    def submit_login(self):
        first_name = self.q_line_name.text().rstrip()
        password = self.q_line_pass.text().rstrip()
        class_id = self.q_line_class.text().rstrip()

        login_success = self.api.login(first_name, password, class_id)
        if login_success:
            print("Login success!")
        else:
            print("Login failure")

        print(first_name, password, class_id)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()