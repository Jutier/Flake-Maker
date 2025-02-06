"""
Flake Maker by Jutier
Version: v1

This script generates a graph showing the regions where each condition is met.
It provides a better understanding of the update method.
"""
from utils import interp
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('dark_background')

# Define the range of temperature and humidity values
temperatures = np.linspace(-20,-5, 100) 
humidities = np.linspace(0, 100, 100)   

# Create a 2D grid for temperature and humidity
T, H = np.meshgrid(temperatures, humidities)
# Calculate the growth multiplier for each combination of temperature and humidity
G = interp(T, -5, -20, 0, 0.3) + interp(H, 0, 100, 0, 0.7)

# Calculate the reference line for humidity
humidity_line = -4 * temperatures
# Calculate the line for the branch angle
angle_line = interp(temperatures, -10, -20, 30, 60)


mesh = plt.pcolormesh(T, H, G, cmap='YlGnBu', vmin=0, vmax=1)
plt.colorbar(mesh, label='Growth Multiplier')

plt.plot(temperatures, humidity_line, color='#2AB6E8', linewidth=2, label='H = -4 * T')
plt.plot(temperatures, angle_line, color='#9de800', linewidth=2, label='Branch Angle')

# Create a mask for the branch condition and plot its contour
branchMask = (G < 0.35) & (T < -10)
plt.contour(T, H, branchMask, colors='#fc3063', linewidths=2)
plt.text(-15, 10, 'Branch', color='#fc3063', fontsize=16)

# Create a mask for the thick condition and plot its contour
thickMask = (G > 0.3) & (H < 50) & (H > -4*T)
plt.contour(T, H, thickMask, colors='#0a329b', linewidths=2)
plt.text(-10, 42, 'Thick', color='#0a329b', fontsize=16)

plt.xlabel('Temperature (°C)')
plt.ylabel('Humidity (%) / Angle (°)')
plt.title('Snowflake Evolution (update method)')
plt.legend()
plt.show()