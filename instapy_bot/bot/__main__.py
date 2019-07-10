#!/usr/bin/python3
import getpass
from os import getcwd, listdir, remove
from os.path import exists, join, isabs, splitext
from platform import python_version
from sys import argv, platform
import configparser
from time import sleep
from datetime import datetime as dt, timedelta

from instapy_bot.cli import client
from instapy_bot.bot.utils import is_bnw, get_timeout, validate_mail, PhotoStack
from instapy_bot.bot.errors import ServerError, WrongPassword
from instapy_bot.bot.logger.logger import Logger
from instapy_bot.bot.mailer.mailer import Mailer
from instapy_bot.bot.utils.photo import Photo

version = "0.1.2"
author = "Nikola Tasic"
repo = "https://github.com/7aske/instapy-bot"
version_line = "window {}({}) | {} | {}".format(version, python_version(), author, repo)
config = configparser.ConfigParser()
config_path = join(getcwd(), "window.conf")
username = ""
password = ""
folder = "photos"
logger = Logger("window.log")
next_upload = join(getcwd(), "nextupload")
# START#FLAGS#####
watch = False
bedtime = False
mail = False
# END###FLAGS#####
# MAIL#CONFIG#####
mailer = None
mail_username = ""
mail_password = ""
mail_to = ""
# MAIL#CONFIG#END#
timeout = 4320
dt_format = "%Y/%d/%m %H:%M:%S"
photos = PhotoStack()
reg_caption = ""
bnw_caption = ""
text_caption = ""


def main():
	global watch, bedtime, config, config_path, logger, username, \
		password, timeout, mail_to, mail_password, mail_username, mail, mailer

	if "--help" in argv or "-h" in argv or "-help" in argv:
		print_help()
		raise SystemExit
	elif "--config" in argv or "-C" in argv:
		generate_config(config, config_path)
		raise SystemExit

	print(version_line)
	if "--log" not in argv and "-l" not in argv:
		logger.set_out(False)
		logger.log("Logging   - off")
	update_config(config, config_path)
	if "--watch" in argv or "-w" in argv:
		watch = True
		logger.log("Watch mode - on")
	if "--bedtime" in argv or "-b" in argv:
		logger.log("No bedtime - on")
		bedtime = True

	try:
		photos_dir = ""
		if "-c" in argv:
			path = argv[argv.index("-c") + 1]
			config_path = path if isabs(path) else join(getcwd(), path)
		else:
			config_path = join(getcwd(), "window.conf")
		if "-f" in argv:
			path = argv[argv.index("-f") + 1]
			photos_dir = path if isabs(path) else join(getcwd(), path)
		elif "config" in config:
			if "folder" in config["config"]:
				path = config["config"]["folder"]
				photos_dir = path if isabs(path) else join(getcwd(), path)
		else:
			print("Current dir: '{}'".format(getcwd()))
			path = input("Photos folder: ")
			photos_dir = join(getcwd(), path)
		if "-t" in argv:
			try:
				timeout = int(argv[argv.index("-t") + 1])
			except ValueError:
				timeout = 43200
		elif "config" in config:
			if "timeout" in config["config"]:
				timeout = int(config["config"]["timeout"])
		else:
			userinput = input("Timeout (default=43000): ")
			if userinput == "":
				timeout = 43200
			else:
				try:
					timeout = int(userinput)
				except ValueError:
					logger.log("Invalid timeout")

		config["config"] = {
			"timeout": timeout,
			"folder": photos_dir
		}

	except Exception:
		print_help()
		raise SystemExit

	if not exists(photos_dir):
		logger.log("Photos directory doesn't exist\n%s" % photos_dir)
		raise SystemExit
	with open(config_path, "w") as configfile:
		config.write(configfile)

	mail = validate_mail(config)
	if mail:
		mail_username = config["mailer"]["username"]
		mail_password = config["mailer"]["password"]
		mail_to = config["mailer"]["to"]
		mailer = Mailer(mail_username, mail_password, mail_to, username)
	answer = ""
	if "-y" not in argv and "--yes" not in argv:
		while answer.upper() not in ["Y", "N"]:
			print("Start uploading from '%s'" % photos_dir, end="")
			print(" with timeout of '%d'" % timeout)
			answer = input("Are you sure? (Y/N) ")
	else:
		answer = "y"
	if answer.upper() == "Y":
		update_photos()
		try:
			while True:
				logger.log("Photos - %d" % len(photos))
				update_tags()
				if len(photos) == 0:
					update_photos()
					s = min(3600, timeout)
					n = dt.now() + timedelta(seconds=s)
					logger.log("Next refresh - %s" % n.strftime(dt_format))
					sleep(s)
				else:
					date = dt.now()
					newdate = dt.now()
					if exists(next_upload):
						with open(next_upload, "r") as nextupload:
							content = nextupload.read()
							date = dt.strptime(content, dt_format)
					if newdate >= date:
						if 1 < newdate.hour < 9 and bedtime:
							logger.log("Bed time, skipping upload")
							sleep(get_timeout((10 - newdate.hour) * 3600))
						else:
							try:
								upload_photo()
							except WrongPassword as e:
								logger.log(str(e))
								raise SystemExit
							except ServerError as e:
								logger.log(str(e))
								raise SystemExit
							s = get_timeout(timeout)
							n = dt.now() + timedelta(seconds=s)
							with open(next_upload, "w") as nextupload:
								nextupload.write(n.strftime(dt_format))
							if mail:
								try:
									mailer.send_mail(n.strftime(dt_format), len(photos))
									logger.log("Mail sent")
								except IOError:
									logger.log("Unable to send mail")
							logger.log("Next upload - %s" % n.strftime(dt_format))
							sleep(s)
					else:
						newdate = date - dt.now()
						logger.log("Waiting for scheduled upload")
						logger.log("Next upload - %s" % date.strftime(dt_format))
						sleep(newdate.seconds + 1)
		except KeyboardInterrupt:
			logger.log("\r**************************")
	else:
		raise SystemExit


def update_config(cfg, cfg_path):
	global username, password, reg_caption, bnw_caption, logger, text_caption
	if exists(cfg_path):
		cfg.read(cfg_path)
		if "credentials" not in cfg:
			logger.log("Bad config file")
			raise SystemExit
		else:
			if "username" not in cfg["credentials"] or "password" not in cfg["credentials"]:
				logger.log("Bad config file")
				raise SystemExit

		username = cfg["credentials"]["username"]
		password = cfg["credentials"]["password"]
		if username == "":
			username = input("Username: ")
		print("Account  - '%s'" % username)
		if password == "":
			if platform == "win32":
				password = getpass.win_getpass("Password: ")
			else:
				password = getpass.getpass("Password: ")
		print("Password - '%s'" % "".join(["*" for _ in password]))
		if "caption" in cfg:
			if "text" in cfg["caption"]:
				text_caption = cfg["caption"]["text"]
			if "bnw" in cfg["caption"]:
				bnw_caption = " ".join(["#" + tag for tag in cfg["caption"]["bnw"].split(" ")])
			if "reg" in cfg["caption"]:
				reg_caption = " ".join(["#" + tag for tag in cfg["caption"]["reg"].split(" ")])
			logger.log("Updated tags from config file")
	else:
		username = input("Username: ")
		password = getpass.getpass()
		cfg["credentials"] = {
			"username": username,
			"password": password
		}
		with open(cfg_path, "w") as configfile:
			cfg.write(configfile)


def upload_photo():
	global logger, bedtime, photos, reg_caption, bnw_caption, username, password
	photo = photos.pop()
	caption = ""
	if len(photo.caption) == 0:
		if len(text_caption) > 0:
			caption += text_caption
		if len(reg_caption) > 0:
			caption += "\n" + reg_caption
		if len(bnw_caption) > 0:
			if is_bnw(photo.path):
				caption += "\n\n" + bnw_caption
		photo.set_caption(caption)
	try:
		with client(username, password) as cli:
			logger.log(str(photo))
			cli.upload(photo.path, photo.caption)
		remove(photo.path)
	except IOError as e:
		if "The password you entered is incorrect." in str(e):
			config["credentials"]["password"] = ""
			with open(config_path, "w") as configfile:
				config.write(configfile)
			raise WrongPassword("Password you entered is incorrect")
		else:
			photos.push(photo)
			logger.log("Retrying photo upload in 60 seconds")
			sleep(60)
			upload_photo()
	except Exception as e:
		raise ServerError(e)


def update_photos():
	global watch, logger, folder, photos
	for photo in listdir(folder):
		name, ext = splitext(photo)
		if ext.upper() == ".JPG":
			caption_file = join(folder, name + ".txt")
			photo_object = Photo(join(folder, photo))
			if exists(caption_file):
				f = open(caption_file, "r")
				photo_object.set_caption(f.read())
			photos.push(photo_object)
	if len(photos) == 0:
		if not watch:
			logger.log("Folder Empty")
			raise SystemExit


def update_tags():
	global bnw_caption, reg_caption
	bnw_path = join(getcwd(), "bnw_tags.txt")
	regular_path = join(getcwd(), "regular_tags.txt")
	if exists(bnw_path):
		with open(bnw_path, "r") as bnw:
			bnw_caption = ""
			for line in bnw.readlines():
				bnw_caption += line
	if exists(regular_path):
		with open(regular_path, "r") as regular:
			regular_caption = ""
			for line in regular.readlines():
				regular_caption += line


def generate_config(cfg, cfg_path:str):
	cfg["credentials"] = {
		"username": "instagram_username",
		"password": "instagram_password",
	}
	cfg["config"] = {
		"timeout": "10",
		"folder": join(getcwd(), "photos")
	}
	cfg["mailer"] = {
		"to": "mail_to@example.com",
		"username": "mailer_username",
		"password": "mailer_password",
	}
	cfg["caption"] = {
		"text": "Photo of the day",
		"reg": "candid nature photooftheday",
		"bnw": "bnw blackandwhite",
	}
	with open(cfg_path, "w") as configfile:
		cfg.write(configfile)


def print_help():
	print(version_line)
	print("usage: window [option] [flags]")
	print("options:")
	print("{:16}{:24}".format("\t-c path", "path to window.conf config file"))
	print("{:16}{:24}".format("\t-f path", "path to photos folder"))
	print("{:16}{:24}".format("\t-t time", "timeout between uploads in seconds"))
	print("flags:")
	print("{:16}{:24}".format("\t--yes     -y", "skip confirmation"))
	print("{:16}{:24}".format("\t--log     -l", "enable logging to file"))
	print("{:16}{:24}".format("\t--watch   -w", "watch the folder for new photos"))
	print("{:16}{:24}".format("\t--bedtime -b", "don't upload photos during nighttime"))
	print("{:16}{:24}".format("\t--config  -C", "generate config file in the current directory and exit"))
	print("{:16}{:24}".format("\t--help    -h", "print this message and exit"))
	print("""sample config file:
	[credentials]
	username = instagram_username
	password = instagram_password
	[config]
	timeout = 10
	folder = /path/to/the/folder
	[mailer]
	to = mail_to
	username = mailer_username
	password = mailer_password
	[caption]
	text = Text based caption
	reg = nature candid photooftheday
	bnw = bnw blackandwhite""")


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\nKeyboardInterrupt")
		raise SystemExit
