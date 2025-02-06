"""
Flake Maker by Jutier
Version: v1

This module provides some usefull functions for other modules.
"""
from math import sin, cos

def interp(value, original_min, original_max, target_min, target_max):
	
	"""
	Interpolate a value from one range to another.

	Args:
		value (float): The value to be interpolated.
		original_min (float): The minimum value of the original range.
		original_max (float): The maximum value of the original range.
		target_min (float): The minimum value of the target range.
		target_max (float): The maximum value of the target range.

	Returns:
		float: The interpolated value in the target range.
	"""
	return target_min + (value - original_min) * (target_max - target_min) / (original_max - original_min)

def rotatePoints(points, center, angle):
	"""
	Rotate a list of points around a center point by a given angle.

	Args:
		points (list of tuple): A list of (x, y) points to be rotated.
		center (tuple): The (x, y) coordinates of the center point.
		angle (float): The angle of rotation in radians.

	Returns:
		list of tuple: The list of rotated (x, y) points.
	"""
	rotPoints = []
	cX, cY = center
	for point in points:
		x, y = point
		rotX = ((x - cX) * cos(angle)) + ((y - cY) * sin(angle))
		rotY = -((x - cX) * sin(angle)) + ((y - cY) * cos(angle))
		rotPoints.append((rotX + cX, rotY + cY))
	return rotPoints