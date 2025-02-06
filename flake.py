"""
Flake Maker by Jutier
Version: v1

This module manages the growth of snowflakes using a branching algorithm.
"""
from math import sin, cos, tan, pi, degrees
from utils import rotatePoints, interp
import json
import pygame

# Load settings from a JSON file
try:
	with open('settings.json', 'r') as f:
		s = json.load(f)
		WINDOW_WIDTH = s['Window']['Width']
		WINDOW_HEIGHT = s['Window']['Height']
		YOUNG_COLOR = pygame.Color(s['Snowflake']['Colors']['Young'])
		OLD_COLOR = pygame.Color(s['Snowflake']['Colors']['Old'])
		BACKGROUNG_COLOR = s['Snowflake']['Colors']['BackGround']
		MAX_GROWTH = s['Snowflake']['MaxGrowth']
		INITIAL_THICKNESS = s['Snowflake']['Thick']
		BRANCH_CROSSING = s['Snowflake']['BranchCrossing']
		MAX_CYCLES = s['Snowflake']['MaxBranching']
except (FileNotFoundError, PermissionError) as e:
	print(f"Error loading settings: {e}")
	raise

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
		self.thick = INITIAL_THICKNESS
		self.buildup = 0
		self.growth = MAX_GROWTH
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
		depthReq = self.snowflake.cycles < MAX_CYCLES
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


	def rotate(self, center, angle=pi/3):
		"""
		Rotate the line segment around a center point.

		Args:
			center (tuple): The center point to rotate around.
			angle (float, optional): The angle to rotate by. Defaults to pi/3.

		Returns:
			list: The rotated points.
		"""
		return rotatePoints((self.start, self.end), center, angle)


	def colorGradient(self, value):
		"""
		Calculate the color gradient based on the line's age.

		Args:
			value (float): The value to interpolate.

		Returns:
			tuple: The interpolated color.
		"""
		r = int(interp(value, 0, MAX_GROWTH, OLD_COLOR[0], YOUNG_COLOR[0]))
		g = int(interp(value, 0, MAX_GROWTH, OLD_COLOR[1], YOUNG_COLOR[1]))
		b = int(interp(value, 0, MAX_GROWTH, OLD_COLOR[2], YOUNG_COLOR[2]))
		return (r, g, b)


	def drawLine(self, points=None):
		"""
		Actually draws the line segment from two points, if no points are passed, 'self.start' and 'self.end' are used.

		Args:
			points (tuple, optional): The start and end points of the line. Defaults to None.
		"""
		if not points:
			points = (self.start, self.end)
		p0, p1 = points
		pygame.draw.line(self.snowflake.image, self.color, p0, p1, int(self.thick))


	def draw(self, angle=pi/2):
		"""
		Draw the line segment and its mirrored counterparts, 'angle' refers to the whole branch.
		Radial symmetry is established here with the angle from parents.

		Args:
			angle (float, optional): The branch angle. Defaults to pi/2.
		"""
		line = self
		self.drawLine(self.rotate(self.snowflake.center, angle))
		cousins = [(self.start, self.end)]

		dad = line.parent
		while dad:
			newCousins = []
			rotation = (dad.angle - line.angle) * 2
			for cousin in cousins:
				newCousin = rotatePoints(cousin, line.start, rotation)
				newCousins.append(newCousin)
				self.drawLine(rotatePoints(newCousin, self.snowflake.center, angle))
			cousins.extend(newCousins)
			line = dad
			dad = line.parent


	def draw_recursive(self, angle=0, cousins=None):
		"""
		Draw the line segment and its mirrored counterparts, 'angle' refers to the whole branch.
		Radial symmetry is established here with the angle from parents.

		This is the same as '.draw', but recursively.
		This method isn't used, but I decided to keep it here because it took me a lot of time to write both of them and it made me proud.

		Args:
			angle (float, optional): The branch angle. Defaults to 0.
			cousins (list, optional): List of cousin line segments. Defaults to None.
		"""
		if cousins is None:
			cousins = [(self.start, self.end)]
			self.drawLine(self.rotate(self.snowflake.center, angle))

		dad = self.parent
		if dad:
			newCousins = []
			rotation = (dad.angle - self.angle) * 2

			for cousin in cousins:
				newCousin = rotatePoints(cousin, self.start, rotation)
				newCousins.append(newCousin)
				self.drawLine(rotatePoints(newCousin, self.snowflake.center, angle))
			cousins.extend(newCousins)
			dad.draw_recursive(angle, cousins)





class Snowflake(pygame.sprite.Sprite):
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

	def __init__(self):
		"""Initialize a new Snowflake."""
		super().__init__()
		self.image = pygame.Surface((WINDOW_WIDTH, WINDOW_WIDTH))
		self.image.fill(BACKGROUNG_COLOR)
		self.rect = self.image.get_rect(topleft=(0, 0))
		self.center = (self.rect.width / 2, self.rect.height / 2)

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
			if BRANCH_CROSSING or -l.end[1] >= abs(l.end[0] * tan(pi/3)): # This should prevent lines from growing outside the cone.
				self.updateBranch(l, humidity, temperature, dt)
			else:
				self.purge(l)
		self.drawBranches()

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


		elif len(branch.children) > 0:
			self.purge(branch)

	def draw(self, screen):
		"""
		Display the snowflake on the given screen.

		Args:
			screen (Surface): The screen to draw the snowflake on.
		"""
		screen.blit(self.image, (0,0))

	def drawBranches(self):
		"""
		Draw each branche of the snowflake six times.
		The six-fold radial symmetry is forced due to the symmetry of the molecule.
		"""
		for line in self.branch:
			for i in range(6):
				line.draw(i*pi/3)

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