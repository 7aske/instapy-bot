class WrongPassword(Exception):
	def __init__(self, *args: object) -> None:
		super().__init__(*args)
		print("Wrong password")


class ServerError(Exception):

	def __init__(self, *args: object) -> None:
		super().__init__(*args)
		print("Server Error")
