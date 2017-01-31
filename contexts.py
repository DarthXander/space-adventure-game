from basic_objects import *
from scene import *

class Button (object):
	def __init__(self, x, y, pressed_func, diameter = 80, draw = None, image = None):
		# draw must be a function with signature:
		#	
		#	def draw(x, y, diameter, active, pressed)
		#
		#	where (x, y) is the center of the button
		#	active is a boolean value representing whether the button is pressable or not
		#.	and pressed is a boolean value representing whether the button pressed or not
		#
		# pressed_func must be a function with signature:
		#
		# 	def pressed_func(pressed)
		#
		# 	where pressed is a boolean value representing the state the button has just changed to.
		# 	this function will be called with corresponding arguments when the Button.pressed attribute changes.
		self.position = Point(x, y)
		self._pressed = False
		self.active = True
		self.pressed_func = pressed_func
		self.diameter = diameter

		if draw != None:
			self.draw_func = draw
		else:
			def d(x, y, diameter, active, pressed):
				stroke(0, 0, 0)
				stroke_weight(2)
				if active:
					if pressed:
						fill(.9, .0, .0)
					else:
						fill(.8, .0, .0)
				else:
					fill(.79, .79, .79)
				ellipse(x - diameter/2.0, y - diameter/2.0, diameter, diameter)
			self.draw_func = d
	@property 
	def pressed(self):
		return self._pressed
	@pressed.setter
	def pressed(self, value):
		self._pressed = value
		self.pressed_func(self._pressed)
	def draw(self):
		self.draw_func(self.position.x, self.position.y, self.diameter, self.active, self.pressed)

class GameContext (DrawableGameObject):
	def __init__(self, buttons):
		self.buttons = buttons
		self.touches = {}
	def draw(self):
		for button in self.buttons:
			button.draw()
	def touch_began(self, touch):
		for b in self.buttons:
			if abs(touch.location - b.position) <= b.diameter/2.0:
				self.touches[touch] = b
				b.pressed = True
				return
	def touch_ended(self, touch):
		if touch in self.touches:
			self.touches[touch].pressed = False
			self.touches.pop(touch)
