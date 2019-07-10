from configparser import ConfigParser
from os import getcwd
from os.path import exists, isdir, join

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox

from instapy_bot.gui.widgets.window import MainWindow


class Main(QMainWindow):
	state = {
		"folder"      : getcwd(),
		"timeout"     : "",
		"ig_user"     : "",
		"ig_pass"     : "",
		"text_caption": "",
		"reg_caption" : "",
		"bnw_caption" : "",
		"mail_mail"   : "",
		"mail_user"   : "",
		"mail_pass"   : "",
	}
	cfg_path = join(getcwd(), "instapy-bot.conf")
	cfg = ConfigParser()

	def __init__(self, *args, **kwrags):
		super().__init__(*args, **kwrags)
		self.setWindowTitle("InstaPy Bot")
		print("Created window", self)
		self.center()
		self.show()
		self.start()

	def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
		if e.key() == Qt.Key_Escape:
			self.close()

	def center(self) -> None:
		from PyQt5.QtWidgets import QDesktopWidget
		center = QDesktopWidget().availableGeometry().center()
		center.setX(int(center.x() - self.width() / 2))
		center.setY(int(center.y() - self.height() / 2))
		self.move(center)

	def start(self):
		from PyQt5.QtWidgets import QFileSystemModel
		from PyQt5.QtCore import QDir
		self.ui = MainWindow()
		self.ui.setupUi(self)

		self.treeModel = QFileSystemModel()
		self.treeModel.setRootPath(QDir.rootPath())

		self.ui.treeView.setModel(self.treeModel)
		self.ui.treeView.setRootIndex(self.treeModel.index(getcwd()))

		self.ui.treeView.clicked.connect(self.render_image)

		self.update_config(self.cfg, self.cfg_path)
		self.render_config()

		self.ui.lineEdit_4.textChanged.connect(self.set_photos_path)

	def set_photos_path(self):
		text = self.ui.lineEdit_4.text()

		if exists(text) and isdir(text):
			self.state["folder"] = text
			self.ui.treeView.setRootIndex(self.treeModel.index(self.state["folder"]))

	def render_image(self):
		index = self.ui.treeView.selectedIndexes()[0]
		item = index.model()
		label = QLabel(self)
		path = join(self.state["folder"], item.itemData(index)[0])
		print(path)
		image = QImage(path)
		if image.isNull():
			QMessageBox.information(self, "Image Viewer", "Cannot load %s." % path)
			return
		pic = QPixmap.fromImage(image).scaled(self.ui.label_4.width(), self.ui.label_4.height(), QtCore.Qt.KeepAspectRatio)
		self.ui.label_4.setPixmap(pic)
		# label.resize(pic.width(), pic.height())
		# label.show()
		# TODO: render image
		pass

	def render_config(self):

		self.ui.lineEdit.setText(self.state["ig_user"])
		self.ui.lineEdit_2.setText(self.state["ig_pass"])

		self.ui.plainTextEdit_3.setPlainText(self.state["text_caption"])
		self.ui.plainTextEdit_2.setPlainText(self.state["reg_caption"])
		self.ui.plainTextEdit.setPlainText(self.state["bnw_caption"])

		self.ui.lineEdit_7.setText(self.state["mail_mail"])
		self.ui.lineEdit_6.setText(self.state["mail_user"])
		self.ui.lineEdit_5.setText(self.state["mail_pass"])

		self.ui.lineEdit_4.setText(self.state["folder"])
		self.ui.lineEdit_3.setText(self.state["timeout"])

		if self.state["mail_mail"] != "" and self.state["mail_user"] != "" and self.state["mail_pass"] != "":
			self.ui.checkBox.setChecked(True)
		else:
			self.ui.checkBox.setChecked(False)

		self.set_photos_path()

	def update_config(self, cfg, cfg_path):
		if exists(cfg_path):
			cfg.read(cfg_path)

			if "credentials" in cfg:
				if "username" in cfg["credentials"]:
					self.state["ig_user"] = cfg["credentials"]["username"]
				if "password" in cfg["credentials"]:
					self.state["ig_pass"] = cfg["credentials"]["password"]

			if "config" in cfg:
				if "folder" in cfg["config"]:
					self.state["folder"] = cfg["config"]["folder"]

				if "timeout" in cfg["config"]:
					self.state["timeout"] = cfg["config"]["timeout"]

			self.state["text_caption"] = ""
			self.state["reg_caption"] = ""
			self.state["bnw_caption"] = ""

			if "caption" in cfg:
				if "text" in cfg["caption"]:
					self.state["text_caption"] += cfg["caption"]["text"]
				if "bnw" in cfg["caption"]:
					for tag in cfg["caption"]["bnw"].split(" "):
						if tag.startswith("#"):
							self.state["bnw_caption"] += tag + " "
						else:
							self.state["bnw_caption"] += "#" + tag + " "
				if "reg" in cfg["caption"]:
					for tag in cfg["caption"]["reg"].split(" "):
						if tag.startswith("#"):
							self.state["reg_caption"] += tag + " "
						else:
							self.state["reg_caption"] += "#" + tag + " "

			if "mailer" in cfg:
				if "to" in cfg["mailer"] and "username" in cfg["mailer"] and "password" in cfg["mailer"]:
					self.state["mail_mail"] = cfg["mailer"]["to"]
					self.state["mail_user"] = cfg["mailer"]["username"]
					self.state["mail_pass"] = cfg["mailer"]["password"]
				else:
					self.state["mail_mail"] = ""
					self.state["mail_user"] = ""
					self.state["mail_pass"] = ""
			else:
				self.state["mail_mail"] = ""
				self.state["mail_user"] = ""
				self.state["mail_pass"] = ""
