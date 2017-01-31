from math import sin, cos
from scene import Vector2, Vector3

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
