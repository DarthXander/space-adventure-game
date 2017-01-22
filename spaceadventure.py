# coding: utf-8
from scene import *
from scene_drawing import *
from math import pi, sin, cos, ceil, acos, atan, sqrt
from colorsys import hsv_to_rgb
from PIL import Image, ImageDraw
import random

debug = False
			
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

def dot(v1, v2):
	m = v1*v2
	return m.x + m.y

def cross(v1, v2):
	# | x  y  z  |
	# | 1x 1y 1z | =   |1y 1z|     |1x 1z|     |1x 1y|
	# | 2x 2y 2z |   x*|2y 2z| - y*|2x 2z| + z*|2x 2y|
	#
	# = x*(1y*2z - 1z*2y) - y*(1x*2z - 1z*2x) + z*(1x*2y - 1y*2x)
	if isinstance(v1, Vector2) and isinstance(v2, Vector2):
		return (v1.x*v2.y - v1.y*v2.x)
	elif isinstance(v1, Vector3) and isinstance(v2, Vector3):
		return Vector3((v1.y*v2.z - v1.z*v2.y), -(v1.x*v2.z - v1.z*v2.x), (v1.x*v2.y - v1.y*v2.x))
	
def rotate(vec, angle):
	c = cos(angle)
	s = sin(angle)
	return Vector2(vec.x*c - vec.y*s, vec.x*s + vec.y*c)

def reflect(v, surface_normal):
			if abs(surface_normal.x**2 + surface_normal.y**2 - 1.0) < .001:
				n = surface_normal/abs(surface_normal)
			else:
				n = surface_normal
			return v-2*dot(v,n)*n

def solve(start1, vec1, start2, vec2):
	# start1 + vec1*dist1 = start2 + vec2*dist2
	# (1)   start1.x + vec1.x*dist1 = start2.x + vec2.x*dist2
	# (2)   start1.y + vec1.y*dist1 = start2.y + vec2.y*dist2
	# (1')  dist1 = (start2.x + vec2.x*dist2 - start1.x)/vec1.x
	# (1')  dist2 = (start1.x + vec1.x*dist1 - start2.x)/vec2.x
	# (2')  dist1 = (vec2.y*dist2 + start2.y - start1.y)/vec1.y
	
	# (2')  dist2 = (vec1.y*dist1 + start1.y - start2.y)/vec2.y
	# (2') -> (1'):
	# dist1 = (start2.x + vec2.x*((vec1.y*dist1 + start1.y - start2.y)/vec2.y) - start1.x)/vec1.x
	# dist1 = (start2.x + (vec2.x/vec2.y)*vec1.y*dist1 + (vec2.x/vec2.y)*start1.y - (vec2.x/vec2.y)*start2.y - start1.x)/vec1.x
	# dist1 = start2.x/vec1.x + (vec2.x/vec2.y)*vec1.y*dist1/vec1.x + (vec2.x/vec2.y)*start1.y/vec1.x - (vec2.x/vec2.y)*start2.y/vec1.x - start1.x/vec1.x
	# dist1*(1 - (vec2.x/vec2.y)*vec1.y/vec1.x) = start2.x/vec1.x + (vec2.x/vec2.y)*start1.y/vec1.x - (vec2.x/vec2.y)*start2.y/vec1.x - start1.x/vec1.x
	
	# bad things that can happen with 0:
	# 1 - vec1.x == 0 and vec2.x == 0
	# 2 - vec1.x == 0 and vec2.y == 0
	# 3 - vec1.y == 0 and vec2.x == 0
	# 4 - vec1.y == 0 and vec2.y == 0
	# general - all vector components non-zero
	# last case - one or both of the vectors has no length. this doesn't make sense for this function, so raise a ValueError:
	if (vec1.x == 0 and vec1.y == 0) or (vec2.x == 0 and vec2.y == 0):
		raise ValueError("Both vectors must have length")
	
	if vec2.y != 0 and vec1.x != 0: # case 3 and general case
		dist1 = (start2.x/vec1.x + (vec2.x/vec2.y)*start1.y/vec1.x - (vec2.x/vec2.y)*start2.y/vec1.x - start1.x/vec1.x)/(1 - (vec2.x/vec2.y)*vec1.y/vec1.x)
		dist2 = (vec1.y*dist1 + start1.y - start2.y)/vec2.y	
	elif vec1.x == 0 and vec2.y == 0: # case 2
		dist1 = (vec2.y*start1.x/vec2.x - vec2.y*start2.x/vec2.x + start2.y - start1.y)/(vec1.y - vec2.y*vec1.x/vec2.x)
		dist2 = (start1.x + vec1.x*dist1 - start2.x)/vec2.x
	else: # case 1 and 4 -- the vectors are parallel; no solution
		return None
	return dist1, dist2

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

class Movement (object):
	def __init__(self, pos, vel, acc, apos, avel, aacc):
		self.position = pos
		self.velocity = vel
		self.acceleration = acc
		self.a_position = apos
		self.a_velocity = avel
		self.a_acceleration = aacc
												
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
		self.landed = 0
		self.planet_landed = None
		self.thrust_force = .1
		self.rotate_force = .003
		self.game = game
		self.context = GameContext(buttons)
		self.flames = []
		# calculate moment of inertia
		i = 0
		collision = self.get_collision()
		for v in collision:
			i += (self.mass/float(len(collision)))*(abs(v - self.position)**2.0)
		self.m_i = i
	@property
	def up(self):
		return rotate(Vector2(0, 1), self.angle)
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
	""""
	def update(self):
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
	"""
	def get_vertices(self, m = None):
		if m == None:
			c = cos(self.angle)
			s = sin(self.angle)
		else:
			c = cos(m.a_position)
			s = sin(m.a_position)
		crop = Rect(0, 0, 1, 1)
		u = [Point(crop.min_x, crop.min_y), Point(crop.max_x, crop.min_y), Point(crop.min_x, crop.max_y), Point(crop.max_x, crop.max_y)]
		
		size = 100
		crop.center(Point(0, 0))
		landed_pos = (crop.h)*size

		r = [Point(crop.min_x*size, crop.min_y*size), Point(crop.max_x*size, crop.min_y*size), Point(crop.min_x*size, crop.max_y*size), Point(crop.max_x*size, crop.max_y*size)]
		# r[2] r[3]
		# r[0] r[1]
		verts = [r[0], r[1], r[2], r[1], r[2], r[3]]
		uverts = [u[0], u[1], u[2], u[1], u[2], u[3]]
		if m == None:
			m = self.give_movement()
		for i, v in enumerate(verts):
			verts[i] = Point(m.position.x + c*v[0] - s*v[1], m.position.y + s*v[0] + c*v[1])
		return verts, uverts
	def get_collision(self, m = None):
		v, _ = self.get_vertices(m)
		collision = []
		origin = v[0]
		width = v[1]-v[0]
		height = v[2]-v[0]
		collision = [Point(0.41, 0.07), Point(0.22, 0.09), Point(0.62, 0.07), Point(0.80, 0.09), Point(0.95, 0.33), Point(0.04, 0.32), Point(0.49, 0.97), Point(0.55, 0.95), Point(0.44, 0.94), Point(0.24, 0.64), Point(0.78, 0.62)]
		for i, c in enumerate(collision):
			collision[i] = origin + width*c.x + height*c.y
		return collision
	def give_movement(self):
		return Movement(self.position, self.velocity, self.acceleration, self.angle, self.v_angle, self.a_angle)
	def set_movement(self, m):
		self.position = m.position
		self.velocity = m.velocity
		self.acceleration = m.acceleration
		self.angle = m.a_position
		self.v_angle = m.a_velocity
		self.a_angle = m.a_acceleration
	def update(self, m):
		pos = m.position
		vel = m.velocity
		acc = m.acceleration
		p_a = m.a_position
		v_a = m.a_velocity
		a_a = m.a_acceleration
		v_a += a_a
		if a_a == 0 and v_a != 0:
			friction = .005
			sign = abs(v_a)/v_a
			v_a += -sign*min(abs(v_a), friction)
		if abs(v_a) < .0001:
			v_a = 0
		p_a += v_a
		acc = Vector2(0, 0)
		if self.accelerating:
			acc += Vector2(sin(-p_a), cos(-p_a))*self.thrust_force
		for celestial in self.game.celestials:
			acc += celestial.calc_force(pos, self.mass)
		vel += acc
		pos += vel
		return Movement(pos, vel, acc, p_a, v_a, a_a)
	def drawobject(self, update = True):
		m = self.give_movement()
		mu = self.update(m)
		pos = mu.position
		verts = self.get_collision(mu)
		pts = []
		lines = []
		hit = False
		planet = None
		for celestial in self.game.celestials:
			r = celestial.radius
			cpos = celestial.position
			for v in verts:
				if abs(v - cpos) <= r:
					hit = True # we're landed
					planet = celestial
					# first, calculate where the ship hit on the planet:
					
					# v is the collision point that hit the planet, so get the location of that point last frame
					i = verts.index(v)
					oldv = self.get_collision(m)[i]
					pts.append(oldv) # and draw it for debug purposes
						
					vec = v - oldv
					moved_by = abs(vec) # how much the point that intersected moved
					vec = vec/moved_by
					to_center = mu.position - v
					# rotate vec by 90 degrees (counterclockwise)
					rvec = Vector2(-vec.y, vec.x)
					
					# some magic math that works for some reason (find the intersection point of a ray with a circle)
					r_section, move = solve(cpos, rvec, v, vec)
					halfchord = sqrt(r**2.0 - r_section**2.0)
					collision_pt = v + vec*(move - halfchord) # go backwards (?) from the new position to the surface of the planet
					
					pts.append((collision_pt, (1, 0, 0))) # draw the point on the surface in red
					pts.append(v)
					#lines.append([cpos, cpos + rvec*r_section])
					#lines.append([v, v + vec*move])
					
					# calculate reflection vector for bounce (fix it though, it's crap.....)
					normal = collision_pt - cpos
					lines.append([cpos, cpos + normal])
					normal = normal/abs(normal)
					bounce = reflect(vec*abs(mu.velocity), normal)
					
					# set the kinematics for next frame # change for actual physics
					deltav = abs(bounce*bouncespeed - mu.velocity)
					
					# torque and angular kinematics
					force = normal*((self.mass*deltav)/deltat_for_impulse)
					torque = cross(force, -1*to_center)
					a_accel = torque/self.m_i
					mu.a_velocity += -a_accel*deltat_for_impulse
					
					# linear kinematics
					# F*∆t = m*∆v
					force = abs(force)
					forcenormal = mu.position - cpos
					lines.append([cpos, cpos + forcenormal, (0,1,0)])
					forcenormal = forcenormal/abs(forcenormal)
					mu.velocity += forcenormal*((force*deltat_for_impulse)/float(self.mass))
					
					#mu.velocity = bounce*.7
					mu.position = collision_pt + to_center
					if debug and self.game.debug_info and self.game.debug_info.should_pause:
						if self.game.debug_info.advance != 0:
							break
						self.game.debug_mode = True
						self.game.debug_info.paused = True
						update = False
						
					break
					
		if hit:
			self.landed += 1
		else:
			self.landed = 0
			self.planet_landed = None
			
		
		######## ACTUAL CRAP HAPPENS HERE
		if self.landed > planet_land_delay and self.planet_landed == None:
			self.planet_landed = planet
			self.game.landed_on(self.planet_landed)
		
		
		
		
		
		
		
		
		######## ^^^^^^ LOTS OF GAME STUFF -- WRITE IT		
														
		lines.append([mu.position, mu.position + mu.velocity*10,(1,0,0)])
		if update:
			self.set_movement(mu)
		self.draw_ship()
		if debug:
			fill(1)
			stroke_weight(0)
			for pt in pts:
				if isinstance(pt, Vector2):
					fill(1)
					ellipse(pt.x - 2, pt.y - 2, 4, 4)
				else:
					fill(pt[1])
					ellipse(pt[0].x - 2, pt[0].y - 2, 4, 4)
			stroke_weight(1)
			stroke(1)
			for l in lines:
				if len(l) == 3:
					stroke(l[2])
				else:
					stroke(1,1,1)
				line(l[0].x, l[0].y, l[1].x, l[1].y)
	def draw(self):
		self.drawobject(False)
	def draw_ship(self):
		verts, uverts = self.get_vertices()
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
			if self.a_angle < 0:
				rightbottom = verts[1]
				righttop = (verts[4] + verts[5])/2.0
				right_anglethruster = (righttop + rightbottom*2)/3.0
				flamedir = Vector2(cos(self.angle), sin(self.angle))
				self.flames.append(Flame(right_anglethruster.x, right_anglethruster.y, flamedir))
			if self.a_angle > 0:
				leftbottom = verts[0]
				lefttop = (verts[4] + verts[5])/2.0
				left_anglethruster = (lefttop + leftbottom*2)/3.0
				flamedir = Vector2(cos(self.angle - pi), sin(self.angle - pi))
				self.flames.append(Flame(left_anglethruster.x, left_anglethruster.y, flamedir))
		for f in self.flames:
			f.draw()
			if f.radius <= 0:
				self.flames.remove(f)
				del f
				
		stroke_weight(0)
		tint(1,1,1)
		fill(1,1,1,.3)
		
		if debug:
			triangle_strip(self.get_collision(self.give_movement()))
		triangle_strip(verts, uverts, "graphics/spaceship.png")
		
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
