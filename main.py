import sys
from PyQt5.QtWidgets import QApplication
from widgets.main_window import MainWindow
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.setFixedSize(300,150)
    sys.exit(app.exec_())

    