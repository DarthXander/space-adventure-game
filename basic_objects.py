class GameObject (object):
	def pause(self):
		pass
	def play(self):
		pass

class DrawableGameObject (GameObject):
	def drawobject(self):
		self.draw()
	def draw(self):
		pass
