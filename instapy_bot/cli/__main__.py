from platform import python_version
from instapy_bot.cli import client
from optparse import OptionParser
import pkg_resources

version = pkg_resources.require("instapy_bot")[0].version


def main(args=None):
    print("instapy-bot " + version + " | python " + python_version())

    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-u", dest="username", help="username")
    parser.add_option("-p", dest="password", help="password")
    parser.add_option("-f", dest="file", help="file path or url")
    parser.add_option("-t", dest="caption", help="caption text")

    (options, args) = parser.parse_args(args)
    if args is None or (
            not options.username and
            not options.password and
            not options.file and
            not options.caption
    ):
        print("[USE] instapy -u USR -p PSW -f FILE/LINK -t 'TEXT CAPTION'")
        return
    username = options.username
    if not options.username:
        username = input("Username: ")
    password = options.password
    if not options.password:
        import getpass
        password = getpass.getpass()
    if not options.file:
        parser.error("File path or url link is required")
    with client(username, password) as cli:
        text = options.caption or ""
        cli.upload(options.file, text)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
