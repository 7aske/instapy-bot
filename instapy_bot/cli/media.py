import requests
from PIL import Image
from os import path, remove
from os.path import join

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

MIN_ASPECT_RATIO = 0.80
MAX_ASPECT_RATIO = 1.91


class Media(object):
    image_path = None
    valid_image = None
    media = None

    def __init__(self, file):
        self.media = file
        if urlparse(file).scheme in ("http", "https"):
            self.image_path = self.download_media(file)
        else:
            self.image_path = file

        original_image_object = Image.open(self.image_path)
        print("Fixing aspect ratio if not according to accepted dimensions")
        print("Generating and saving valid image")
        new_object = self.fix_aspect_ratio(original_image_object)

        filename, ext = path.splitext(path.basename(self.image_path))
        valid_image_path = join(path.dirname(self.image_path), filename + "_valid" + ext)

        new_object.save(valid_image_path, "JPEG", quality=50, optimize=True)

        self.valid_image = valid_image_path

    def get_path(self):
        return self.valid_image

    @staticmethod
    def fix_aspect_ratio(original_img):
        width, height = original_img.size
        aspect_ratio = width / height
        size = (2048, 2048)
        if aspect_ratio < MIN_ASPECT_RATIO:
            blank = Image.new("RGB", (height, height), color=(255, 255, 255))
            new_img = blank.copy()
            pos = (int((height - width) / 2), 0)
            new_img.paste(original_img, pos)
            new_img = new_img.resize(size, Image.ANTIALIAS)
            blank.close()
            return new_img
        elif aspect_ratio > MAX_ASPECT_RATIO:
            blank = Image.new("RGB", (width, width), color=(255, 255, 255))
            new_img = blank.copy()
            pos = (0, int((width - height) / 2))
            new_img.paste(original_img, pos)
            new_img = new_img.resize(size, Image.ANTIALIAS)
            blank.close()
            return new_img
        else:
            scale = max(width, height) / 2048
            original_img = original_img.resize((int(width / scale), int(height / scale)))
            return original_img

    @staticmethod
    def download_media(url):
        print("Downloading Media..")
        file_name = urlparse(url).path.split("/")[-1]
        r = requests.get(url, allow_redirects=True)
        open(file_name, "wb").write(r.content)
        return file_name

    def remove_media(self):
        pass
        remove(self.valid_image)
