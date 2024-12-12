import random
from abc import abstractmethod, ABC

from constants import MAX_ENERGY, MAX_LIFE, GROWING, AGING, MAX_GROUP

from cells import Cell
from groups import Pride, Herd


class Entity(ABC):
    @abstractmethod
    def live_first_phase_of_a_day(self):
        """
        Abstract method for the first phase of a day in the entity's life.
        This method should be implemented by subclasses.
        """
        pass

    @classmethod
    def name(cls):
        """
        Return the name of the entity class.
        This method is a class method that can be accessed without an instance.
        """
        return cls.__name__.lower()


class Vegetebob(Entity):
    def __init__(self, spawn_cell: Cell, density: int = 5):
        """
        Initialize a Vegetebob entity with a given density in the specified spawn cell.
        """
        self.density = density
        self.current_cell = spawn_cell
        self.surrounding_vegetebobs = None

        self.__add_to_cell(spawn_cell)
        self.__add_to_world_population_data()

    def __add_to_cell(self, cell: Cell):
        """
        Add the Vegetebob entity to the specified cell's population.
        """
        cell.population[self.name()].add(self)
        self.current_cell = cell
        cell.trigger_appeal_evaluation()

    def __add_to_world_population_data(self):
        """
        Add the Vegetebob entity to the world's population data.
        """
        if self not in self.current_cell.world.population[self.name()]:
            self.current_cell.world.population[self.name()].add(self)

    def __str__(self):
        """
        Return a string representation of the Vegetebob entity.
        """
        return f"Vegetob: Density - {self.density}"

    def __grow(self):
        """
        Increase the density of the Vegetebob entity.
        The density can grow up to a maximum value of 100.
        """
        if self.density < 100:
            self.density += GROWING
            self.current_cell.trigger_appeal_evaluation()

    def __get_surrounding_vegetebobs(self):
        """
        Get the surrounding Vegetebob entities in neighboring cells.
        """
        surrounding_vegetebobs = []
        for cell in self.current_cell.get_surrounding_cells():
            if len(cell.population["vegetebob"]) != 0:
                surrounding_vegetebobs.append(list(cell.population["vegetebob"])[0])

        self.surrounding_vegetebobs = surrounding_vegetebobs

    def __overwhelm(self):
        """
        Check if the Vegetebob entity overwhelms neighboring cells.
        If all surrounding Vegetebobs have a density of 100, remove animals from the current cell.
        """
        if self.surrounding_vegetebobs is None:
            self.__get_surrounding_vegetebobs()
        if all(vegetebob.density == 100 for vegetebob in self.surrounding_vegetebobs):
            for animal in self.current_cell.population["erbast"].union(self.current_cell.population["carviz"]):
                del animal

    def live_first_phase_of_a_day(self):
        """
        Execute the first phase of a day in the life of the Vegetebob entity.
        This phase involves growth and overwhelming of neighboring cells.
        """
        self.__grow()
        self.__overwhelm()


class Animal(Entity):
    def __init__(self, spawn_cell: Cell):
        """
        Initialize an Animal entity with a random initial state in the specified spawn cell.
        """
        self.deleted = False

        self.current_cell: Cell | None = None
        self.current_group = None

        self.energy = random.randint(1, MAX_ENERGY)
        self.lifetime = random.randint(1, MAX_LIFE)
        self.social_attitude = random.uniform(0, 1)
        self.age = 0

        self.__add_to_cell(spawn_cell)
        self.__add_to_world_population_data()

    def __add_to_world_population_data(self):
        """
        Add the Animal entity to the world's population data.
        """
        if self not in self.current_cell.world.population[self.name()]:
            self.current_cell.world.population[self.name()].add(self)

    def __remove_from_world_population_data(self):
        """
        Remove the Animal entity from the world's population data.
        """
        self.current_cell.world.population[self.name()].remove(self)

    def __remove_from_current_cell(self):
        """
        Remove the Animal entity from its current cell's population.
        """
        self.current_cell.population[self.name()].remove(self)
        self.current_cell.trigger_appeal_evaluation()

    def __add_to_cell(self, cell: Cell):
        """
        Add the Animal entity to the specified cell's population.
        """
        cell.population[self.name()].add(self)
        self.current_cell = cell
        cell.trigger_appeal_evaluation()

    def remove_from_current_group(self):
        """
        Remove the Animal entity from its current group.
        """
        if self.current_group is not None:
            self.current_group.individuals.remove(self)
            self.current_group = None

    def _add_to_group(self, target_group):
        """
        Add the Animal entity to the specified group.
        """
        self.current_group = target_group
        target_group.individuals.add(self)

    def get_best_cell_in_neighborhood(self):
        """
        Get the best cell in the neighborhood for the Animal entity.
        By default, the best cell is the current cell. The Animal iterates through neighboring cells
        and if there is a cell with greater appeal, the best_cell variable is reassigned.
        :return: The Cell object with the greatest appeal for the given species
        """
        best_cell: Cell = self.current_cell

        for cell in self.current_cell.get_surrounding_cells():
            # Animals prefer to stay in the current cell due to energy, therefore if
            if best_cell is self.current_cell:
                best_cell_appeal = best_cell.appeal[self.name()] + 50
            else:
                best_cell_appeal = best_cell.appeal[self.name()]

            if cell.appeal[self.name()] >= best_cell_appeal and cell.cell_type != "water":
                best_cell = cell

        return best_cell

    def move(self, target_cell: Cell):
        """
        Move the Animal entity to the target cell, consuming energy in the process.
        """
        self.energy -= 1
        self.__remove_from_current_cell()
        self.__add_to_cell(target_cell)

    def __increase_age(self):
        """
        Increase the age of the Animal entity and reduce energy due to aging.
        """
        self.age += 1
        if self.age % 10 == 0:
            self.energy -= AGING

    def decide_to_move(self):
        """
        Decide whether the Animal entity should move to a better cell in its neighborhood.
        The decision is based on energy level and the availability of a better cell.
        :return: True if the Animal entity decides to move, False otherwise
        """
        self.get_best_cell_in_neighborhood()
        if self.energy < 4:
            return False
        # If there is no better cell in the neighborhood, the Animal stays in the current cell.
        # Additionally, if the best cell is the current cell, the Animal also stays.
        return False if self.get_best_cell_in_neighborhood == self.current_cell else True

    def __spawn_offspring(self):
        """
        Spawn offspring for the Animal entity.
        If the current group has fewer members than the maximum allowed group size,
        the Animal can spawn offspring.
        """
        if len(self.current_group.individuals) < MAX_GROUP:
            self.__class__(self.current_cell)

    def __die_from_lifetime(self):
        """
        Handle the death of the Animal entity due to reaching its maximum lifetime.
        Spawn offspring and delete the entity.
        """
        self.__spawn_offspring()
        self.__spawn_offspring()
        self.delete()

    def __live_spawn_phase(self):
        """
        Execute the spawn phase in the life of the Animal entity.
        If the entity has reached its maximum lifetime, it dies and spawns offspring.
        If the energy level is below 1, the entity dies.
        """
        if self.age >= self.lifetime:
            self.__die_from_lifetime()
        elif self.energy < 1:
            self.delete()

    def initiate_group(self):
        """
        Abstract method for initiating a group for the Animal entity.
        This method should be overridden by subclasses.
        """
        pass

    def live_first_phase_of_a_day(self):
        """
        Execute the first phase of a day in the life of the Animal entity.
        This phase involves increasing age, initiating a group, and handling the spawn phase.
        """
        self.__increase_age()
        if self.current_group is None:
            self.initiate_group()
        self.__live_spawn_phase()

    def delete(self):
        """
        Delete the Animal entity from the simulation.
        """
        self.deleted = True
        self.__remove_from_current_cell()
        self.__remove_from_world_population_data()
        self.remove_from_current_group()


class Erbast(Animal):
    def __init__(self, spawn_cell: Cell):
        """
        Initialize an Erbast entity in the specified spawn cell.
        """
        super().__init__(spawn_cell)

    def initiate_group(self):
        """
        Initiate a group for the Erbast entity.
        Erbast entities form herds.
        """
        animals_without_group_in_current_cell = [individual for individual in self.current_cell.population[self.name()]
                                                 if individual.current_group is None]
        herd = Herd(self.current_cell, self, *animals_without_group_in_current_cell)

        for animal in animals_without_group_in_current_cell + [self]:
            animal._add_to_group(herd)

    def graze(self):
        """
        Increase the energy of the Erbast entity by 1 if there is Vegetob in the cell.
        """
        if len(self.current_cell.population["vegetebob"]) != 0:
            vegetebob_elem: Vegetebob = list(self.current_cell.population["vegetebob"])[0]
            if vegetebob_elem.density > 0:
                vegetebob_elem.density -= 1
                self.energy += 1


class Carviz(Animal):
    def __init__(self, spawn_cell: Cell):
        """
        Initialize a Carviz entity in the specified spawn cell.
        """
        super().__init__(spawn_cell)

    def initiate_group(self):
        """
        Initiate a group for the Carviz entity.
        Carviz entities form prides.
        """
        animals_without_group_in_current_cell = [individual for individual in self.current_cell.population[self.name()]
                                                 if individual.current_group is None]
        pride = Pride(self.current_cell, self, *animals_without_group_in_current_cell)

        for animal in animals_without_group_in_current_cell + [self]:
            animal._add_to_group(pride)


# Mapping of available entity names to their corresponding classes
available_entities = {
    "carviz": Carviz,
    "erbast": Erbast,
    "vegetebob": Vegetebob
}
