import atexit
import sys
import io
import time

from configparser import ConfigParser
from os import getcwd, path
from subprocess import Popen, PIPE

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

from instapy_bot.cli import client
from instapy_bot.gui.widgets.window import MainWindow


class Main(QMainWindow):
	state = {
		"folder"        : getcwd(),
		"timeout"       : "",
		"ig_user"       : "",
		"ig_pass"       : "",
		"text_caption"  : "",
		"reg_caption"   : "",
		"bnw_caption"   : "",
		"mail_use"      : False,
		"mail_mail"     : "",
		"mail_user"     : "",
		"mail_pass"     : "",
		"selected_photo": ""
	}

	def __init__(self, *args, **kwrags):
		super().__init__(*args, **kwrags)
		self.ui = MainWindow()
		self.setWindowTitle("InstaPy Bot")
		print("Created window", self)

		self.cfg = ConfigParser()
		self.cfg_path = path.join(getcwd(), "instapy-bot.conf")
		self.read_config(self.cfg, self.cfg_path)

		self.center()
		self.show()
		self.start()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.write_config()

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
		self.ui.setupUi(self)

		self.treeModel = QFileSystemModel()
		self.treeModel.setRootPath(QDir.rootPath())

		self.ui.treeView.setModel(self.treeModel)
		self.ui.treeView.setRootIndex(self.treeModel.index(getcwd()))

		# render selected image to screen
		self.ui.treeView.clicked.connect(self.render_image)

		# render config on start
		self.render_config()

		# change photos path on type
		self.ui.lineEdit_4.textChanged.connect(self.set_photos_path)

		self.ui.lineEdit.textChanged.connect(self.update_state)
		self.ui.lineEdit_2.textChanged.connect(self.update_state)
		self.ui.lineEdit_4.textChanged.connect(self.update_state)
		self.ui.lineEdit_3.textChanged.connect(self.update_state)
		self.ui.plainTextEdit_3.textChanged.connect(self.update_state)
		self.ui.plainTextEdit_2.textChanged.connect(self.update_state)
		self.ui.plainTextEdit.textChanged.connect(self.update_state)
		self.ui.lineEdit_7.textChanged.connect(self.update_state)
		self.ui.lineEdit_6.textChanged.connect(self.update_state)
		self.ui.lineEdit_5.textChanged.connect(self.update_state)

		self.ui.pushButton.clicked.connect(self.upload_photo)

		self.ui.checkBox.clicked.connect(self.set_mailer_usa)

	def set_mailer_usa(self):
		self.state["mail_use"] = self.ui.checkBox.isChecked()
		self.ui.lineEdit_7.setDisabled(not self.ui.checkBox.isChecked())
		self.ui.lineEdit_6.setDisabled(not self.ui.checkBox.isChecked())
		self.ui.lineEdit_5.setDisabled(not self.ui.checkBox.isChecked())
		print(self.state["mail_use"])

	def set_photos_path(self):
		text = self.ui.lineEdit_4.text()

		if path.exists(text) and path.isdir(text):
			self.state["folder"] = text
			self.ui.treeView.setRootIndex(self.treeModel.index(self.state["folder"]))

	def render_image(self):
		index = self.ui.treeView.selectedIndexes()[0]
		item = index.model()
		selected_photo = item.itemData(index)[0]
		pth = path.join(self.state["folder"], selected_photo)

		self.state["selected_photo"] = selected_photo

		image = QImage(pth)
		if image.isNull():
			QMessageBox.information(self, "Image Viewer", "Cannot load %s." % pth)
			self.state["selected_photo"] = ""
			return

		pic = QPixmap.fromImage(image).scaled(self.ui.label_4.width(), self.ui.label_4.height(),
		                                      QtCore.Qt.KeepAspectRatio)
		self.ui.label_4.setPixmap(pic)

	def upload_photo(self):
		from instapy_bot.bot.utils import is_bnw
		from instapy_bot.bot.mailer.mailer import Mailer

		self.ui.label_5.setText("")

		print(self.state["ig_user"])
		print(self.state["ig_pass"])
		print(self.state["selected_photo"])

		photo = self.state["selected_photo"]
		photo_path = path.join(self.state["folder"], photo)
		photo_caption = self.state["text_caption"] + " " + self.state["reg_caption"]
		if is_bnw(photo_path):
			photo_caption += " " + self.state["bnw_caption"]
		try:
			with client(self.state["ig_user"], self.state["ig_pass"]) as cli:
				cli.upload(photo_path, photo_caption)
			self.ui.label_5.setText("Photo uploaded successfully!")
			print("Photo uploaded successfully!")
			mailer = Mailer(self.state["mail_user"], self.state["mail_pass"], self.state["mail_mail"],
			                self.state["ig_user"])
			mailer.send_mail("Not scheduled", 0)
		except IOError as e:
			if "The password you entered is incorrect." in str(e):
				self.ui.label_5.setText("Password you entered is incorrect!")
				print("Password you entered is incorrect!")
			else:
				self.ui.label_5.setText(str(e))
				print(e)
		except Exception as e:
			self.ui.label_5.setText(str(e))

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

	def write_config(self):
		self.update_config()
		with open(self.cfg_path, "w") as configfile:
			self.cfg.write(configfile)

	def update_state(self):
		self.state["ig_user"] = self.ui.lineEdit.text()
		self.state["ig_pass"] = self.ui.lineEdit_2.text()
		self.state["folder"] = self.ui.lineEdit_4.text()
		self.state["timeout"] = self.ui.lineEdit_3.text()
		self.state["text_caption"] = self.ui.plainTextEdit_3.toPlainText()
		self.state["reg_caption"] = self.ui.plainTextEdit_2.toPlainText()
		self.state["bnw_caption"] = self.ui.plainTextEdit.toPlainText()
		self.state["mail_mail"] = self.ui.lineEdit_7.text()
		self.state["mail_user"] = self.ui.lineEdit_6.text()
		self.state["mail_pass"] = self.ui.lineEdit_5.text()

	def update_config(self):
		self.cfg["config"]["folder"] = self.state["folder"]
		self.cfg["config"]["timeout"] = self.state["timeout"]
		self.cfg["credentials"]["username"] = self.state["ig_user"]
		self.cfg["credentials"]["password"] = self.state["ig_pass"]
		self.cfg["caption"]["text"] = self.state["text_caption"]
		self.cfg["caption"]["reg"] = self.state["reg_caption"]
		self.cfg["caption"]["bnw"] = self.state["bnw_caption"]
		self.cfg["mailer"]["to"] = self.state["mail_mail"]
		self.cfg["mailer"]["username"] = self.state["mail_user"]
		self.cfg["mailer"]["password"] = self.state["mail_pass"]

	def read_config(self, cfg, cfg_path):
		if path.exists(cfg_path):
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


if __name__ == "__main__":
	app = QApplication(sys.argv)
	with Main() as main:
		pass
	sys.exit(app.exec_())
