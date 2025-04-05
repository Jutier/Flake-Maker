# Flake Maker by Jutier
# Version: v1.2

# This module manages the growth of snowflakes using a branching algorithm.

from math import sin, cos, tan, pi, degrees
from utils import rotatePoints, interp
import json


class Line:
	"""
	Represents a line segment in the snowflake structure.

	Attributes:
		snowflake (Snowflake): The parent snowflake object.
		angle (float): The angle of the line segment.
		parent (Line): The parent line segment.
		depth (int): The 'depth' of the line in the snowflake (it's reversed).
		start (tuple): The starting point of the line segment.
		length (float): The length of the line segment.
		thick (float): The thickness of the line segment.
		buildup (float): Accumulated buildup for branching.
		growth (float): Remaining growth potential.
		children (list): List of child line segments.
		lastChild (float): Time of the last child creation.
	"""


	def __init__(self, snowflake, angle=0, parent=None):
		"""
		Initialize a new line segment.

		Args:
			snowflake (Snowflake): The parent snowflake object.
			angle (float, optional): The angle of the line segment. Defaults to 0.
			parent (Line, optional): The parent line segment. Defaults to None.
		"""
		self.snowflake = snowflake
		self.angle = angle
		self.parent = parent
		try:
			self.depth = self.parent.depth + 1
		except:
			self.depth = 0
		try:
			self.start = self.parent.end
		except:
			self.start = (0, 0)
		self.length = 0
		self.thick = self.snowflake.min_thick
		self.buildup = 0
		self.growth = self.snowflake.max_growth
		self.children = []
		self.lastChild = self.snowflake.elapsedTime

	@property
	def color(self):
		"""Changes the line color according to it's age/growth."""
		return self.colorGradient(self.growth)

	@property
	def end(self):
		return (self.length*cos(self.angle) + self.start[0], -self.length*sin(self.angle)+self.start[1])


	def okToBranch(self, temperature):
		"""
		Check if the line segment can branch.

		This validation is determined based on several conditions:
		- Time since the last child was created.
		- Number of children the current line has.
		- Depth of the current line in the snowflake structure.
		- Current temperature.
		- Remaining growth potential of the line.

		Args:
			temperature (float): The current temperature.

		Returns:
			bool: True if the line can branch, False otherwise.
		"""
		timeReq = (self.snowflake.elapsedTime - self.lastChild) > 1
		childReq = len(self.children) < (8 - self.depth)
		depthReq = self.snowflake.cycles < self.snowflake.max_cycles
		tempReq = temperature <= -10
		growReq = self.growth > 1
		return (timeReq and childReq and depthReq and tempReq)


	def branch(self, angle=pi/3):
		"""
		Create a new child Line branching from this line.

		Args:
			angle (float, optional): The angle at which to branch. Defaults to pi/3.
		"""
		self.snowflake.cycles += 1
		self.lastChild = self.snowflake.elapsedTime
		NewBorns = Line(self.snowflake, (self.angle - angle)%(2*pi), self)
		self.children.append(NewBorns)
		self.snowflake.branch.append(NewBorns)


	def colorGradient(self, value):
		"""
		Calculate the color gradient based on the line's age.

		Args:
			value (float): The value to interpolate.

		Returns:
			tuple: The interpolated color.
		"""
		MAX_GROWTH = self.snowflake.max_growth
		OLD_COLOR = self.snowflake.color_old
		YOUNG_COLOR = self.snowflake.color_young
		r = int(interp(value, 0, MAX_GROWTH, OLD_COLOR[0], YOUNG_COLOR[0]))
		g = int(interp(value, 0, MAX_GROWTH, OLD_COLOR[1], YOUNG_COLOR[1]))
		b = int(interp(value, 0, MAX_GROWTH, OLD_COLOR[2], YOUNG_COLOR[2]))
		return (r, g, b)


	def draw(self, angle=pi/2):
		"""
		Draw the line segment and its mirrored counterparts, 'angle' refers to the whole branch.
		Radial symmetry is established here with the angle from parents.

		Args:
			angle (float, optional): The branch angle. Defaults to pi/2.
		"""

		cousins = [(self.start, self.end)]
		self.snowflake.drawLine(self, rotatePoints(cousins[0], self.snowflake.center, angle))

		line = self
		dad = line.parent
		while dad:
			newCousins = []
			rotation = (dad.angle - line.angle) * 2
			for cousin in cousins:
				newCousin = rotatePoints(cousin, line.start, rotation)
				newCousins.append(newCousin)
				self.snowflake.drawLine(self, rotatePoints(newCousin, self.snowflake.center, angle))
			cousins.extend(newCousins)
			line = dad
			dad = line.parent





class Snowflake():
	"""
	Represents a snowflake in the simulation, extending from pygame.sprite.Sprite.
	Manages the Line objects in '.branch' attribute.

	Attributes:
		image (Surface): The surface on which the snowflake is drawn.
		rect (Rect): The rectangle defining the snowflake's position.
		center (tuple): The center point of the snowflake.
		branch (list): List of Line objects in the snowflake.
		cycles (int): Counts the number of branch events that have occurred.
		elapsedTime (float): The elapsed time since the Snowflake was created.
	"""

	def __init__(self, center, thickness, growth, max_cycles, branch_crossing, color_young, color_old):
		"""Initialize a new Snowflake."""
		self.color_young = color_young if isinstance(color_young, (tuple, list)) else tuple(int(color_young[i:i+2], 16) for i in (1, 3, 5))
		self.color_old = color_old if isinstance(color_old, (tuple, list)) else tuple(int(color_old[i:i+2], 16) for i in (1, 3, 5))

		self.min_thick = thickness
		self.max_growth = growth
		self.max_cycles = max_cycles
		self.branch_crossing = branch_crossing

		self.center = center

		self.cycles = 0
		self.elapsedTime = 0

		self.branch = [Line(self, pi/2)]
		self.branch[0].start = self.center



	def update(self, humidity, temperature, dt):
		"""
		Update all of the the snowflake's current branches individually and draws them.

		Args:
			humidity (float): The current humidity.
			temperature (float): The current temperature.
			dt (float): The time delta since the last update.
		"""
		self.elapsedTime += dt
		currentBranch = self.branch

		for l in currentBranch:
			if self.branch_crossing or -l.end[1] >= abs(l.end[0] * tan(pi/3)): # This should prevent lines from growing outside the cone.
				self.updateBranch(l, humidity, temperature, dt)
			else:
				self.purge(l)


	def updateBranch(self, branch, humidity, temperature, dt):
		"""
		Update one individual branch based on the parameters.

		This functions is a bit convoluted, for a better understandment of how it works check 'EvolutionGraph.png'

		Args:
			branch (Line): The branch to update.
			humidity (float): The current humidity.
			temperature (float): The current temperature.
			dt (float): The time delta since the last update.
		"""
		if branch.growth > 0:
			if branch.depth >= interp(temperature, -5, -20, -1, 3*self.cycles/4):
				growthInterp = (interp(humidity, 0, 100, 0, 0.7) + interp(temperature, -5, -20, 0, 0.3))
				branch.length += 20 * growthInterp * dt
				branch.growth -= 1 * dt

				if growthInterp < 0.35 and branch.okToBranch(temperature):
					branch.buildup += 2 * dt
					if branch.buildup >= 4:
						angle = interp(temperature, -10, -20, pi/6, pi/3)
						branch.branch(angle)
						branch.buildup = 0
						branch.growth -= 0.2 * dt

				elif growthInterp > 0.3 and humidity > -4 * (temperature) and humidity < 50:
					branch.thick += 0.4 * dt
					branch.growth -= 0.1 * dt



	def drawBranches(self):
		"""
		Draw each branche of the snowflake six times.
		The six-fold radial symmetry is forced due to the symmetry of the molecule.
		"""
		for line in self.branch:
			for i in range(6):
				line.draw(i*pi/3)



	def drawLine(self, line, points):
		"""
		The "drawLine" method must be implemented by a subclass.

		Please implement: drawLine(self, line: Line, points: Tuple[Tuple[float, float], Tuple[float, float]])
		This method is called inside of Line.draw.
		It should be implemented to draw a line.
		The rest of the snowflake drawing process is handled elsewhere.

		Args:
			line (Line): Line object that made the original call, can be used to get color, thickness, etc.
			points (tuple): The start and end points of the line to be drawn.
		"""
		raise NotImplementedError('The "drawLine" method must be implemented by a subclass.\nPlease implement: drawLine(self, line: Line, points: Tuple[Tuple[float, float], Tuple[float, float]])')


	def purge(self, line):
		"""
		Remove a branch from the snowflake.
		It was made to optimize resources, it needs improvements.

		Args:
			line (Line): The branch to remove.
		"""
		self.branch.remove(line)
		for c in line.children:
			c.parent = None
		del(line)