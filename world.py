import numpy as np
import random

from species import Carviz, Erbast, Vegetebob
from cells import Cell
from groups import Group
from constants import NUMCELLS_R, NUMCELLS_C, MAX_CARVIZ, MAX_ERBAST, MAX_VEGETOBOB


class World:
    def __init__(self, rows: int = NUMCELLS_R, cols: int = NUMCELLS_C):
        """Initialize World with rows and cols, default to 100 each."""
        self.rows = rows
        self.cols = cols
        self.cells_grid = None
        self.population = None

    def generate(self):
        # Clear existing groups and initialize population dictionary
        Group.all_groups = []
        self.population = {
            Vegetebob.name(): set(),
            Erbast.name(): set(),
            Carviz.name(): set(),
        }

        # Create an empty grid of cells
        self.cells_grid = np.empty((self.rows, self.cols), dtype=Cell)

        """Generate the world and return a 2D array of cells."""
        Cell.assign_to_world(self)

        # Initialize each cell in the grid
        for x in range(self.rows):
            for y in range(self.cols):
                self._initialize_cell(x, y)

    def _initialize_cell(self, x: int, y: int):
        """Initialize a single cell at position (x, y)."""
        # Create water cells at the boundary
        if self._is_boundary(x, y):
            self.cells_grid[x, y] = Cell(x=x, y=y, cell_type="water")
        else:
            # Initialize other cells with a random type
            cell_type = np.random.choice(Cell.available_cell_types())
            self.cells_grid[x, y] = Cell(x=x, y=y, cell_type=cell_type)
            self._initialize_species(x, y)

    def _initialize_species(self, x: int, y: int):
        """
        Initialize a species at the cell in position (x, y).

        ASSUMPTION: Only one type of species can be spawned per cell at once.
        """
        if self.cells_grid[x, y].cell_type == "ground":
            # Determine available species to be spawned based on population limits
            available_creatures = []
            if len(self.population[Erbast.name()]) <= MAX_ERBAST:
                available_creatures.append(Erbast)
            if len(self.population[Vegetebob.name()]) <= MAX_VEGETOBOB:
                available_creatures.append(Vegetebob)
            if len(self.population[Carviz.name()]) <= MAX_CARVIZ:
                available_creatures.append(Carviz)

            if len(available_creatures) == 0:
                return

            # Randomly choose a species from the available ones and spawn an instance
            species = random.choice(available_creatures)
            species_instance = species(spawn_cell=self.cells_grid[x, y])
            self.population[species_instance.name()].add(species_instance)

    def _is_boundary(self, x: int, y: int):
        """Check if cell is on the boundary."""
        return x == 0 or x == self.rows - 1 or y == 0 or y == self.cols - 1

    def live_day(self):
        # Execute the live_first_phase_of_a_day() method for each species in each cell
        for row in self.cells_grid:
            for cell in row:
                for species in cell.population.values():
                    for instance in list(species):
                        instance.live_first_phase_of_a_day()

        # Execute the live_day() method for each group
        for group in Group.all_groups:
            group.live_day()

    def print_population_data(self):
        # Print the population data for each species
        print(self.population.keys(), [len(species) for species in self.population.values()])
