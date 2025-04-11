# Flake Maker by Jutier
# Version: v2

# This module generates snowflakes based on seeds or hashes.

import hashlib
from utils import interp
import numpy as np
from flake import Snowflake
from PIL import Image, ImageDraw
from os import urandom

def hashSeed(seed, salt=False):
	"""
	Generates a SHA256 hash from a given seed. Optionally adds a random salt to the seed before hashing.

	Args:
		seed (str or int): The input seed to generate the hash.
		salt (bool): If True, a random salt is added to the seed before hashing. Default is False.

	Returns:
		str: The resulting SHA256 hash in hexadecimal format.
	"""
	encoded_seed = str(seed).encode() # Convert the seed to bytes
	if salt:
		encoded_seed += urandom(16)
	sha = hashlib.sha256(encoded_seed).hexdigest()
	return sha

def evoVal(hex_string, target_min, target_max, decimal=3):
	"""
	Maps hexadecimal values to a range of values between target_min and target_max.
	Interprets each character in the given string as a separate hexadecimal value.

	Args:
		hex_string (str):  A string of hexadecimal characters, each representing a separate hexadecimal value.
		target_min (float): The minimum value of the target range.
		target_max (float): The maximum value of the target range.
		decimal (int): The number of decimal places to round the result. Defaults to 3.

	Returns:
		list of float: A list of values mapped to the specified range.
	"""
	evo_list = []
	for n_16 in hex_string:
		n = int(n_16, 16) # Convert hex string to integer
		value = interp(n, 0, 15, target_min, target_max)
		evo_list.append(round(value, decimal))
	return evo_list

def hash2Img(image, sha):
	"""
	Embeds a SHA256 hash into an image by modifying the least significant bit (LSB) of the
	red and green channels of the image with the corresponding bits from the hash.

	Args:
		image (PIL.Image): The input image to embed the hash into.
		sha (str): The SHA256 hash to embed into the image (in hexadecimal format).

	Returns:
		PIL.Image: The image with the embedded hash.
	"""
	pixels = np.array(image)
	lin, col = 0, 0
	bin_sha = bin(int(sha, 16))[2:].zfill(256) # Convert the SHA hash to a 256-bit binary string

	for i in range(0, len(bin_sha), 2):
		r, g, b = pixels[lin, col]

		r = (r & 0xfe) | int(bin_sha[i], 2)
		g = (g & 0xfe) | int(bin_sha[i+1], 2)

		pixels[lin, col] = [r, g, b]

		col += 1

	return Image.fromarray(pixels)

def img2Hash(image, pos):
	"""
	Extracts a 256-bit SHA256 hash from an image starting at the specified pixel position by reading the 
	least significant bit (LSB) of the red and green channels.

	Args:
		image (PIL.Image): The input image from which to extract the hash.
		pos (tuple): A tuple (lin, col) representing the starting pixel coordinates.

	Returns:
		str: The extracted SHA256 hash in hexadecimal format.
	"""
	pixels = np.array(image)
	lin, col = pos
	extracted_bin = 0

	for i in range(128):
		r, g, _ = pixels[lin, col]

		#Extract the LSB of red and green channels, int conversion for size
		extracted_bin = int(extracted_bin << 2) | int((r & 1) << 1) | int(g & 1)

		col += 1

	hex_hash = hex(extracted_bin)[2:].zfill(64)

	return hex_hash



class PillowFlake(Snowflake):
	"""
	A subclass of Snowflake that implements drawLine method and adds some attributes.

	Attributes:
		image (PIL.Image): The image for the snowflake.
		imgDraw (ImageDraw): The drawing context for the image.
	"""
	def __init__(self, **kwargs):
		"""
		Initializes a PillowFlake object with specified parameters.

		Args:
			size (int): The size of the resulting image. Defaults to 700.
			bg_color (str): The background color of the image. Defaults to '#282923'.
			**kwargs: Additional parameters passed to the parent class Snowflake.
		"""

		# Using pop is preferable over an optional parameter,
		# it allows passing the value from distant functions.
		size = kwargs.pop('size', 700)
		bg_color = kwargs.pop('bg_color', '#282923')

		default_params = {
			'thickness': 1,
			'growth': 20,
			'max_cycles': 9,
			'branch_crossing': True,
			'color_young': '#2ab6e8',
			'color_old': '#c0c4cf'
		}

		default_params.update(kwargs)
		center = (size/2, size/2)

		super().__init__(center, **default_params)
		self.image = Image.new(mode='RGB', size=(size, size), color=bg_color)
		self.imgDraw = ImageDraw.Draw(self.image)



	def drawLine(self, line, points):
		"""
		Draws a line on the canvas from the specified points and line properties.

		Args:
			line (object): The Line object containing color and thickness information.
			points (tuple of tuple): The start and end points of the line to be drawn.

		Returns:
			None: This method modifies the image directly and does not return any value.
		"""
		self.imgDraw.line(points, fill=line.color, width=int(line.thick)*2)



def flakeFromHash(sha, dt=1, **kwargs):
	"""
	Generates a flake image based on a SHA256 hash.
	The used hash is embedded to the image with steganography.

	Args:
		sha (str): The SHA256 hash used to generate the flake.
		dt (float): Delta used for the evolution. Values outside the range (0, growth) may result in unintended behavior. Defaults to 1.
		**kwargs: Additional parameters passed to the PillowFlake class.

	Returns:
		PIL.Image: The generated flake image, with steganography.
	"""
	evoH = evoVal(sha[:32], 0, 100) # Extract the first 32 hex characters for humidity evolution
	evoT = evoVal(sha[32:], -20, -5) # Extract the last 32 hex characters for temperature evolution

	Flake = PillowFlake(**kwargs)

	for h, t in zip(evoH, evoT):
		Flake.update(h, t, dt)

	Flake.drawBranches()

	steg_image = hash2Img(Flake.image, sha) # Embed the hash into the image

	return steg_image

def flakeCollage(N, **kwargs):
	"""
	Generates a collage of N flakes.
	Makes N hashes that are passed to collageFromHashList.

	Args:
		N (int): The desired number of flakes on the collage.
		**kwargs: Additional parameters passed to the collageFromHashList function.

	Returns:
		PIL.Image: The collage of flakes.
	"""
	hash_list = [hashSeed('random', True) for _ in range(N)]

	return collageFromHashList(hash_list, **kwargs)

def collageFromHashList(hash_list, **kwargs):
	"""
	Creates a collage from a list of hashes, arranging the flakes in a grid.
	If there aren't enough hashes to fill the grid, random flakes will be used.

	Args:
		hash_list (list): A list of hashes used to generate the flakes.
		**kwargs: Additional parameters, such as rows, columns, size or others passed to the flakeFromHash function.

	Returns:
		PIL.Image: The collage of flakes.
	"""
	N = len(hash_list)
	ceil = lambda n: -1 * int(-1 * n // 1) # Rounds up given number
	rows = kwargs.get('rows', ceil(N**(1/2))) # I believe this is a great default
	columns = kwargs.get('columns', rows)
	size = kwargs.get('size', 700)

	collage = Image.new(mode='RGB', size=(size*columns, size*rows), color=None)

	h = 0
	complete = True
	for i in range(rows):
		for j in range(columns):
			if h < N:
				flakeimg = flakeFromHash(hash_list[h], **kwargs)
			else:
				flakeimg = flakeFromHash(hashSeed('random', True), **kwargs)
				complete = False
			collage.paste(flakeimg, (size*j, size*i))
			h += 1
	if not complete:
		print(f"The collage couldn't be filled with the provided hashes. {h - N} flakes were randomly generated.")

	return collage

def readFlakes(image, **kwargs):
	"""
	Extracts the hashes from a flake or a collage by reading the hash embedded in each flake.

	Args:
		image (PIL.Image): The collage image from which to extract the hashes.
		columns (int): The number of flake columns on the collage.
		flakes (list): A list of The desired flakes  positions (row-wise, starting from 1).

	Returns:
		list: A list of extracted SHA256 hashes.
	"""
	columns = kwargs.get('columns', 1)
	flakes = kwargs.get('flakes', [1])

	hashList = []
	size = int(image.size[0] / columns) # Calculate the size of each flake image

	for p in flakes:
		pos = (((p - 1) // columns) * size, ((p - 1) % columns) * size) # Calculate the position of the current flake in the collage
		sha = img2Hash(image, pos)
		hashList.append(sha)
	return hashList



def main():
	"""
	This function handles the CLI logic.
	Performs actions such as reading from an image, generating
	snowflakes from a seed or hash file, and saving or displaying the results.

	CLI Arguments:
		--seed: Desired seed to generate the flake.
		--rows: Number of rows in the image.
		--columns: Number of columns in the image.
		--hashes: File with hashes for the collage.
		--save: File to save the output, either an image or flakes.
		-r/--read: Read snowflakes from the given image.
		--flakes: Desired flakes to read from the collage.

	Example usage:
		python script.py --rows 5 --columns 5 --save output.png
		python script.py --read input.png --save output.txt
	"""
	import argparse

	parser = argparse.ArgumentParser(
		description='Generates a Snowflake from a seed or hash file, can also read hashes from an image.'
	)

	parser.add_argument(
		'--seed',
		metavar='SEED',
		help='Specific seed value to generate the snowflake.'
	)

	parser.add_argument(
		'--rows',
		default=1,
		type=int,
		metavar='N',
		help='Number of rows in the image.'
	)

	parser.add_argument(
		'--columns',
		default=1,
		type=int,
		metavar='N',
		help='Number of columns in the image.'
	)

	parser.add_argument(
		'--hashes',
		type=argparse.FileType('r'),
		metavar='FILE',
		help='File containing hashes for the collage (one hash per line).'
	)

	parser.add_argument(
		'--save',
		metavar='FILE',
		help='File to save the output, image or hashes (append).'
	)

	parser.add_argument(
		'-r', '--read',
		type=argparse.FileType('rb'),
		metavar='FILE',
		help='Read snowflakes from the given image file.'
	)

	parser.add_argument(
		'--flakes',
		nargs='*',
		type=int,
		metavar='N',
		help='Desired flakes to read from the collage.'
	)

	args = parser.parse_args()
	kwargs = {k: v for k, v in vars(args).items() if v} # filter None values

	if args.read: # -r/--read
		image = Image.open(args.read)
		hash_list = readFlakes(image, **kwargs)

		if args.save: # --save
			with open(args.save, 'a') as file:
				file.write('\n'.join(hash_list) + '\n')

		else:
			print(hash_list, sep='\n')

	else:
		N = (args.rows * args.columns) # --rows * --columns

		if args.hashes: # --hashes
			hash_list = args.hashes.read().splitlines()

			if N < 2:
				image = collageFromHashList(hash_list)

			else:
				image = collageFromHashList(hash_list, **kwargs)

		elif N > 1:
				image = flakeCollage(N, **kwargs)

		else:
			sha = hashSeed(args.seed, not args.seed) # --seed
			image = flakeFromHash(sha)
			print(sha)

		if args.save: # --save
			image.save(args.save)

		else:
			image.show()

if __name__ == "__main__":
	main()
