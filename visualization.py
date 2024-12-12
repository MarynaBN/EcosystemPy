import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
from world import World
from matplotlib.animation import FuncAnimation


class SimulationUI:
    def __init__(self):
        # Create the world and initialize variables
        self.world = World()
        self.world.generate()
        self.day = 0
        self.paused = True

        # Create the figure and subplots for the map and buttons
        self.fig, (self.ax_graph, self.ax_map) = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))
        plt.subplots_adjust(wspace=0.1)

        # Create the pause/continue button and connect it to the event handler
        button_ax = plt.axes([0.00, 0.90, 0.15, 0.060])
        self.pause_continue_button = Button(button_ax, 'Start', color='lightgoldenrodyellow', hovercolor='0.975')
        self.pause_continue_button.on_clicked(self.pause_start)

        # Create the reset button and connect it to the event handler
        reset_button_ax = plt.axes([0.15, 0.90, 0.15, 0.060])
        self.reset_button = Button(reset_button_ax, 'Reset', color='lightgoldenrodyellow', hovercolor='0.975')
        self.reset_button.on_clicked(self.reset)

        # Display the initial world state
        self.update_map()

        # Set up the animation
        self.anim = FuncAnimation(self.fig, self.run, interval=100)

        # Data for population graph
        self.population_data = {"carviz": [], "vegetebob": [], "erbast": []}
        self.days_data = []
        self.lines = {}
        self.init_graph()

        # Show the plot
        plt.show()

    def run(self, i):
        # Animation function called for each frame
        if not self.paused:
            self.day += 1
            self.world.live_day()
            self.update_map()
            self.update_graph()

    def pause_start(self, event):
        # Event handler for pause/continue button
        self.paused = not self.paused
        if self.paused:
            self.pause_continue_button.label.set_text("Start")
        else:
            self.pause_continue_button.label.set_text("Pause")

    def reset(self, event):
        # Event handler for reset button
        self.world.generate()
        self.day = 0
        self.paused = True
        self.pause_continue_button.label.set_text("Start")
        self.update_map()
        self.init_graph()

    def update_map(self):
        # Update the map subplot with the current world state
        self.ax_map.cla()

        # Convert the Cell objects to integers
        world_int = np.vectorize(int)(self.world.cells_grid)

        # Create a colormap for water, ground, and species cells
        cmap = plt.cm.colors.ListedColormap(['blue', 'green'])

        # Plot the world grid
        self.ax_map.imshow(world_int, cmap=cmap)
        self.ax_map.axis('off')

        # Define colors for species markers
        species_colors = {
            'V': 'yellow',
            'E': 'black',
            'C': 'red'
        }

        # Add species markers to the cells
        for x in range(self.world.rows):
            for y in range(self.world.cols):
                cell = self.world.cells_grid[x, y]
                population = cell.population

                species_present = []
                colors_present = []

                # Determine which species are present in the cell and their colors
                for species, individuals in population.items():
                    if len(individuals) > 0:
                        species_present.append(species[0].upper() + str(len(individuals)))
                        colors_present.append(species_colors.get(species[0].upper(), 'black'))

                # Add species markers to the cell
                if len(species_present) > 0:
                    for i, species_marker in enumerate(species_present):
                        color = colors_present[i]
                        self.ax_map.text(y + (i * 0.2), x, species_marker, color=color, ha="center", va="center",
                                         fontweight="bold", fontsize=4)

        # Set the label for the current day
        self.ax_map.set_xlabel(f"day: {self.day}")

        # Redraw the figure
        self.fig.canvas.draw()

    def init_graph(self):
        # Initialize the population graph with empty data
        self.ax_graph.cla()
        self.population_data = {"carviz": [], "vegetebob": [], "erbast": []}
        self.days_data = []
        self.lines = {}
        for species in self.population_data.keys():
            line, = self.ax_graph.plot([], [], label=species)
            self.lines[species] = line
        self.ax_graph.legend()

    def update_graph(self):
        """
        Update the population graph with current data
        ASSUMPTION: Extended mechanics.
        """

        # append this day data to memory
        for species, population in self.world.population.items():
            self.population_data[species].append(len(population))
        self.days_data.append(self.day)

        # Update the lines of the population graph
        for species, line in self.lines.items():
            line.set_data(self.days_data, self.population_data[species])

        # Rescale the graph to fit the data and redraw
        self.ax_graph.relim()
        self.ax_graph.autoscale_view()
        self.fig.canvas.draw()
