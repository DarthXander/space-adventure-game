from scene import *
from ui import Path

image = "graphics/spaceship.png"

class Analysis (Scene):
	def setup(self):
		self.image = SpriteNode(Texture(image), z_position = -12, position = self.bounds.center(), parent = self)
		self.background = ShapeNode(path = Path.rect(0,0,self.image.size.w,self.image.size.h), position = self.image.position, z_position = -15, parent = self, fill_color = (1,1,1,.1))
		self.offset = Point(-50, 50)
		self.cursor = Node(parent = self)
		ShapeNode(path = Path.rect(0,0,1,20), parent = self.cursor, fill_color = (0,0,0))
		ShapeNode(path = Path.rect(0,0,20,1), parent = self.cursor, fill_color = (0,0,0))
		self.cursorlabel = LabelNode("", parent = self, position = (self.bounds.w/2.0, self.bounds.h*.9))
		self.selected = []
		self.selected_nodes = []
		self.selectbutton = ShapeNode(Path.rect(0,0,150,50), parent = self, position = (self.bounds.w*.2, self.bounds.h*.9), fill_color = (0,0,0), stroke_color = (1,1,1))
		LabelNode("Select", parent = self.selectbutton)
		
		self.printbutton = ShapeNode(Path.rect(0,0,150,50), parent = self, position = (self.bounds.w*.8, self.bounds.h*.9), fill_color = (0,0,0), stroke_color = (1,1,1))
		LabelNode("Print", parent = self.printbutton)
	def give_position(self, pos):
		pt = (self.image.point_from_scene(pos) + self.image.size/2.0)
		pt = Point(pt.x/self.image.size.w, pt.y/self.image.size.h)
		return pt
	def update_position(self, pos):
		self.cursorlabel.text = str(self.give_position(pos))
	def update(self):
		for touch in self.touches.values():
				if touch.location not in self.selectbutton.bbox and touch.location not in self.printbutton.bbox:
					self.cursor.position = touch.location + self.offset
					self.update_position(self.cursor.position)
	def touch_began(self, touch):
		if touch.location in self.selectbutton.bbox:
			self.selected.append(self.give_position(self.cursor.position))
			self.selected_nodes.append(ShapeNode(path = Path.oval(0,0,5,5), parent = self, position = self.cursor.position, z_position = -10, fill_color = (1,1,1), stroke_color = (0,0,0)))
		if touch.location in self.printbutton.bbox:
			print self.selected
run(Analysis())
