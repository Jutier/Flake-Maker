import pygame as pg
import json
from math import sin, cos, pi

with open('settings.json', 'r') as f:
	s = json.load(f)

class TextBox:
	def __init__(self, x, y, width, height, text, value):
		self.rect = pg.Rect(x, y, width, height)
		self.font = pg.font.Font(None, 24)
		self._base_text = text
		self._formatted_text = self._base_text.replace('VAR', str(value))

	@property
	def text(self):
		return self._formatted_text

	@text.setter
	def text(self, value):
		self._formatted_text = self._base_text.replace('VAR', str(value))

	def draw(self, screen):
		pg.draw.rect(screen, s['Colors']['DisplayBg'], self.rect)
		pg.draw.rect(screen, s['Colors']['OutLine'], self.rect, 4)
		text_surface = self.font.render(self.text, True, s['Colors']['Text'])
		text_rect = text_surface.get_rect(center=self.rect.center)
		screen.blit(text_surface, text_rect)

class RotatingCircle:
	def __init__(self, x, y, radius):
		self.x = x
		self.y = y
		self.radius = radius
		self.angle = pi/2

	def draw(self, screen):
		pg.draw.circle(screen, s['Colors']['Accent'], (self.x, self.y), self.radius)
		pg.draw.circle(screen, s['Colors']['OutLine'], (self.x, self.y), self.radius, 5)

		outer_x = self.x + self.radius * cos(self.angle)
		outer_y = self.y - self.radius * sin(self.angle)
		inner_x = self.x + (self.radius - 15) * cos(self.angle)
		inner_y = self.y - (self.radius - 15) * sin(self.angle)

		pg.draw.line(screen, s['Colors']['OutLine'], (outer_x, outer_y), (inner_x, inner_y), 5)


	def rotate(self, amount):
		self.angle += amount
		self.angle %= 2 * pi

class BaseUI:
	def __init__(self, x, y, width, height):
		self.rect = pg.Rect(x, y, width, height)

	def draw(self, screen):
		pg.draw.rect(screen, s['Colors']['Base'], self.rect)
		pg.draw.rect(screen, s['Colors']['OutLine'], self.rect, 5)
