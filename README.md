instapy-bot
==========================


## Description
CLI bot for automated and scheduled Instagram photos uploading using instagrams private API. Uploading via private API was made possible by using sligthly modified version of [instapy-cli](https://github.com/b3nab/instapy-cli) by **b3nab**.

## Usage

After running ``python setup.py install`` two commands will be available to use in your shell. \
``instapy-cli`` which is becaully the original instapy-cli script
``instapy-bot`` which is the bot-like wrapper that can be configured
---

``instapy-bot -f ./photos -t 3600 -c <path/to/config.ini>``\
This simple command will upload all the photos from photos folder with a timer of 60 seconds(timer is randomized with up to +-10% of difference). You will be prompted for the username and password which will be stored in a .ini file in the same directory
---
You can use mentioned .ini file to do further confguration.
```ini
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

[tags]
reg = \ #nature #candid #photooftheday
bnw = \ #bnw #blackandwhite
```
As you can see there are some aditional settings.\
`config` section is used to specify paramters that you would otherwise assign in the command line.\
`mailer` section is used to provide mail notification using pythons built in smpt library. There you would use your spare email account and send yourself email notifications.\
`tags` section is used to assign captions to photographs. Bot can distinguish between grayscale and color images and assign different groups of tags to each. Keep in mind that if the photo is grayscale bnw tags are just getting appended to the existings ones.
---
Furthermore you can put a file with the same name as the photograph in the folder only with `.txt` extension containing the caption and the bot will read that instead of the predefined ones.

---
After a successful upload ``nextupload`` file is created in the directory containing the next upload time. That means you can restart the bot whenever you want and it will wait for that time before uploading.

---
####Additional options
`--watch`   prevents bot from exiting and makes wait for photos to be added to the specified folder.\
`--bedtime` prevents uplading during sleeping hours 1AM - 8AM. \
`--log`     outputs the logs to `instapy-bot.log` file in the same directory.

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

## Requirements

Package requirements are handled using pip. To install them do

```
pip install -r requirements.txt
```
## Conclusion

This is my first sort of well-rounded package release on github so im happy to recieve suggestions.
 Pull requests are welcome as well.