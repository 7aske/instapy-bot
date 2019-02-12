from os import getcwd
from os.path import join, isabs
from datetime import datetime as dt


class Logger:
    file = ""
    out = True
    dt_format = "%d/%m %H:%M:%S"

    def __init__(self, file, out=True):
        if isabs(file):
            self.file = file
        else:
            self.file = join(getcwd(), file)
        self.out = out

    def log(self, data):
        output = "{}:\t{}".format(dt.now().strftime(self.dt_format), data + "\n")
        if self.out:
            with open(self.file, "a+") as f:
                f.write(output)
        print(data)

    def set_file(self, file):
        self.file = file

    def get_file(self):
        return self.file

    def set_out(self, out):
        self.out = out

    def get_out(self):
        return self.out
