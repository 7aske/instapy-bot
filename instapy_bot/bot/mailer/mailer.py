import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailer:
    username = ""
    password = ""
    mail_to = ""
    account = ""

    def __init__(self, username, password, mail_to, account):
        self.username = username
        self.password = password
        self.mail_to = mail_to
        self.account = account

    def send_mail(self, nextupload, remaining):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Instagram Upload"
        msg['From'] = self.username
        msg['To'] = self.mail_to
        html = """\
        <html>
          <head></head>
          <body>
            New photo uploaded on account <b><a href="https://instagram.com/{account}">{account}</a></b>.<br><br>
            Next scheduled for: <u><b>{nextupload}</u></b>.<br><br>
            Remaining photos: <b>{remaining}</b>.
          </body>
        </html>
        """.format(account=self.account, nextupload=nextupload, remaining=remaining)
        text = ("Subject: Instagram Upload\n\n"
                "New photo uploaded on account %s.\n\n"
                "Next scheduled for: %s.\n"
                "Remaining photos: %d."
                % (self.account, nextupload, remaining))
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        try:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, self.mail_to, msg.as_string())
            server.quit()
        except Exception as e:
            print(str(e))
            raise IOError(str(e))
