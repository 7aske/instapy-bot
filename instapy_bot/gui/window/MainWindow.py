from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow

from instapy_bot.gui.widgets.ConfigWidget import ConfigWidget


class MainWindow(QMainWindow):
	def __init__(self, *args, **kwrags):
		super().__init__(*args, **kwrags)
		self.setWindowTitle("InstaPy Bot")

		self.setGeometry(0, 0, 640, 400)

		self.config_widget = ConfigWidget()
		self.setCentralWidget(self.config_widget)

		self.center()
		self.show()
		print("Created window", self)

	def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
		if e.key() == Qt.Key_Escape:
			self.close()

	def center(self):
		center = QDesktopWidget().availableGeometry().center()
		center.setX(int(center.x() - self.width() / 2))
		center.setY(int(center.y() - self.height() / 2))
		self.move(center)
