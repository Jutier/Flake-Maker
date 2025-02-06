"""
Flake Maker by Jutier
Version: v1

This module provides the main game loop and user interface management for the Flake Maker application.
It includes classes and functions to initialize the game, handle user input, and update the game state.
"""
from flake import Snowflake, Line
from UI import InfoText, TextBox, Knob, BaseUI
from datetime import datetime
from math import pi
import json
import pygame
import asyncio

# Load settings from a JSON file
try:
	with open('settings.json', 'r') as f:
		s = json.load(f)
		WINDOW_WIDTH = s['Window']['Width']
		WINDOW_HEIGHT = s['Window']['Height']
		DISPLAY_WIDTH = s['UI']['ParamDisplay']['Width']
		DISPLAY_HEIGHT = s['UI']['ParamDisplay']['Height']
		FPS = s['FPS']
except (FileNotFoundError, PermissionError) as e:
	print(f"Error loading settings: {e}")
	raise



class Game:
	"""
	Main game class to manage the Flake Maker application.

	Attributes:
		screen (pygame.Surface): The main screen surface for the game.
		clock (pygame.time.Clock): Clock object to manage the frame rate.
		running (bool): Flag to control the game loop.
		stopGrowth (bool): Flag to control the snowflake growth.
		snowflake (Snowflake): The snowflake object.
		temperature (float): The current temperature in the game.
		humidity (int): The current humidity in the game.
		_UIElements (list): List of UI elements to be drawn.
	"""
	def __init__(self):
		"""Initialize the Game object."""
		pygame.init()
		pygame.display.set_caption('Flake Maker')
		pygame.display.set_icon(pygame.image.load('icon.png'))

		self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		self.clock = pygame.time.Clock()

		self.running = True
		self.stopGrowth = False

		self.snowflake = Snowflake()

		self.temperature = -12.5
		self.humidity = 50

		self._createUI()

	def _createUI(self):
		"""Create and initialize the UI elements for the game."""
		ECCENTRICITY = WINDOW_HEIGHT - WINDOW_WIDTH
		KNOB_RADIUS = ECCENTRICITY * 0.3
		KNOB_PADDING_X = KNOB_RADIUS + 20
		KNOB_PADDING_Y = WINDOW_HEIGHT - ECCENTRICITY/2
		DISPLAY_PADDING_X = KNOB_PADDING_X + ECCENTRICITY * 0.3 + 10 + DISPLAY_WIDTH / 2
		DISPLAY_PADDING_Y = WINDOW_HEIGHT - (ECCENTRICITY) / 2

		self._ui_box = BaseUI(WINDOW_WIDTH/2, KNOB_PADDING_Y, WINDOW_WIDTH, ECCENTRICITY)

		self._cycles_text = InfoText(WINDOW_WIDTH/2, WINDOW_WIDTH + 35, 'Branch: VAR', self.snowflake.cycles)
		self._time_text = InfoText(WINDOW_WIDTH/2, WINDOW_WIDTH + 55, 'Time: VAR', round(self.snowflake.elapsedTime, 1))

		self._hmdt_box = TextBox(DISPLAY_PADDING_X, DISPLAY_PADDING_Y, DISPLAY_WIDTH, DISPLAY_HEIGHT, 'Humidity: VAR%', self.humidity)
		self._hmdt_knob = Knob(KNOB_PADDING_X, KNOB_PADDING_Y, KNOB_RADIUS)

		self._temp_box = TextBox(WINDOW_WIDTH - DISPLAY_PADDING_X, DISPLAY_PADDING_Y, DISPLAY_WIDTH, DISPLAY_HEIGHT, 'Temp: VARºC', self.temperature)
		self._temp_knob = Knob(WINDOW_WIDTH - KNOB_PADDING_X, KNOB_PADDING_Y, KNOB_RADIUS)
   
		self._UIElements = [self._ui_box, self._time_text, self._cycles_text, self._hmdt_box, self._hmdt_knob, self._temp_box, self._temp_knob]


	def tempChange(self, value):
		"""
		Change the temperature and update the temperature display.

		Args:
			value (float): The amount to change the temperature by.
		"""
		self.temperature += value
		self._temp_box.text = '{0:>2.1f}'.format(self.temperature)
		self._temp_knob.angle -= pi / 18 * value / abs(value)

	def hmdtChange(self, value):
		"""
		Change the humidity and update the humidity display.

		Args:
			value (float): The amount to change the humidity by.
		"""
		self.humidity += value
		self._hmdt_box.text = '{0:>3.0f}'.format(self.humidity)
		self._hmdt_knob.angle -= pi / 12 * value / abs(value)

	def screenShot(self):
		"""Save a screenshot of the snowflake in the /Screenshots directory with date and time."""
		time = datetime.now()
		fileName = time.strftime("Screenshots/Snowflake_%d-%m-%y_%H-%M-%S.png")
		pygame.image.save(self.snowflake.image, fileName)

# Async function needed to use WebAssembly and run on browser with pygbag
async def main(game):
	"""
	Main game loop to handle events, update the game state, and draw the screen.

	Args:
		game (Game): The Game object managing the game state.
	"""
	while game.running:
		dt = game.clock.tick(FPS) / 1000
		keys_pressed = pygame.key.get_pressed()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				game.running = False

			elif event.type == pygame.KEYDOWN:

				if event.key == pygame.K_SPACE:
					game.stopGrowth = not game.stopGrowth 

				elif event.key == pygame.K_r:
					for line in game.snowflake.branch:
						game.snowflake.purge(line)
					del game.snowflake
					game.snowflake = Snowflake()

				elif event.key == pygame.K_s:
					game.screenShot()


		if keys_pressed[pygame.K_RIGHT]:
			if game.temperature < -5:
				game.tempChange(1 * dt)
		if keys_pressed[pygame.K_LEFT]:
			if game.temperature > -20:
				game.tempChange(-1 * dt)
		if keys_pressed[pygame.K_UP]:
			if game.humidity < 100:
				game.hmdtChange(10 * dt)
		if keys_pressed[pygame.K_DOWN]:
			if game.humidity > 0:
				game.hmdtChange(-10 * dt)

		if not game.stopGrowth:
			game.snowflake.update(game.humidity, game.temperature, dt)

		game.snowflake.draw(game.screen)

		game._cycles_text.text = game.snowflake.cycles
		game._time_text.text = round(game.snowflake.elapsedTime, 1)

		for element in game._UIElements:
			element.draw(game.screen)
		
		pygame.display.update()

		await asyncio.sleep(0)

	pygame.quit()

if __name__ == '__main__':
	GAME = Game()
	asyncio.run(main(GAME))