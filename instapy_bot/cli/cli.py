from instapy_bot.cli.session import InstapySession
from instapy_bot.cli.media import Media


class Cli(object):
    media = None

    def __init__(self, username, password):
        self._session = InstapySession()
        self._session.login(username, password)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.clean_up()
        pass

    def upload(self, file, caption=""):
        self.media = Media(file)
        upload_completed = True

        try:
            media_id = self._session.upload_photo(self.media.get_path())
            self._session.configure_photo(media_id, caption)
        except Exception as e:
            print(str(e))
            print("\nSomething went bad.\n")
            upload_completed = False
        finally:
            if upload_completed:
                print("Uploaded %s" % self.media.get_path())
            else:
                self.clean_up()
                raise IOError("Unable to upload")

            self.clean_up()

    def clean_up(self):
        self.media.remove_media()
