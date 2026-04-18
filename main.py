from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

import sys
import os

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

