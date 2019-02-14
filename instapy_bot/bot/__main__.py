import getpass
from os import getcwd, listdir, remove
from os.path import exists, join, isabs, splitext
from platform import python_version
from sys import argv
import configparser
from time import sleep
from datetime import datetime as dt, timedelta

from instapy_bot.cli import client
import pkg_resources
from instapy_bot.bot.utils import is_bnw, get_timeout, validate_mail, PhotoStack, ServerError, WrongPassword
from instapy_bot.bot.logger.logger import Logger
from instapy_bot.bot.mailer.mailer import Mailer
from instapy_bot.bot.utils.photo import Photo

version = pkg_resources.require("instapy_bot")[0].version

config = configparser.ConfigParser()
config_path = join(getcwd(), "instapy-bot.ini")
username = ""
password = ""
folder = "photos"
logger = Logger("instapy-bot.log")
next_upload = join(getcwd(), "nextupload")
mailer = None
watch = False
bedtime = False
timeout = 4320
dt_format = "%Y/%d/%m %H:%M:%S"
mail = False
mail_username = ""
mail_password = ""
mail_to = ""
photos = PhotoStack()
reg_caption = ""
bnw_caption = ""
text_caption = ""


def main():
    global watch, bedtime, config, config_path, logger, username, \
        password, timeout, mail_to, mail_password, mail_username, mail, mailer
    print("instapy-bot " + version + " | python " + python_version())
    if "--log" not in argv:
        logger.set_out(False)
        logger.log("Logging disabled")
    update_config(config, config_path)
    if "--watch" in argv:
        watch = True
        logger.log("Starting in watch mode.")
        argv.remove("--watch")
    if "--bedtime" in argv:
        logger.log("Starting in no bedtime mode.")
        bedtime = True
        argv.remove("--bedtime")

    try:
        if "-c" in argv:
            path = argv[argv.index("-c") + 1]
            config_path = path if isabs(path) else join(getcwd(), path)
        else:
            config_path = join(getcwd(), "instapy-bot.ini")
    except Exception:
        raise SystemExit("Usage: -f <folder> -t <timeout> -c <config> [--watch] [--bedtime] [--log]")
    try:
        if "-f" in argv:
            path = argv[argv.index("-f") + 1]
            photos_dir = path if isabs(path) else join(getcwd(), path)
        elif "folder" in config["config"]:
            path = config["config"]["folder"]
            photos_dir = path if isabs(path) else join(getcwd(), path)
        else:
            photos_dir = getcwd()
        if "-t" in argv:
            try:
                timeout = int(argv[argv.index("-t") + 1])
            except ValueError:
                timeout = 43200
        elif "timeout" in config["config"]:
            timeout = int(config["config"]["timeout"])
        else:
            timeout = 43200

        config["config"] = {
            "timeout": timeout,
            "folder": photos_dir
        }

    except Exception:
        raise SystemExit("Usage: -f <folder> -t <timeout> -c <config> [--watch] [--bedtime] [--log]")
    if not exists(photos_dir):
        logger.log("Photos directory doesn't exist.\n%s" % photos_dir)
        raise SystemExit
    with open(config_path, "w") as configfile:
        config.write(configfile)

    mail = validate_mail(config)
    if mail:
        mail_username = config["mailer"]["username"]
        mail_password = config["mailer"]["password"]
        mail_to = config["mailer"]["to"]
        mailer = Mailer(mail_username, mail_password, mail_to, username)
    possible_answers = ["Y", "N"]
    answer = ""
    while answer.upper() not in possible_answers:
        print("Start uploading from: '%s'" % photos_dir, end="")
        print(" with timeout of '%d'" % timeout)
        answer = input("Are you sure? (Y/N) ")
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
                    if exists(next_upload):
                        with open(next_upload, "r") as nextupload:
                            content = nextupload.read()
                            date = dt.strptime(content, dt_format)
                    if dt.now() >= date:
                        if 1 < date.hour < 9 and bedtime:
                            logger.log("Bed time, skipping upload")
                            sleep(get_timeout((10 - date.hour) * 3600))
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
        raise SystemExit("Bye")


def update_config(cfg, cfg_path):
    global username, password, reg_caption, bnw_caption, logger, text_caption
    if exists(cfg_path):
        cfg.read(cfg_path)
        if "credentials" not in cfg:
            raise SystemExit("Bad config file.")
        else:
            if "username" not in cfg["credentials"] or "password" not in cfg["credentials"]:
                raise SystemExit("Bad config file.")

        username = cfg["credentials"]["username"]
        password = cfg["credentials"]["password"]
        print("Account: %s" % username)
        if username == "":
            raise SystemExit("Invalid instapy-bot.ini username.")
        if password == "":
            password = getpass.getpass()
        print("Password: %s" % "".join(["*" for _ in password]))
        if "caption" in config:
            if "text" in config["caption"]:
                text_caption = config["caption"]["text"]
            if "bnw" in config["caption"]:
                bnw_caption = " ".join(["#" + tag for tag in config["caption"]["bnw"].split(" ")])
            if "reg" in config["caption"]:
                reg_caption = " ".join(["#z" + tag for tag in config["caption"]["reg"].split(" ")])
            logger.log("Updated tags from .ini")
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
    if len(text_caption) > 0:
        caption += text_caption
    if len(reg_caption) > 0:
        caption += "\n" + reg_caption
    if len(bnw_caption) > 0:
        if is_bnw(photo.path):
            caption += "\n\n" + bnw_caption
    try:
        with client(username, password) as cli:
            logger.log(str(photo))
            cli.upload(photo.path, caption)
        remove(photo.path)
    except IOError as e:
        if "The password you entered is incorrect." in str(e):
            config["credentials"]["password"] = ""
            with open(config_path, "w") as configfile:
                config.write(configfile)
            raise WrongPassword("Password The password you entered is incorrect. Please try again.")
        else:
            photos.push(photo)
            logger.log("Retrying photo upload in 60 seconds.")
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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
