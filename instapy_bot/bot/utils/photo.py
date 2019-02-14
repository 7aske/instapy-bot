class Photo:
    path = ""
    caption = ""

    def __init__(self, path, caption=""):
        self.path = path
        self.caption = caption

    def set_caption(self, caption):
        self.caption = caption

    def get_caption(self):
        return self.caption

    def __repr__(self) -> str:
        return "Photo path='{path}' caption='{caption}'".format(path=self.path, caption=self.caption)

