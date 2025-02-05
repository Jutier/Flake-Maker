import pygame as pg
from flake import SnowFlake
from math import pi
from UI import TextBox, RotatingCircle, BaseUI
import json

with open('settings.json', 'r') as f:
	s = json.load(f)

class Game:
	def __init__(self):

		pg.init()
		pg.display.set_caption('Flake Maker')

		self.screen = pg.display.set_mode((s['Window']['Width'], s['Window']['Height']))
		self.clock = pg.time.Clock()

		self.running = True
		self.stopGrowth = False

		self.snowFlake = SnowFlake()

		self.temperature = -12.5
		self.humidity = 50

		self.ui_box = BaseUI(0, 500, 500, 100)

		self.temp_box = TextBox(s['Window']['Width'] - 220, s['Window']['Height'] - 75, 130, 50, 'Temp: VARºC', self.temperature)
		self.temp_knob = RotatingCircle(s['Window']['Width'] - 50, s['Window']['Height'] - 50, 30)


		self.hmdt_box = TextBox(90, s['Window']['Height'] - 75, 130, 50, 'Humidity: VAR%', self.humidity)
		self.hmdt_knob = RotatingCircle(50, s['Window']['Height'] - 50, 30)

		self.UI = [self.ui_box, self.temp_box, self.temp_knob, self.hmdt_box, self.hmdt_knob]


	def tempChange(self, value):
		self.temperature += value
		self.temp_box.text = self.temperature
		self.temp_knob.angle -= pi / 18 * value / abs(value)

	def hmdtChange(self, value):
		self.humidity += value
		self.hmdt_box.text = self.humidity
		self.hmdt_knob.angle -= pi / 12 * value / abs(value)



	def main(self):
		while self.running:
			dt = self.clock.tick(5)

			for event in pg.event.get():
				if event.type == pg.QUIT:
					self.running = False

				if event.type == pg.KEYDOWN:

					if event.key == pg.K_SPACE:
						self.stopGrowth = not self.stopGrowth

					if event.key == pg.K_r:
						del self.snowFlake
						self.snowFlake = SnowFlake()

					if event.key == pg.K_RIGHT:
						if self.temperature < -5:
							self.tempChange(0.5)
					if event.key == pg.K_LEFT:
						if self.temperature > -20:
							self.tempChange(-0.5)
					if event.key == pg.K_UP:
						if self.humidity < 100:
							self.hmdtChange(5)
					if event.key == pg.K_DOWN:
						if self.humidity > 0:
							self.hmdtChange(-5)

			if not self.stopGrowth:
				self.snowFlake.update(self.humidity, self.temperature)
			self.snowFlake.draw(self.screen)
			for element in self.UI:
				element.draw(self.screen)
			pg.display.update()

		pg.quit()

if __name__ == '__main__':
	GAME = Game()
	GAME.main()