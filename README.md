# Flake Maker

**Flake Maker** is a simulation game where you can observe and control the growth of a snowflake, watching it branch and expand over time. By adjusting environmental factors such as humidity and temperature, you can influence its branching patterns, and overall complexity.

Experiment with different settings to see how changes can produce unique and beautiful snowflakes!

I aimed to mimic real-world crystal formation, drawing inspiration from the work of Dr. Ukichiro Nakaya and Dr. Ken Libbrecht. You can learn more about snowflakes [here](https://www.snowcrystals.com/science/science.html)!

## Controls

- **↑ / ↓** – Increase / decrease **humidity**  
- **→ / ←** – Increase / decrease **temperature**  
- **R** – Restart the snowflake  
- **S** – Save a screenshot  
- **Space** – Pause or resume growth


## Tips

- **Lower humidity** encourages branch formation.
- **Temperature** controls water diffusion, influencing how humidity affects inner branches.
- **Higher temperatures** can create thicker branches.
- Refer (`EvolutionGraph.png`) for a detailed growth graph showing where each condition is met.
- Pause anytime to fine-tune parameters and control the snowflake’s growth.


## Bugs & Features

The whole code is here for you! If you feel like it, give it a try and change the [`Snowflake.updateBranch()`](flake.py#L273) method. It's complicated at best but manageable.

I've tried to fix everything I could find, but at some point, I don't know what is a bug and what is a feature.


### Features

- **Branch Crossing**: Enable or disable in the settings. When enabled, radial branches can overlap or cross each other, adding complexity.
- **Max Branching**:  Set a maximum number of branch events in the settings. This should help prevent performance issues.
- **Age Coloring**: Each branch's color represents it's "age" (remaining growth potential).
- **UI Customization**: Almost every UI element can be easily customized through the settings, including colors, fonts, and sizes.
- **Settings**: All settings can be customized ***only*** in the `settings.json` file.


### Bugs

Occasionally, the snowflake may lose its radial symmetry and develop a rotational one. This happens when a parent branch dies. While this can be fixed by adjusting how branches are killed, I haven't yet found a perfect solution. For now, it adds an interesting layer of visual complexity.


## How to run

### Web Version

If you want to run the game in a web browser, I have used [*pygbag*](https://github.com/pygame-web/pygbag) to compile the game to WebAssembly and it's available on **itch.io**.
I don't believe the screenshot feature works there, but everything else seemed fine.

[Flake Maker on itch.io](https://jutier.itch.io/flake-maker)

### Desktop Version

If you just want to play the game on your desktop, you can download the `exe` on the [itch.io page](https://jutier.itch.io/flake-maker)

1. Download the necessary files.
2. Ensure files are in the same directory.
	- If you'd like to save screenshots, create a folder named `Screenshots` in the same directory.
4. Run the `.exe`.

### Directly with Python

If you want to make your own changes to the game and/or run it directly with Python:

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

4. Run the game:
	```bash
	python main.py
	```


## Settings

All settings can be customized ***only*** in the `settings.json` file.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.



