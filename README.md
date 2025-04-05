# Flake Maker

**Flake Maker** is a simulation/game where you can observe and control the growth of a snowflake, watching it branch and expand over time. By adjusting environmental factors such as humidity and temperature, you can influence its branching patterns, and overall complexity.

You can use the pygame implementation to watch it grow live, generate a complete one from a seed with `randomSeed.py`, or just make your own implementation.

Experiment with different settings to see how changes can produce unique and beautiful snowflakes!

I aimed to mimic real-world crystal formation, drawing inspiration from the work of Dr. Ukichiro Nakaya and Dr. Ken Libbrecht. You can learn more about snowflakes [here](https://www.snowcrystals.com/science/science.html)!


### Features

- **Branch Crossing**:  When enabled, radial branches can overlap or cross each other.
- **Max Branching**:  Set a maximum number of branching events.
- **Age Coloring**: Each branch's color represents it's "age" (remaining growth potential).


## Tips

- **Lower humidity** encourages branch formation.
- **Temperature** controls water diffusion, influencing how humidity affects inner branches.
- **Higher temperatures** can create thicker branches.
- Refer (`EvolutionGraph.png`) for a detailed growth graph showing where each condition is met.


## How to use

### Web Version

If you want to try the game in a web browser, I have used [*pygbag*](https://github.com/pygame-web/pygbag) to compile the game to WebAssembly and it's available on **itch.io**.
I don't believe the screenshot feature works there, but everything else seemed fine.

[Flake Maker on itch.io](https://jutier.itch.io/flake-maker)

### Locally

1. Clone the repository and navigate to the project directory:
	```bash	
	git clone https://github.com/Jutier/Flake-Maker.git
	cd flakemaker
	```

2. Create a virtual environment (optional but recommended):
	```bash
	python -m venv env
	source env/bin/activate # On Windows: env\Scripts\activate
	```

3. Install the required packages:
	```bash
	pip install -r requirements.txt
	```

4. Run the PyGame implementation:
	```bash
	python main.py
	```


#### Controls

- **↑ / ↓** – Increase / decrease **humidity**  
- **→ / ←** – Increase / decrease **temperature**  
- **R** – Restart the snowflake  
- **S** – Save a screenshot  
- **Space** – Pause or resume growth

**Settings**: All settings can be customized ***only*** in the `settings.json` file.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
