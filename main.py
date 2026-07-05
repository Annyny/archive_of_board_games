import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from ui_main import MainWindow

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())