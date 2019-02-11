from os.path import isabs
from random import choice, randrange
from PIL import Image


def get_timeout(timeout):
    offset = choice([-1, 1]) * randrange(int(timeout / 20), int(timeout / 10) + 1)
    return timeout + offset


def is_bnw(path):
    img = Image.open(path)
    w, h = img.size
    pix = {"B": 0, "C": 0, "T": 0}
    for i in range(int(w / 4)):
        for j in range(int(h / 4)):
            r, g, b = img.getpixel((i * 4, j * 4))
            if r != g != b:
                pix["C"] += 1
            else:
                pix["B"] += 1
            pix["T"] += 1
    try:
        out = pix["C"] / pix["T"]
        return out < 0.2
    except ZeroDivisionError:
        out = 0
        return out < 0.2
    finally:
        img.close()


def validate_mail(config):
    if "mailer" in config:
        if "to" in config["mailer"] and "username" in config["mailer"] and "password" in \
                config["mailer"]:
            return True
    return False


class PhotoStack:
    def __init__(self):
        self.photos = []

    def __repr__(self):
        return str([str(photo) for photo in self.photos])

    def __len__(self):
        return len(self.photos)

    def push(self, item):
        from instapy_bot.bot.utils.photo import Photo
        if isinstance(item, Photo):
            self.photos.append(item)
        elif isabs(item):
            self.photos.append(Photo(item))

    def pop(self):
        return self.photos.pop()

    def is_empty(self):
        return self.photos == []


class WrongPassword(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        print("Wrong password")


class ServerError(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        print("Server Error")
