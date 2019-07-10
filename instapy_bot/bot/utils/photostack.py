from os.path import isabs


class PhotoStack:
	def __init__(self):
		self.photos = []

	def __repr__(self):
		return str([str(photo) for photo in self.photos])

	def __len__(self):
		return len(self.photos)

	def push(self, item):
		from instapy_bot.bot.utils.photo import Photo
		if isinstance(item, Photo):
			self.photos.append(item)
		elif isabs(item):
			self.photos.append(Photo(item))

	def pop(self):
		return self.photos.pop()

	def is_empty(self):
		return self.photos == []
