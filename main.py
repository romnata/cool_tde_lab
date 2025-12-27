# initializes the PyQt5 application

import sys
from PyQt5.QtWidgets import QApplication
from black_hole import BlackHoleScene


def main():

    app = QApplication(sys.argv)  
    scene = BlackHoleScene()      
    scene.show()                   
    sys.exit(app.exec_())          


if __name__ == "__main__":
    main()
