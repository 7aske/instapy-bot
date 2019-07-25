# instapy-bot

## Description

CLI bot for automated and scheduled Instagram photos uploading using instagrams private API. Uploading via private API was made possible by using slightly modified version of [instapy-cli](https://github.com/b3nab/instapy-cli) by **b3nab**.

## Installation

After running:

`# python3 -m pip install -r requirements.txt`

and

`# python -m pip install -I -e .`

two commands will be available to use in your shell.

`$ instapy-cli` - which is basically the original instapy-cli script.

`$ instapy-bot` - which is the wrapper that can be configured to automate the upload process.

## Usage

```
$ instapy-bot -f ./photos -t 3600
```

This simple command will upload all the photos from photos folder with a timer of 60 seconds (timer is randomized with up to +-10% of difference). You will be prompted for the username and password which will be stored in a .conf file in the same current working directory.

If you have a instapy-bot.conf file in the current working directory you can simply run `$ instapy-bot` and the configuration file will be automatically loaded. Otherwise if the file is located in a different directory you can specify the path with `-c` flag and the resulting command would look like:

```
$ instapy-bot -c /path/to/config
```

---
You can use mentioned .conf file to do further configuration.

```conf
[credentials]
username = instagram_username
password = instagram_password

[config]
timeout = 3600
folder = /path/to/photos/folder

[mailer]
to = mail_to@example.com
username = mailer_username
password = mailer_password

[caption]
text = Photo of the day
reg = candid nature photooftheday
bnw = bnw blackandwhite
```

As you can see there are some additional settings.

`config` section is used to specify parameters that you would otherwise assign in the command line.

`mailer` section is used to provide mail notification using pythons built in SMPT library. There you would use your spare email account and send yourself email notifications.

`caption` section is used to assign captions to photographs. Bot can distinguish between grayscale and color images and assign different groups of tags to each. Keep in mind that if the photo is grayscale bnw tags are just getting appended to the existing ones. `bnw` and `reg` are being parsed as hashtags("#" is added to front) and `text` is the caption text.

Furthermore you can put a file with the same name as the photograph in the folder only with `.txt` extension containing the caption and the bot will read that instead of the predefined ones.

After a successful upload ``nextupload`` file is created in the directory containing the next upload time. That means you can restart the bot whenever you want and it will wait for that time before uploading.

### Additional options

`--watch, -w` - prevents bot from exiting and makes wait for photos to be added to the specified folder.

`--bedtime, -b` -  prevents uploading during sleeping hours 1AM - 8AM.

`--log, -l` - outputs the logs to `instapy-bot.log` file in the same directory.

`--config, -C` - generate a `instapy-bot.conf` file in the current working directory and exits.

`--yes -y` - answers "yes" to the confirmation dialog. Useful if run in scripts.

You can always run the program with `--help` to display all of the information.

## Package

Basic structure of package is

```
.
├── CHANGELOG.md
├── CONTRIBUTING.md
├── instapy_bot
│   ├── bot
│   │   ├── __init__.py
│   │   ├── logger
│   │   │   ├── __init__.py
│   │   │   └── logger.py
│   │   ├── mailer
│   │   │   ├── __init__.py
│   │   │   └── mailer.py
│   │   ├── __main__.py
│   │   └── utils
│   │       ├── __init__.py
│   │       └── photo.py
│   │  
│   ├── cli
│   │   ├── cli.py
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── media.py
│   │   └── session.py
│   ├── __init__.py
│   └── version.py
├── LICENSE
├── README.md
├── requirements.txt
└── setup.py

```

## Conclusion

This is my first sort of well-rounded package release on github so im happy to receive suggestions. Pull requests and other contributions are more than welcome.
