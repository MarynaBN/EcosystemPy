from constants import WATER_COLOR, GROUND_COLOR, NUMCELLS_R


class Cell:
    world = None

    # Mapping of cell types to colors
    cell_type_handler = {
        "water": WATER_COLOR,
        "ground": GROUND_COLOR,
    }

    def __init__(self, x, y, cell_type):
        self.x = x
        self.y = y
        self.cell_type = cell_type  # water or ground
        self.appeal = {
            "carviz": 0,
            "erbast": 0
        }
        self.population = {  # Population of species in the cell
            "vegetebob": set(),
            "erbast": set(),
            "carviz": set(),
        }
        self.groups = {  # Social groups in the cell
            "herd": set(),
            "pride": set()
        }
        self.__surrounding_cells = []  # Cache for surrounding cells

    def __int__(self):
        return self.cell_type_handler[self.cell_type]

    def __str__(self):
        return f"{self.cell_type}"

    def trigger_appeal_evaluation(self) -> None:
        """
        Evaluate the appeal of the cell based on the population of species in the cell.
        The appeal determines the desirability of the cell for species movement.

        ASSUMPTION: Inspired by sid meier's civilization.
        """

        # Reset the appeal values
        self.appeal["erbast"] = 0
        self.appeal["carviz"] = 0

        # Each point of vegetob's density adds 1 point of erbast appeal
        if len(self.population["vegetebob"]) != 0:
            vegetebob_elem = list(self.population["vegetebob"])[0]
            self.appeal["erbast"] += vegetebob_elem.density

        # Each erbast's individual removes 10 points of prey appeal and adds 50 points for predator appeal
        self.appeal["erbast"] -= len(self.population["erbast"]) * 10
        self.appeal["carviz"] += len(self.population["erbast"]) * 50

        # Each carviz's individual removes 25 points from prey appeal and 10 from predator appeal
        self.appeal["erbast"] -= len(self.population["carviz"]) * 25
        self.appeal["carviz"] -= len(self.population["carviz"]) * 10

    @classmethod
    def available_cell_types(cls):
        # Returns a list of available cell types
        return list(cls.cell_type_handler.keys())

    @classmethod
    def assign_to_world(cls, world):
        # Assigns the world object to the Cell class
        cls.world = world

    def __get_surrounding_coordinates(self):
        # Returns a list of eight neighboring coordinates in a 2D grid
        x = self.x
        y = self.y

        surrounding_coordinates = [(nx, ny) for nx in range(x - 1, x + 2) for ny in range(y - 1, y + 2)
                                   if 0 <= nx < NUMCELLS_R and 0 <= ny < NUMCELLS_R and (nx, ny) != (x, y)]
        return surrounding_coordinates

    def get_surrounding_cells(self):
        # Returns the surrounding cells of the current cell
        if len(self.__surrounding_cells) == 0:
            self.__surrounding_cells = [self.world.cells_grid[coord[0], coord[1]] for coord in
                                        self.__get_surrounding_coordinates()]
        return self.__surrounding_cells
