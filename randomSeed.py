# Flake Maker by Jutier
# Version: v1.2

# This module generates snowflakes based on seeds,
# can be used to replicated a snowflake or make a collage with multiple random snowflakes.

import flake
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
		salt (bool): If True, a random salt is appended to the seed before hashing. Default is False.

	Returns:
		str: The resulting SHA256 hash in hexadecimal format.
	"""
	encoded_seed = str(seed).encode() # Convert the seed to bytes
	if salt:
		encoded_seed += urandom(16)
	sha = hashlib.sha256(encoded_seed).hexdigest()
	return sha

def evoVal(hex_list, target_min, target_max):
	"""
	Maps a list of hexadecimal values to a range of values between target_min and target_max.

	Args:
		hex_list (list of str): A list of hexadecimal strings to map.
		target_min (float): The minimum value of the target range.
		target_max (float): The maximum value of the target range.

	Returns:
		list of float: A list of values mapped to the specified range.
	"""
	evo_list = []
	for n_16 in hex_list:
		n = int(n_16, 16) # Convert hex string to integer
		value = interp(n, 0, 15, target_min, target_max)
		evo_list.append(round(value, 3))
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
	A subclass of Snowflake that adds functionality to draw lines on the canvas.
	"""

	def drawLine(self, line, points):
		"""
		Draws a line on the canvas from the specified points and line properties.

		Args:
			line (object): The line object containing color and thickness information.
			points (tuple of tuple): The start and end points of the line to be drawn.
		"""
		self.canva.line(points, fill=line.color, width=int(line.thick)*2)



def FlakeFromHash(sha, size):
	"""
	Generates a flake image based on a SHA256 hash. 

	Args:
		sha (str): The SHA256 hash used to generate the flake.
		size (int): The size of the resulting flake image.

	Returns:
		PIL.Image: The generated flake image, with hash steganography.
	"""
	evoH = evoVal(sha[:32], 0, 100) # Extract the first 32 hex characters for humidity evolution
	evoT = evoVal(sha[32:], -20, -5) # Extract the last 32 hex characters for temperature evolution
	Flake = PillowFlake((size/2, size/2), 1, 20, 9, True, "#2ab6e8", "#c0c4cf")

	image = Image.new(mode='RGB', size=(size, size), color='#282923')
	canva = ImageDraw.Draw(image)
	Flake.canva = canva # Assign the canvas to the PillowFlake object

	for h, t in zip(evoH, evoT):
		Flake.update(h, t, 1)

	Flake.drawBranches()

	steg_image = hash2Img(image, sha) # Embed the hash into the image

	return steg_image

def FlakeCollage(seed, size, N):
	"""
	Generates a collage of flake images based on a seed. Each flake is generated from a hash derived 
	from the seed, and the resulting images are arranged in a grid.

	Args:
		seed (str): The input seed used to generate the hashes.
		size (int): The size of each individual flake image.
		N (int): The number of flakes along one dimension of the collage (grid size).

	Returns:
		PIL.Image: The collage of flake images.
	"""
	collage = Image.new(mode='RGB', size=(size*N, size*N), color=None)

	for i in range(N):
		for j in range(N):
			flakeimg = FlakeFromHash(hashSeed(seed, False), size)
			collage.paste(flakeimg, (size*i, size*j))

	return collage

def readCollage(image, N, flakes):
	"""
	Extracts the hashes from a collage of flake images by reading the hash embedded in each flake image.

	Args:
		image (PIL.Image): The collage image from which to extract the hashes.
		N (int): The number of flakes along one dimension of the collage (grid size).
		flakes (list of int): A list of positions (1, N) representing the wanted flakes.

	Returns:
		list of str: A list of extracted SHA256 hashes.
	"""
	hashList = []
	size = int(image.size[0] / N) # Calculate the size of each flake image

	for p in flakes:
		pos = (((p - 1) % N) * size, ((p - 1) // N) * size) # Calculate the position of the current flake in the collage
		sha = img2Hash(image, pos)
		hashList.append(sha)
	return hashList
