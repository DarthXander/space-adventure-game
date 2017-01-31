from scene import *
from math import pi
from colorsys import hsv_to_rgb
import random

from basic_objects import *

g = .0003

valid_landing_angle = 2*pi*(5.0/360.0)
planet_land_delay = 10 # number of frames touching a planet before considered landed on that planet
deltat_for_impulse = 1/60.0
bouncespeed = .6

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
	def valid_landing(self, center, up):
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
