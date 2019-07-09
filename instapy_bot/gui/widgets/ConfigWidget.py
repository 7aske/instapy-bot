from PyQt5.QtWidgets import QComboBox, QVBoxLayout, QLabel, QTextEdit, QWidget, QCheckBox


class ConfigWidget(QWidget):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.setLayout(QVBoxLayout())

		self.cred_label = QLabel(text="Credentials")
		self.conf_label = QLabel(text="Config")
		self.capt_label = QLabel(text="Caption")
		# self.mail_label = QLabel(text="Mailer")

		# self.cred_check = QCheckBox(text="Credentials")
		# self.conf_check = QCheckBox(text="Config")
		# self.capt_check = QCheckBox(text="Caption")
		self.mail_check = QCheckBox(text="Myailer")

		self.layout().addWidget(self.cred_label)
		# self.layout().addWidget(self.cred_check)
		self.layout().addWidget(self.conf_label)
		# self.layout().addWidget(self.conf_check)
		self.layout().addWidget(self.capt_label)
		# self.layout().addWidget(self.capt_check)
		# self.layout().addWidget(self.mail_label)
		self.layout().addWidget(self.mail_check)


