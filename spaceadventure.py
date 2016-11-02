# coding: utf-8
from scene import *
from math import pi, sin, cos, ceil, acos, atan
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw
import random

def distribution(x):
	d = abs(x - .5)
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

# looking like a good plan so far!

g = .0003

valid_landing_angle = 2*pi*(5.0/360.0)

min_planet_num = 1
max_planet_num = 8

min_sun_mass = 5000
max_sun_mass = 50000

min_planet_mass = 20
max_planet_mass = 500

min_moon_mass = 3
max_moon_mass = 17

min_moon_num = -3
max_moon_num = 5

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

class StarSection (object):
	def __init__(self, x, y, w, h):
		random.seed(x+y + (2*x + 3)^(3*y + 2))
		self.stars = []
		for i in range(random.randint(2,4)):
			brightness = .5 + random.random()/2.0
			pos = Point(x + random.random()*w, y + random.random()*h)
			self.stars.append((brightness, pos))
	def draw(self):
		for s in self.stars:
			fill(s[0])
			ellipse(s[1].x, s[1].y, 1.5, 1.5)

class Stars (DrawableGameObject):
	def __init__(self, game):
		self.game = game
		self.density = 150.0
		self.stars = {}
	def snap(self, rect, snapto):
		snapto = float(snapto)
		start = Point(int(rect.min_x/snapto), int(rect.min_y/snapto))*snapto
		end = Point(int(rect.max_x/snapto)+1, int(rect.max_y/snapto)+1)*snapto
		size = Size(end.x - start.x, end.y - start.y)
		return Rect(start.x, start.y, size.w, size.h)
	def draw(self):
		r = self.snap(self.game.view_rect.inset(-self.density, -self.density), self.density)
		for x in range(int(r.x), int(r.max_x), int(self.density)):
			for y in range(int(r.y), int(r.max_y), int(self.density)):
				good = False
				if x in self.stars:
					if y in self.stars[x]:
						good = True
				if not good:
					if x not in self.stars:
						self.stars[x] = {}
					self.stars[x][y] = StarSection(x, y, self.density, self.density)
				self.stars[x][y].draw()

class Celestial (DrawableGameObject):
	def __init__(self, x, y, radius = None, mass = None, density = .01):
		self.position = Point(x, y)
		self.density = density
		if mass == None and radius == None:
			raise ValueError("Celestial contructor must supply mass or radius")
		if mass == None:
			self.radius = radius
			self.mass = self.calc_mass()
		if radius == None:
			self.mass = mass
			self.radius = self.calc_radius()
	def calc_force(self, other_pos, mass):
		v = self.position - other_pos
		length = abs(v)
		f = (g*mass*self.mass)/(length**2)
		norm = v/length
		return norm*f
	def calc_mass(self):
		volume = (4.0/3)*pi*(self.radius**3)
		return volume*self.density
	def calc_radius(self):
		return ((3.0*self.mass)/(4.0*self.density*pi))**(1.0/3.0)
	def collision_test_rect(self, pts):
		for p in pts:
			if abs(p - self.position) <= self.radius:
				return True
	def valid_landing(self, center, vert):
		out = center - self.position
		out = out/abs(out)
		return acos(out.x * vert.x + out.y * vert.y) < valid_landing_angle
	def landed_pos(self, center, height):
		out = center - self.position
		nout = out/abs(out)
		angle = atan(out.y/out.x) + pi/2.0 + (pi if out.x > 0 else 0)
		return (self.position + nout*(self.radius + height/2.0), angle)

class Path (object):
	def __init__(self, path, speed = .01):
		# path is a function that takes one float parameter between 0 and 1
		# this function must return a scene.Point object
		# this function must be cyclic -> position at 1 equals position at 0
		self.path = path
		self.speed = speed
		self.progress = 0
	def next_position(self):
		self.progress += self.speed
		return self.path(self.progress)
	def look_next(self):
		return self.path(self.progress + self.speed)
	def look_previous(self):
		return self.path(self.progress - self.speed)
	def current(self):
		return self.path(self.progress)

class SolarSystemSpawner (object):
	pass
	
class SolarSystemGenerator (object):
	def __init__(self, seed, sun_position, planets):
		pass
	
class SunGenerator (object):
	pass
	
class PlanetMoonSystemGenerator (object):
	pass
	
class PlanetGenerator (object):
	pass

class MoonGenerator (object):
	pass
	
class Sun (Celestial):
	pass

class Planet (Celestial):
	def __init__(self, *args, **kwargs):
		Celestial.__init__(self, *args, **kwargs)
		if "biome" in kwargs:
			self.biome = kwargs["biome"]
		self.color = hsv_to_rgb(random.random(), .6, .6)
	def draw(self):
		stroke_weight(0)
		fill(self.color)
		ellipse(self.position.x - self.radius, self.position.y - self.radius, self.radius*2, self.radius*2)
		
	
class Moon (Celestial):
	pass
	
class SolarSystem (DrawableGameObject):
	pass
	
class PlanetMoonSystem (DrawableGameObject):
	pass

class Vehicle (DrawableGameObject):
	def __init__(self, game, x, y):
		self.position = Point(x, y)
		self.context = None
	def get_context(self):
		return self.context	
													
class Flame (object):
	def __init__(self, x, y, direction):
		self.position = Point(x, y)
		self.color = (1.0, .32, .08)
		self.speed = 4 + random.random()*2
		self.radius = 15
		self.direction = direction
	def draw(self):
		self.position += self.direction*self.speed
		self.radius -= .5
		decay = .95
		self.color = (self.color[0]*decay, self.color[1]*decay, self.color[2]*decay)
		stroke_weight(0)
		fill(self.color)
		ellipse(self.position.x - self.radius, self.position.y - self.radius, self.radius*2, self.radius*2)
		
												
class Ship (Vehicle):
	def __init__(self, game, x, y):
		self.position = Point(x, y)
		self.velocity = Vector2(0, 0)
		self.acceleration = Vector2(0, 0)
		self.accelerating = False
		self.mass = 10
		self.angle = 0
		self.v_angle = 0
		self.a_angle = 0
		buttons = []
		buttons.append(Button(game.bounds.w*.9, game.bounds.h*.1, self.accelerate))
		buttons.append(Button(game.bounds.w*.1, game.bounds.h*.1, self.rotate_left))
		buttons.append(Button(game.bounds.w*.2, game.bounds.h*.1, self.rotate_right))
		self.landed = False
		self.thrust_force = .1
		self.rotate_force = .003
		self.game = game
		self.context = GameContext(buttons)
		self.flames = []
	def accelerate(self, state):
		if state:
			self.accelerating = True 
			self.landed = False
		else:
			self.accelerating = False
	def rotate_left(self, state):
		if state:
			self.a_angle = self.rotate_force
		else:
			self.a_angle = 0
	def rotate_right(self, state):
		if state:
			self.a_angle = -self.rotate_force
		else:
			self.a_angle = 0
	def get_context(self):
		return self.context
	@property
	def speed(self):
		return abs(self.velocity)
	def draw(self):
		x = self.position.x
		y = self.position.y
		c = cos(self.angle)
		s = sin(self.angle)
		
		crop = Rect(0, .1, 1, .9)
		u = [Point(crop.min_x, crop.min_y), Point(crop.max_x, crop.min_y), Point(crop.min_x, crop.max_y), Point(crop.max_x, crop.max_y)]
		
		size = 100
		crop.center(Point(0, 0))
		landed_pos = (crop.h)*size
		r = [Point(crop.min_x*size, crop.min_y*size), Point(crop.max_x*size, crop.min_y*size), Point(crop.min_x*size, crop.max_y*size), Point(crop.max_x*size, crop.max_y*size)]
		# r[2] r[3]
		# r[0] r[1]
		
		verts = [r[0], r[1], r[2], r[1], r[2], r[3]]
		uverts = [u[0], u[1], u[2], u[1], u[2], u[3]]
		collision = [r[0], r[2], (r[1] + r[3])/2.0]
		
		for i, v in enumerate(verts):
			verts[i] = Point(self.position.x + c*v[0] - s*v[1], self.position.y + s*v[0] + c*v[1])
			
		nv = self.velocity + self.acceleration
		np = self.position + nv
		for i, v in enumerate(collision):
			collision[i] = Point(np.x + c*v[0] - s*v[1], np.y + s*v[0] + c*v[1])
			
		if self.accelerating:
			leftbottom = Point(verts[0][0], verts[0][1])
			rightbottom = Point(verts[1][0], verts[1][1])
			bottomside = rightbottom - leftbottom
			leftthruster = leftbottom + bottomside*.3
			rightthruster = leftbottom + bottomside*.7
			
			for flamepos in [leftthruster, rightthruster]:
				flamedir = Vector2(cos(self.angle - pi/2.0), sin(self.angle - pi/2.0))
				self.flames.append(Flame(flamepos.x, flamepos.y, flamedir))
			
		if self.a_angle != 0:
			if self.a_angle > 0:
				rightbottom = verts[1]
				righttop = (verts[4] + verts[5])/2.0
				right_anglethruster = (righttop + rightbottom)/2.0
				flamedir = Vector2(cos(self.angle), sin(self.angle))
				self.flames.append(Flame(right_anglethruster.x, right_anglethruster.y, flamedir))
			if self.a_angle < 0:
				leftbottom = verts[0]
				lefttop = (verts[4] + verts[5])/2.0
				left_anglethruster = (lefttop + leftbottom)/2.0
				flamedir = Vector2(cos(self.angle - pi), sin(self.angle - pi))
				self.flames.append(Flame(left_anglethruster.x, left_anglethruster.y, flamedir))
		for f in self.flames:
			f.draw()
			if f.radius <= 0:
				self.flames.remove(f)
				del f
		for celestial in self.game.celestials:
			if celestial.collision_test_rect(collision):
				if celestial.valid_landing(self.position, Vector2(cos(self.angle + pi/2.0), sin(self.angle + pi/2.0))):
					self.acceleration = Vector2(0, 0)
					self.velocity = Vector2(0, 0)
					self.a_angle = 0
					self.v_angle = 0
					landed = celestial.landed_pos(self.position, landed_pos)
					self.position = landed[0]
					self.angle = landed[1]
					self.landed = True
				else:
					self.velocity *= -.5
		stroke_weight(0)
		tint(1,1,1)
		fill(1,1,1,.5)
		
		#triangle_strip(verts)
		triangle_strip(verts, uverts, "graphics/spaceship.PNG")
		
		
		if not self.landed:
			self.v_angle += self.a_angle
			if self.a_angle == 0:
				self.v_angle *= .9
			if abs(self.v_angle) < .0001:
				self.v_angle = 0
			self.angle += self.v_angle
			self.acceleration = Vector2(0, 0)
			if self.accelerating:
				self.acceleration += Vector2(sin(-self.angle), cos(-self.angle))*self.thrust_force
			for celestial in self.game.celestials:
				self.acceleration += celestial.calc_force(self.position, self.mass)
			self.velocity += self.acceleration
			self.position += self.velocity
		
class Button (object):
	def __init__(self, x, y, pressed_func, diameter = 80, draw = None, image = None):
		# draw must be a function with signature:
		#	
		#		def draw(x, y, active, pressed)
		#
		#		where (x, y) is the center of the button
		#		active is a boolean value representing whether the button is pressable or not
		#		and pressed is a boolean value representing whether the button pressed or not
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
		self.vehicle = Ship(self, 0, 0)
		self.view_rect = self.scale(self.bounds, 1.5)
		self.view_rect.center(self.vehicle.position)
		self.view_scale = 1.5
		type(self.view_rect)
		self.celestials = [Planet(1000, 1000, radius = 800), Planet(-500, -500, radius = 200)]
		self.stars = Stars(self)
		
	def scale(self, rect, s):
		return Rect(rect.x - rect.w/s, rect.y - rect.h/s, rect.w*s, rect.h*s)
	def draw(self):
		if not hasattr(self, "stars"):
			return
		background(.01, .0, .08)
		self.draw_in_view_rect()
		self.context.drawobject()
	def draw_in_view_rect(self):
		target = min(1.5 + self.vehicle.speed/20.0, 3)
		self.view_scale += (target - self.view_scale)/100.0
		self.view_rect = self.scale(self.bounds, self.view_scale)
		self.view_rect.center(self.vehicle.position)
		push_matrix()
		scale(self.bounds.w/self.view_rect.w, self.bounds.h/self.view_rect.h)
		translate(-self.view_rect.x, -self.view_rect.y)
		self.stars.drawobject()
		for c in self.celestials:
			c.drawobject()
		self.vehicle.drawobject()
		pop_matrix()
	def touch_began(self, touch):
		self.context.touch_began(touch)
	def touch_ended(self, touch):
		self.context.touch_ended(touch)
	
blankcontext = GameContext([])
spaceadventure = SpaceAdventure()
run(spaceadventure, show_fps = True)
