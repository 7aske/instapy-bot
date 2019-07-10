import atexit
import sys
import time

from configparser import ConfigParser
from datetime import timedelta
from os import getcwd, path, listdir, rename

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

from instapy_bot.bot.utils import PhotoStack, get_timeout
from instapy_bot.bot.utils.photo import Photo
from instapy_bot.cli import client
from instapy_bot.gui.widgets.window import MainWindow


class Main(QMainWindow):
	def __init__(self, *args, **kwrags):
		super().__init__(*args, **kwrags)
		self.state = {
			"folder"        : getcwd(),
			"timeout"       : "",
			"ig_user"       : "",
			"ig_pass"       : "",
			"captions"      : {},
			"text_caption"  : "",
			"reg_caption"   : "",
			"bnw_caption"   : "",
			"mail_use"      : False,
			"mail_mail"     : "",
			"mail_user"     : "",
			"mail_pass"     : "",
			"selected_photo": ""
		}
		self.upload_thread = None
		self.dt_format = "%Y/%d/%m %H:%M:%S"
		self.next_upload = str(path.join(getcwd(), "nextupload"))
		self.photos = PhotoStack()
		self.ui = MainWindow()
		self.setWindowTitle("InstaPy Bot")
		print("Created window", self)

		self.cfg = ConfigParser()
		self.cfg_captions = ConfigParser()

		self.cfg_path = path.join(getcwd(), "instapy-bot.conf")
		self.cfg_caption_path = path.join(getcwd(), "instapy-bot_captions.conf")

		if not path.exists(self.cfg_path):
			self.generate_config(self.cfg, self.cfg_path)

		if not path.exists(self.cfg_caption_path):
			with open(self.cfg_caption_path, "w") as file:
				file.write("")

		self.read_config(self.cfg, self.cfg_path)
		self.read_caption_config(self.cfg_captions, self.cfg_caption_path)

		self.center()
		self.show()
		self.start()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		pass

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
		self.ui.treeView.clicked.connect(self.select_photo)

		# render config on start
		self.render_config()

		# change photos path on type
		self.ui.lineEdit_4.textChanged.connect(self.set_photos_path)

		self.ui.radioButton_2.clicked.connect(self.caption_change)
		self.ui.radioButton.clicked.connect(self.caption_change)

		self.ui.lineEdit.textChanged.connect(self.update_state)
		self.ui.lineEdit_2.textChanged.connect(self.update_state)
		self.ui.lineEdit_4.textChanged.connect(self.update_state)
		self.ui.lineEdit_3.textChanged.connect(self.update_state)

		self.ui.plainTextEdit_3.textChanged.connect(self.update_specific_caption)
		self.ui.plainTextEdit_2.textChanged.connect(self.update_specific_caption)
		self.ui.plainTextEdit.textChanged.connect(self.update_specific_caption)

		self.ui.lineEdit_7.textChanged.connect(self.update_state)
		self.ui.lineEdit_6.textChanged.connect(self.update_state)
		self.ui.lineEdit_5.textChanged.connect(self.update_state)

		self.ui.pushButton.clicked.connect(self.threaded_upload_photo)
		self.ui.pushButton_2.clicked.connect(self.threaded_upload_loop)
		self.ui.pushButton_3.clicked.connect(self.stop_threaded_upload)

		self.ui.checkBox.clicked.connect(self.set_mailer_use)

	def set_mailer_use(self):
		self.state["mail_use"] = self.ui.checkBox.isChecked()
		self.ui.lineEdit_7.setDisabled(not self.ui.checkBox.isChecked())
		self.ui.lineEdit_6.setDisabled(not self.ui.checkBox.isChecked())
		self.ui.lineEdit_5.setDisabled(not self.ui.checkBox.isChecked())

	def set_photos_path(self):
		text = self.ui.lineEdit_4.text()

		if path.exists(text) and path.isdir(text):
			self.state["folder"] = text
			self.ui.treeView.setRootIndex(self.treeModel.index(text))

	def select_photo(self):
		index = self.ui.treeView.selectedIndexes()[0]
		item = index.model()
		selected_photo = item.itemData(index)[0]

		self.state["selected_photo"] = selected_photo
		self.render_image()

	def render_image(self):
		selected_photo = self.state["selected_photo"]
		pth = path.join(self.state["folder"], selected_photo)
		if selected_photo in self.state["captions"].keys():
			self.ui.radioButton.click()
		else:
			self.ui.radioButton_2.click()

		image = QImage(pth)
		if image.isNull():
			QMessageBox.information(self, "Image Viewer", "Cannot load %s." % pth)
			self.state["selected_photo"] = ""
			return

		pic = QPixmap.fromImage(image).scaled(self.ui.label_4.width(), self.ui.label_4.height(),
		                                      QtCore.Qt.KeepAspectRatio)
		self.ui.label_4.setPixmap(pic)

	def threaded_upload_photo(self):
		import threading
		self.upload_thread = threading.Thread(target=self.upload_photo)
		self.upload_thread.setDaemon(True)
		self.upload_thread.start()

	def upload_photo(self):
		from instapy_bot.bot.utils import is_bnw
		from datetime import datetime as dt

		self.write_out("")

		photo = self.state["selected_photo"]
		photo_path = path.join(self.state["folder"], photo)
		photo_caption = self.state["text_caption"] + " " + self.state["reg_caption"]
		if is_bnw(photo_path):
			photo_caption += " " + self.state["bnw_caption"]
		try:
			with client(self.state["ig_user"], self.state["ig_pass"]) as cli:
				cli.upload(photo_path, photo_caption)

			self.write_out("Photo uploaded successfully!")
			print("Photo uploaded successfully!")
			rename(photo_path, photo_path + ".UPLOADED")
			s = get_timeout(int(self.state["timeout"]))
			n = dt.now() + timedelta(seconds=s)
			with open(self.next_upload, "w") as nextupload:
				nextupload.write(n.strftime(self.dt_format))
			if self.state["mail_use"]:
				try:
					from instapy_bot.bot.mailer.mailer import Mailer
					mailer = Mailer(self.state["mail_user"], self.state["mail_pass"],
					                self.state["mail_mail"],
					                self.state["ig_user"])
					mailer.send_mail(n.strftime(self.dt_format), len(self.photos))
					self.write_out("Mail sent")
				except IOError:
					self.write_out("Unable to send mail")
			self.write_out("Next upload - %s" % n.strftime(self.dt_format))
			time.sleep(s)

		except IOError as e:
			if "The password you entered is incorrect." in str(e):
				self.write_out("Password you entered is incorrect!")
				print("Password you entered is incorrect!")

			else:
				self.write_out(str(e))
				print(e)
		except Exception as e:
			self.ui.label_5.setText(str(e))

	def read_caption_config(self, cfg, cfg_path):
		if path.exists(cfg_path):
			cfg.read(cfg_path)
			for key in cfg.keys():
				if key != "DEFAULT":
					self.state["captions"][key] = {
						"text": cfg[key]["text"],
						"reg" : cfg[key]["reg"],
						"bnw" : cfg[key]["bnw"],
					}

	def update_captions_config(self):
		for key in self.state["captions"]:
			self.cfg_captions[key] = self.state["captions"][key]

	def write_caption_config(self):
		self.update_captions_config()
		with open(self.cfg_caption_path, "w") as configfile:
			self.cfg_captions.write(configfile)

	def update_photos(self):
		for photo in listdir(self.state["folder"]):
			name, ext = path.splitext(photo)
			if ext.upper() == ".JPG" or ext.upper() == ".PNG" or ext.upper() == ".JPEG":
				photo_object = Photo(path.join(self.state["folder"], photo))
				self.photos.push(photo_object)
		if len(self.photos) == 0:
			self.write_out("Done")

	def stop_threaded_upload(self):
		if self.upload_thread is not None:
			self.write_out("Stopped")
			self.upload_thread = None

	def threaded_upload_loop(self):
		import threading
		self.upload_thread = threading.Thread(target=self.upload_loop)
		self.upload_thread.setDaemon(True)
		self.upload_thread.start()

	def upload_loop(self):
		from instapy_bot.bot.errors import ServerError
		from instapy_bot.bot.errors import WrongPassword
		from datetime import datetime as dt
		while True:
			self.write_out("Photos - %d" % len(self.photos))
			if len(self.photos) == 0:
				self.update_photos()
				s = min(3600, int(self.state["timeout"]))
				n = dt.now() + timedelta(seconds=s)
				self.write_out("Next refresh - %s" % n.strftime(self.dt_format))
				time.sleep(s)
			else:
				date = dt.now()
				newdate = dt.now()
				if path.exists(self.next_upload):
					with open(self.next_upload, "r") as nextupload:
						content = nextupload.read()
						date = dt.strptime(content, self.dt_format)
				if newdate >= date:
					if 1 < newdate.hour < 9 and self.state["bedtime"]:
						self.write_out("Bed time, skipping upload")
						time.sleep(get_timeout((10 - newdate.hour) * 3600))
					else:
						try:
							self.state["selected_photo"] = path.basename(self.photos.pop().path)
							self.render_image()
							self.upload_photo()
						except WrongPassword as e:
							self.write_out(str(e))
							return
						except ServerError as e:
							self.write_out(str(e))
							return
				else:
					newdate = date - dt.now()
					self.write_out("Waiting for scheduled upload")
					self.write_out("Next upload - %s" % date.strftime(self.dt_format))
					time.sleep(newdate.seconds + 1)

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

	def caption_change(self):
		self.ui.plainTextEdit_3.textChanged.disconnect(self.update_specific_caption)
		self.ui.plainTextEdit_2.textChanged.disconnect(self.update_specific_caption)
		self.ui.plainTextEdit.textChanged.disconnect(self.update_specific_caption)

		if self.ui.radioButton_2.isChecked():
			self.ui.plainTextEdit_3.setPlainText(self.state["text_caption"])
			self.ui.plainTextEdit_2.setPlainText(self.state["reg_caption"])
			self.ui.plainTextEdit.setPlainText(self.state["bnw_caption"])

		elif self.ui.radioButton.isChecked():
			if self.state["selected_photo"] != "":
				if self.state["selected_photo"] in self.state["captions"].keys():
					self.ui.plainTextEdit_3.setPlainText(self.state["captions"][self.state["selected_photo"]]["text"])
					self.ui.plainTextEdit_2.setPlainText(self.state["captions"][self.state["selected_photo"]]["reg"])
					self.ui.plainTextEdit.setPlainText(self.state["captions"][self.state["selected_photo"]]["bnw"])

				else:
					self.state["captions"][self.state["selected_photo"]] = {
						"text": self.state["text_caption"],
						"reg" : self.state["reg_caption"],
						"bnw" : self.state["bnw_caption"],
					}

			else:
				self.ui.plainTextEdit_3.setPlainText(self.state["text_caption"])
				self.ui.plainTextEdit_2.setPlainText(self.state["reg_caption"])
				self.ui.plainTextEdit.setPlainText(self.state["bnw_caption"])

		self.ui.plainTextEdit_3.textChanged.connect(self.update_specific_caption)
		self.ui.plainTextEdit_2.textChanged.connect(self.update_specific_caption)
		self.ui.plainTextEdit.textChanged.connect(self.update_specific_caption)

	def update_specific_caption(self):
		if self.ui.radioButton_2.isChecked():
			self.state["text_caption"] = self.ui.plainTextEdit_3.toPlainText()
			self.state["reg_caption"] = self.ui.plainTextEdit_2.toPlainText()
			self.state["bnw_caption"] = self.ui.plainTextEdit.toPlainText()

		elif self.state["selected_photo"] != "":
			self.state["captions"][self.state["selected_photo"]] = {
				"text": self.ui.plainTextEdit_3.toPlainText(),
				"reg" : self.ui.plainTextEdit_2.toPlainText(),
				"bnw" : self.ui.plainTextEdit.toPlainText(),
			}

	def update_state(self):
		self.state["ig_user"] = self.ui.lineEdit.text()
		self.state["ig_pass"] = self.ui.lineEdit_2.text()
		self.state["folder"] = self.ui.lineEdit_4.text()
		self.state["timeout"] = self.ui.lineEdit_3.text()
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

	def generate_config(self, cfg, cfg_path: str):
		cfg["credentials"] = {
			"username": "instagram_username",
			"password": "instagram_password",
		}
		cfg["config"] = {
			"timeout": "10",
			"folder" : path.join(getcwd(), "photos")
		}
		cfg["mailer"] = {
			"to"      : "mail_to@example.com",
			"username": "mailer_username",
			"password": "mailer_password",
		}
		cfg["caption"] = {
			"text": "Photo of the day",
			"reg" : "candid nature photooftheday",
			"bnw" : "bnw blackandwhite",
		}
		with open(cfg_path, "w") as configfile:
			cfg.write(configfile)

	def write_out(self, text: str):
		self.ui.label_5.setText(text)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	main = Main()


	@atexit.register
	def write_config():
		if main is not None:
			main.write_config()
			main.write_caption_config()
			main.stop_threaded_upload()


	sys.exit(app.exec_())
