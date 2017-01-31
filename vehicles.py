# coding: utf-8
from math import sin, cos, pi, sqrt
from scene import *
import random

from basic_objects import *
from contexts import *
from global_constants import *
from vector_operations import *

valid_landing_angle = 2*pi*(5.0/360.0)
planet_land_delay = 10 # number of frames touching a planet before considered landed on that planet
deltat_for_impulse = 1/60.0
bouncespeed = .6

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
												
class Collision (object):
	def __init__(self, collision_pt, planet, position):
		self.point = collision_pt
		self.planet = planet
		self.position = position
												
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
		
		collisions = []
		
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
					if abs(bounce) > 100:
						deltav = abs(bounce*bouncespeed - mu.velocity)
					else:
						deltav = abs(mu.velocity)
					
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
		
		if len(collisions) > 0:
			# we hit something
			pass
		else:
			# normal; just traveling through space
			pass
		
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
		
		#if debug:
		#	triangle_strip(self.get_collision(self.give_movement()))
		triangle_strip(verts, uverts, "graphics/spaceship.png")
