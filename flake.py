import pygame as pg
from math import sin, cos, tan, pi
import json
with open('settings.json', 'r') as f:
	s = json.load(f)


class Line:

	cycles = 0
	timeLeft = 500

	def __init__(self, angle=0, parent=None):
		self.angle = angle
		self.parent = parent
		self.depth = Line.cycles
		try:
			self.start = self.parent.end
		except:
			self.start = (0, 0)
		self.length = 0
		self.thick = 1
		self._buildup = 0
		self.growth = 100
		self.children = []
		self.lastChild = Line.timeLeft

	@property
	def end(self):
		return (self.length*cos(self.angle) + self.start[0], -self.length*sin(self.angle)+self.start[1])

	def branch(self, snowFlake, angle=pi/3):
		Line.cycles += 1
		self.lastChild = Line.timeLeft
		NewBorns = [Line((self.angle - angle)%(2*pi), self), Line((self.angle + angle)%(2*pi), self)]
		self.children.extend(NewBorns)
		snowFlake.branch.extend(NewBorns)

	def update(self, snowFlake, humidity=0, temperature=0):
		if self.end[1] <= abs(self.end[0] * tan(pi/3)) and Line.timeLeft > 0:
			Line.timeLeft -= 1
			if self.growth > 0:
				
				if self.depth >= (temperature + 5) * (Line.cycles) / (-15):

					if humidity > 30:
						self.length += (humidity / 100) * (25+temperature) / 5
						self.growth -= 1

					else:
						if temperature < -10:
							self._buildup += -temperature*humidity

						if self._buildup > 1000:
							okToBranch = (self.lastChild - Line.timeLeft) > 50 and len(self.children) < 13 and Line.cycles < 10				
							if self.growth > 3 and okToBranch:
								angle = (5 * pi / 12) + (temperature + 20) * ((pi / 6) - (5 * pi / 12)) / 15
								self.branch(snowFlake, angle)
								self.growth -= 2
							else:
								self.thick += 0.3
								self.growth -= 0.5
							self._buildup -= 1300

			elif len(self.children) > 0:
				snowFlake.branch.remove(self)
		else:
			snowFlake.branch.remove(self)




class SnowFlake(pg.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.image = pg.Surface((500, 500))
		self.image.fill(s['Colors']['BackGround'])
		self.rect = self.image.get_rect(topleft=(0, 0))
		self.centerX = self.rect.width / 2
		self.centerY = self.rect.height / 2
		self.branch = [Line(pi/2)]

	def update(self, humidity=0, temperature=0):
		for l in self.branch:
			l.update(self, humidity, temperature)
		self.drawBranches()

	def draw(self, screen):
		screen.blit(self.image, (0,0))

	def rotatePoint(self, point, angle=pi/3):
		x, y = point
		rotX = (x * cos(angle)) - (y * sin(angle))
		rotY = (x * sin(angle)) + (y * cos(angle))
		return (rotX + self.centerX, rotY + self.centerY)

	def drawBranches(self):
			for line in self.branch:
				for i in range(6):
					pg.draw.line(self.image, s['Colors']['SnowFlake'], self.rotatePoint(line.start, i*pi/3), self.rotatePoint(line.end, i*pi/3), int(line.thick))