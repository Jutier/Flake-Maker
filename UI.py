"""
Flake Maker by Jutier
Version: v1

This module provides the user interface components for the Flake Maker application.
It includes classes for UI elements such as buttons, text boxes, and knobs.
"""
from math import sin, cos, pi
import json
import pygame

# Load settings from a JSON file
try:
	with open('settings.json', 'r') as f:
		s = json.load(f)
		WINDOW_WIDTH = s['Window']['Width']
		WINDOW_HEIGHT = s['Window']['Height']
		TEXT_COLOR = s['UI']['ParamDisplay']['TextColor']
		KNOB_COLOR = s['UI']['Knob']['Color']
		OUTLINE_COLOR = s['UI']['OutLineColor']
		DISPLAY_COLOR = s['UI']['ParamDisplay']['BackgroundColor']
		BASE_COLOR = s['UI']['BackgroundColor']
		DISPLAY_FONT = s['UI']['ParamDisplay']['Font']
		DISPLAY_FONT_SIZE = s['UI']['ParamDisplay']['FontSize']
		DETAILS_COLOR = s['UI']['Details']['TextColor']
		DETAILS_FONT = s['UI']['Details']['Font']
		DETAILS_FONT_SIZE = s['UI']['Details']['FontSize']
except (FileNotFoundError, PermissionError) as e:
	print(f"Error loading settings: {e}")
	raise

class BaseUI:
	"""
	Class for the UI background.

	Attributes:
		rect (pygame.Rect): The rectangle defining position and size.
	"""
	def __init__(self, centerX, centerY, width, height):
		"""
		Initialize the BaseUI element.

		Args:
			centerX (int): The x-coordinate of the center.
			centerY (int): The y-coordinate of the center.
			width (int): The width of the UI element.
			height (int): The height of the UI element.
		"""
		self.rect = pygame.Rect(centerX - width/2, centerY - height/2, width, height)

	def draw(self, screen):
		"""
		Draw the UI element on the screen.

		Args:
			screen (pygame.Surface): The screen to draw the UI element on.
		"""
		pygame.draw.rect(screen, BASE_COLOR, self.rect)
		pygame.draw.rect(screen, OUTLINE_COLOR, self.rect, 5)


class TextBox:
	"""
	Class for creating and managing text boxes.

	Attributes:
		rect (pygame.Rect): The rectangle defining the text box's position and size.
		font (pygame.font.Font): The font used for rendering text.
		_base_text (str): The base text template with a placeholder for variable values.
		_formatted_text (str): The formatted text with the variable value replaced.
	"""

	def __init__(self, centerX, centerY, width, height, text, value):
		"""
		Initialize the TextBox element.

		Args:
			centerX (int): The x-coordinate of the center of the text box.
			centerY (int): The y-coordinate of the center of the text box.
			width (int): The width of the text box.
			height (int): The height of the text box.
			text (str): The base text with a placeholder 'VAR' for variable values.
			value (str): The initial value to replace the placeholder in the text.
		"""
		self.rect = pygame.Rect(centerX - width/2, centerY - height/2, width, height)
		self.font = pygame.font.SysFont(DISPLAY_FONT, DISPLAY_FONT_SIZE)
		self._base_text = text
		self._formatted_text = self._base_text.replace('VAR', str(value))

	@property
	def text(self):
		"""Get the formatted text."""
		return self._formatted_text

	@text.setter
	def text(self, value):
		"""Set the text by replacing the placeholder with the provided value."""
		self._formatted_text = self._base_text.replace('VAR', str(value))

	def draw(self, screen):
		"""
		Draw the text box on the screen.

		Args:
			screen (pygame.Surface): The screen to draw the text box on.
		"""
		pygame.draw.rect(screen, DISPLAY_COLOR, self.rect)
		pygame.draw.rect(screen, OUTLINE_COLOR, self.rect, 4)
		text = self.font.render(self.text, True, TEXT_COLOR)
		text_rect = text.get_rect(center=self.rect.center)
		screen.blit(text, text_rect)


class Knob:
	"""
	Class for creating and managing knobs.

	Attributes:
		x (int): The x-coordinate of the knob's center.
		y (int): The y-coordinate of the knob's center.
		radius (int): The radius of the knob.
		angle (float): The angle of the knob's pointer.
	"""
	def __init__(self, x, y, radius):
		"""
		Initialize the Knob element.

		Args:
			x (int): The x-coordinate of the knob's center.
			y (int): The y-coordinate of the knob's center.
			radius (int): The radius of the knob.
		"""
		self.x = x
		self.y = y
		self.radius = radius
		self.angle = pi/2

	def draw(self, screen):
		"""
		Draw the knob on the screen.

		Args:
			screen (pygame.Surface): The screen to draw the knob on.
		"""
		# Draw the knob circles
		pygame.draw.circle(screen, KNOB_COLOR, (self.x, self.y), self.radius)
		pygame.draw.circle(screen, OUTLINE_COLOR, (self.x, self.y), self.radius, 5)

		# Calculate the positions for the pointer line
		outer_x = self.x + self.radius * cos(self.angle)
		outer_y = self.y - self.radius * sin(self.angle)
		inner_x = self.x + (self.radius - 15) * cos(self.angle)
		inner_y = self.y - (self.radius - 15) * sin(self.angle)

		# Draw the pointer line
		pygame.draw.line(screen, OUTLINE_COLOR, (outer_x, outer_y), (inner_x, inner_y), 5)


	def rotate(self, amount):
		"""
		Rotate the knob by a given amount.

		Args:
			amount (float): The amount to rotate the knob by (in radians).
		"""
		self.angle += amount
		# Modulate the angle to a (0, 2*pi) interval
		self.angle %= 2 * pi


class InfoText:
	"""
	Class for creating and managing informational text.

	Attributes:
		centerX (int): The x-coordinate of the text's center position.
		centerY (int): The y-coordinate of the text's center position.
		font (pygame.font.Font): The font used for rendering text.
		_base_text (str): The base text template with a placeholder for variable values.
		_formatted_text (str): The formatted text with the variable value replaced.
	"""
	def __init__(self, centerX, centerY, text, value):
		"""
		Initialize the InfoText element.

		Args:
			centerX (int): The x-coordinate of the text's center position.
			centerY (int): The y-coordinate of the text's center position.
			text (str): The base text with a placeholder 'VAR' for variable values.
			value (str): The initial value to replace the placeholder in the text.
		"""
		self.centerX = centerX
		self.centerY = centerY

		self.font = pygame.font.SysFont(DETAILS_FONT, DETAILS_FONT_SIZE)
		self._base_text = text
		self._formatted_text = self._base_text.replace('VAR', str(value))

	@property
	def text(self):
		"""Get the formatted text."""
		return self._formatted_text

	@text.setter
	def text(self, value):
		"""Set the text by replacing the placeholder with the provided value."""
		self._formatted_text = self._base_text.replace('VAR', str(value))

	def draw(self, screen):
		"""
		Draw the informational text on the screen.

		Args:
			screen (pygame.Surface): The screen to draw the text on.
		"""
		text = self.font.render(self.text, True, DETAILS_COLOR)
		text_rect = text.get_rect(center=(self.centerX, self.centerY))
		screen.blit(text, text_rect)