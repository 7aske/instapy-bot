import sys
from subprocess import Popen, PIPE
from PyQt5.QtWidgets import QApplication

from instapy_bot.gui.window.MainWindow import MainWindow

app = QApplication(sys.argv)
window = MainWindow()

# gs = Popen(["echo", "testssss"], stderr=PIPE, stdout=PIPE).stdout.read()
sys.exit(app.exec_())
