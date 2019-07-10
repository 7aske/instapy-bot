from random import choice, randrange
from PIL import Image

from instapy_bot.bot.utils.photostack import PhotoStack

def get_timeout(timeout):
	offset = choice([-1, 1]) * randrange(int(timeout / 20), int(timeout / 10) + 1)
	return timeout + offset


def is_bnw(path):
	img = Image.open(path)
	w, h = img.size
	pixels = {"B": 0, "C": 0, "T": 0}
	for i in range(int(w / 4)):
		for j in range(int(h / 4)):
			pixel = img.getpixel((i * 4, j * 4))
			if pixel[0] != pixel[1] != pixel[0]:
				pixels["C"] += 1
			else:
				pixels["B"] += 1
			pixels["T"] += 1
	try:
		out = pixels["C"] / pixels["T"]
		return out < 0.2
	except ZeroDivisionError:
		out = 0
		return out < 0.2
	finally:
		img.close()


def validate_mail(config):
	if "mailer" in config:
		return "to" in config["mailer"] and "username" in config["mailer"] and "password" in \
		       config["mailer"]


