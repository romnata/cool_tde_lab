# initializes the PyQt5 application

import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QCheckBox
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt
from black_hole import BlackHoleScene
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.setWindowTitle("Cool TDE GUI")
        self.setGeometry(1900, 100, 1000, 900)  # x, y, width, height
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet(
            "QMainWindow { border-image: url(stars.png) 0 0 0 0 stretch stretch; }")

        label = QLabel("Welcome to Cool TDE Lab!", self)
        label.setFont(QFont("Helvetica", 20))
        label.setGeometry(0, -360, 1000, 900)
        label.setStyleSheet("color: white;"
                            "background: transparent;"
                            "font-weight: bold")

        label.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        # TR FORMULA
        self.pixmap_label = QLabel(self)
        pixmap = QPixmap("tidal_radius_formula.png")
        self.pixmap_label.setPixmap(pixmap)
        self.pixmap_label.setGeometry(600, 500, 350, 135)
        self.pixmap_label.setScaledContents(True)

        # INSTRUCTIONS
        self.simple_text = QLabel("  To add a star \n    or update \n     press 'T'.\n"
                                  " To start the TDE \n     press 'D'.", self)
        self.simple_text.setGeometry(600, 70, 500, 500)  # x, y, width, height
        self.simple_text.setStyleSheet(
            "color: white; background: transparent; font-size: 45px")

        # INPUT
        input_style = (
            "color: black;"
            "font-size: 45px;"
            "font-family: Helvetica;"
            "font-weight: bold;")

        # star radius
        self.input1 = QLineEdit(self)
        self.input1.setGeometry(60, 220, 210, 100)
        self.input1.setStyleSheet(input_style)
        self.input1.setPlaceholderText("R∗")

        # star mass
        self.input2 = QLineEdit(self)
        self.input2.setGeometry(60, 420, 210, 100)
        self.input2.setStyleSheet(input_style)
        self.input2.setPlaceholderText("M∗")

        # BH mass
        self.input3 = QLineEdit(self)
        self.input3.setGeometry(60, 620, 210, 100)
        self.input3.setStyleSheet(input_style)
        self.input3.setPlaceholderText("Mʙʜ")

        # SUBMIT BUTTONS
        button_style = (
            "color: black;"
            "font-size: 30px;"
            "font-family: Helvetica;"
            "font-weight: bold;"
            "background-color: #d1d0cf")
        # 1
        self.button1 = QPushButton("Submit", self)
        self.button1.setGeometry(310, 230, 150, 80)
        self.button1.setStyleSheet(button_style)
        self.button1.clicked.connect(self.submit1)

        # 2
        self.button2 = QPushButton("Submit", self)
        self.button2.setGeometry(310, 430, 150, 80)
        self.button2.setStyleSheet(button_style)
        self.button2.clicked.connect(self.submit2)

        # 3
        self.button3 = QPushButton("Submit", self)
        self.button3.setGeometry(310, 630, 150, 80)
        self.button3.setStyleSheet(button_style)
        self.button3.clicked.connect(self.submit3)

        # database
        data_button_style = (
            "color: black;"
            "font-size: 30px;"
            "font-family: Helvetica;"
            "font-weight: bold;"
            "background-color: #d1d0cf")

        self.data_button = QPushButton("Database", self)
        self.data_button.setGeometry(650, 690, 250, 100)
        self.data_button.setStyleSheet(data_button_style)
        self.data_button.clicked.connect(self.open_database)

        # TITLES
        # 1
        self.title_SR = QLabel("Star Radius (R☉):", self)
        self.title_SR.setFont(QFont("Helvetica", 14))
        self.title_SR.setStyleSheet("color: white; background: transparent;")
        self.title_SR.setGeometry(60, 170, 300, 40)  # x, y, width, height

        # 2
        self.title_SM = QLabel("Star Mass (M☉):", self)
        self.title_SM.setFont(QFont("Helvetica", 14))
        self.title_SM.setStyleSheet("color: white; background: transparent;")
        self.title_SM.setGeometry(60, 370, 300, 40)

        # 3
        self.title_BHM = QLabel("Black Hole Mass (M☉):", self)
        self.title_BHM.setFont(QFont("Helvetica", 14))
        self.title_BHM.setStyleSheet("color: white; background: transparent;")
        self.title_BHM.setGeometry(60, 570, 400, 40)

        # JETS YES/NO
        self.checkbox = QCheckBox(" Jets", self)
        self.checkbox.setFont(QFont("Helvetica", 15))
        self.checkbox.setStyleSheet("color: white; background: transparent;")
        self.checkbox.setGeometry(60, 780, 400, 40)
        self.checkbox.setChecked(True)
        self.scene.jets_enabled = True  # jets YES by default
        self.checkbox.stateChanged.connect(self.switch_jets)

    def submit1(self):
        value = float(self.input1.text())
        self.scene.star_radius = value
        print(f"Star Radius (R∗) is {self.input1.text()} R☉", value)

    def submit2(self):
        value = float(self.input2.text())
        self.scene.star_mass = value
        print(f"Star Mass (M∗) is {self.input2.text()} M☉", value)

    def submit3(self):
        value = float(self.input3.text())
        self.scene.tde.M_bh = value
        print(f"Black Hole Mass (Mʙʜ) is {self.input3.text()} M☉", value)

    def switch_jets(self, state):
        if state == Qt.Checked:
            self.scene.jets_enabled = True
            self.scene.generate_jets()
        else:
            self.scene.jets_enabled = False
            self.scene.remove_jets()
        self.scene.update()

    def open_database(self):
        import os
        import subprocess

        # to folders
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_file = os.path.join(current_dir, "database_tde.py")
        manual_file = os.path.join(current_dir, "database_manual.py")

        subprocess.Popen([sys.executable, db_file])
        subprocess.Popen([sys.executable, manual_file])


def main():

    app = QApplication(sys.argv)  
    scene = BlackHoleScene()
    window = MainWindow(scene)
    window.show()
    scene.show()                   
    sys.exit(app.exec_())          


if __name__ == "__main__":
    main()
