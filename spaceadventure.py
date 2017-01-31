# coding: utf-8
from scene import *
from scene_drawing import *
from math import pi, sin, cos, ceil, acos, atan, sqrt

from PIL import Image, ImageDraw
import random

# other files
from vehicles import *
from celestials import *
from contexts import *
from global_constants import *
			
def distribution(x):
	d = abs(x - 1.5)
	if d < .1:
		n = 1
	elif d < .2:
		n = 3
	elif d < .40:
		n = 5
	else:
		n = 7
	return ((x*2 - 1)**n + 1)/2.0

def generate(min, max):
	l = max - min
	return min + l*distribution(random.random())

# remember to add distribution skew function!
# which means:
# for example a planet with a higher mass would have the bell curve scooted over so that it would have more moons more often than a planet with less mass, which would have less moons far more often (almost always 0 for a small planet)
# then say for that small planet which happened to spawn a moon, it will spawn small, because of the skewing of the original spawn
# so skewing will inherit among class delegation for the solar system generation classes.
	
class SpaceAdventure (Scene):
	@property
	def vehicle(self):
		return self._vehicle
	@vehicle.setter
	def vehicle(self, value):
		self._vehicle = value
		self.context = value.get_context()
		
	def setup(self):
		self.context = blankcontext
		
		### DEBUG CODE v
		class DebugInfo (object):
			scroll = Point(0,0)
			scale = 1
			advance = 0
			paused = True
			should_pause = False
		
		self.debug_info = DebugInfo()
		def drawdebugpause(x, y, diameter, active, pressed):
			fill(1, 0, 0)
			stroke(.8,.8,.8)
			stroke_weight(2)
			if pressed:
				fill(0,1,0)
			if not active:
				fill(.3, .3, .3)
				
			rect(x - diameter/2.0, y - diameter/2.0, diameter, diameter)
			diameter *= .7
			stroke_weight(0)
			fill(.8,.8,.8)
			if not self.debug_info.paused:
				rect(x - diameter/2.0, y - diameter/2.0, diameter/3., diameter)
				rect(x - diameter/2.0 + diameter*2./3., y - diameter/2.0, diameter/3., diameter)
			else:
				v = [(x - diameter/2.0, y - diameter/2.0), (x - diameter/2., y + diameter/2.), (x + diameter/2., y)]
				triangle_strip(v)
		def drawdebugbutton(x, y, diameter, active, pressed):
			fill(1,0,0)
			stroke_weight(2)
			stroke(.8,.8,.8)
			if pressed:
				fill(0, 1, 0)
			if not active:
				fill(.3, .3, .3)
			rect(x - diameter/2.0, y - diameter/2.0, diameter, diameter)
			text("debug", x = x, y = y)
		def drawdebugadvance(x, y, diameter, active, pressed):
			fill(1, 0, 0)
			stroke(.8, .8, .8)
			stroke_weight(2)
			if pressed:
				fill(0, 1, 0)
			if not active:
				fill(.3, .3, .3)
			rect(x - diameter/2.0, y - diameter/2.0, diameter, diameter)
			diameter *= .7
			line(x - diameter/2.0, y - diameter/2.0, x + diameter/2.0, y)
			line(x + diameter/2.0, y, x - diameter/2.0, y + diameter/2.0)
		def drawdebugshouldpause(x, y, diameter, active, pressed):
			fill(1, 0, 0)
			stroke(.8,.8,.8)
			stroke_weight(2)
			if pressed:
				fill(0,1,0)
			if not active:
				fill(.3, .3, .3)	
			rect(x - diameter/2.0, y - diameter/2.0, diameter, diameter)
			text("pause on\nplanet\ncollision:", x = x, y = y + diameter/7.0, font_size = 12)
			if self.debug_info.should_pause:
				txt = "yes"
			else:
				txt = "no"
			text(txt, x = x, y = y - diameter/4.0, font_size = 14)
		debugshouldpausebutton = Button(self.bounds.w*.6, self.bounds.h*.9, self.debug_should_pause_button_pressed, draw = drawdebugshouldpause)	
		debugpausebutton = Button(self.bounds.w*.8, self.bounds.h*.9, self.debug_pause_button_pressed, draw = drawdebugpause)
		debugpausebutton.active = False
		debugadvancebutton = Button(self.bounds.w*.7, self.bounds.h*.9, self.debug_advance_button_pressed, draw = drawdebugadvance)
		debugadvancebutton.active = False
		debugbutton = Button(self.bounds.w*.9, self.bounds.h*.9, self.debug_button_pressed, draw = drawdebugbutton)
		self.debugcontext = GameContext([debugbutton, debugpausebutton, debugadvancebutton, debugshouldpausebutton])
		self.debug_mode = False
		### DEBUG CODE ^
		
		self.vehicle = Ship(self, 0, 0)
		self.view_rect = self.scale(self.bounds, 1.5)
		self.view_rect.center(self.vehicle.position)
		self.view_scale = 1.5
		
		self.celestials = []
		for x in range(-5, 5):
			for y in range(-5, 5):
				if not (x == 0 and y == 0):
					self.celestials.append(Planet(x*2000, y*2000, radius = 500 + random.random()*400))
		#self.stars = Stars(self)
		self.started = True
	
	@property
	def debug_mode(self):
		return self._debug_mode
	@debug_mode.setter
	def debug_mode(self, value):
		if hasattr(self, "_debug_mode") and value == self._debug_mode:
			return
		if value:
			self.debugcontext.buttons[1].active = True
			self.debugcontext.buttons[2].active = True
			self.debug_info.scroll = self.view_rect.center()
			self.debug_info.scale = self.view_scale
		else:
			self.debugcontext.buttons[1].active = False
			self.debugcontext.buttons[2].active = False
		self._debug_mode = value
		
	def debug_should_pause_button_pressed(self, pressed):
		if pressed:
			self.debug_info.should_pause = not self.debug_info.should_pause
	def debug_button_pressed(self, pressed):
		if pressed:
			self.debug_mode = not self.debug_mode
	def debug_advance_button_pressed(self, pressed):
		if pressed:
			self.debug_info.advance = 1
	def debug_pause_button_pressed(self, pressed):
		if pressed:
			self.debug_info.paused = not self.debug_info.paused
	def landed_on(self, planet):
		planet.color = (.2,.2,.2)
	def scale(self, rect, s):
		return Rect(rect.x - rect.w/s, rect.y - rect.h/s, rect.w*s, rect.h*s)
	def draw(self):
		if not hasattr(self, "started"):
			return
		background(.01, .0, .08)
		self.draw_in_view_rect()
		self.context.drawobject()
		if debug:
			self.debugcontext.drawobject()
	def draw_in_view_rect(self):
		if not self.debug_mode:
			target = min(1.5 + self.vehicle.speed/20.0, 3)
			self.view_scale += (target - self.view_scale)/100.0
			self.view_rect = self.scale(self.bounds, self.view_scale)
			self.view_rect.center(self.vehicle.position)
		else:
			self.view_rect = self.scale(self.bounds, self.debug_info.scale)
			self.view_rect.center(self.debug_info.scroll)
		push_matrix()
		scale(self.bounds.w/self.view_rect.w, self.bounds.h/self.view_rect.h)
		translate(-self.view_rect.x, -self.view_rect.y)
		#self.stars.drawobject()
		if self.debug_mode and (self.debug_info.paused and self.debug_info.advance == 0):
			for c in self.celestials:
				c.draw()
			self.vehicle.draw()
		else:
			for c in self.celestials:
				c.drawobject()
			self.vehicle.drawobject()
			if self.debug_mode and self.debug_info.advance > 0:
				self.debug_info.advance -= 1
		pop_matrix()
	def touch_began(self, touch):
		self.context.touch_began(touch)
		if debug:
			self.debugcontext.touch_began(touch)
	def touch_moved(self, touch):
		if debug and self.debug_mode:
			self.debug_info.scroll -= (touch.location - touch.prev_location)*self.debug_info.scale
			if len(self.touches) >= 2:
				d1 = abs(self.touches.values()[0].prev_location - self.touches.values()[1].prev_location)
				d2 = abs(self.touches.values()[0].location - self.touches.values()[1].location)
				scalediff = d1/float(d2)
				self.debug_info.scale *= scalediff
	def touch_ended(self, touch):
		self.context.touch_ended(touch)
		if debug:
			self.debugcontext.touch_ended(touch)
	
blankcontext = GameContext([])
spaceadventure = SpaceAdventure()
run(spaceadventure, show_fps = debug)
