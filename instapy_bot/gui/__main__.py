import sys

from PyQt5.QtWidgets import QApplication

from instapy_bot.gui.start import Main

app = QApplication(sys.argv)

main = Main()

sys.exit(app.exec_())
