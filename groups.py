from __future__ import annotations
from typing import TYPE_CHECKING

from random import choices

if TYPE_CHECKING:
    from species import Animal, Erbast, Carviz  # Importing type hints for type checking
    from cells import Cell


class Group:
    all_groups = []  # A list to store all the group instances

    def __init__(self, initiation_cell, *individuals: Animal | Erbast | Carviz):
        self.deleted = False  # Flag to mark if the group is deleted
        self.individuals = set(individuals)  # Set to store the individuals in the group
        self.all_groups.append(self)  # Add the group to the list of all groups
        initiation_cell.groups[self.name()].add(self)  # Add the group to the cell's group set
        self.current_cell: Cell = initiation_cell  # Current cell where the group is located

    def remove_from_current_cell(self):
        if self in self.current_cell.groups[self.name()]:
            self.current_cell.groups[self.name()].remove(
                self)  # Remove the group from the cell's group set

    def add_to_target_cell(self, cell: Cell):
        cell.groups[self.name()].add(self)  # Add the group to the target cell's group set
        self.current_cell = cell  # Update the current cell of the group

    def set_current_cell(self):
        self.remove_from_current_cell()  # Remove the group from the current cell
        updated_current_cell = list(self.individuals)[
            0].current_cell  # Get the current cell of any individual in the group
        self.add_to_target_cell(updated_current_cell)  # Add the group to the current cell of the individual

    def decide_to_move(self):
        individual_votes = [individual.decide_to_move() for individual in self.individuals]

        # if half or more individuals decide to move, group moves
        if individual_votes.count(True) >= len(individual_votes) / 2:
            return True
        else:
            return False

    def join(self, other_group):
        self.individuals.union(other_group.individuals)  # Merge the individuals from the other group into this group
        other_group.delete()  # Delete the other group

    def movement(self):
        if not self.decide_to_move():
            return False

        best_cell_in_neighborhood = list(self.individuals)[
            0].get_best_cell_in_neighborhood()  # Get the best cell to move

        for individual in list(self.individuals):
            if individual.energy == 1:
                individual.remove_from_current_group()  # Remove the individual from the group if energy is 1
                continue
            individual.move(best_cell_in_neighborhood)  # Move the individual to the best cell

        self.set_current_cell()  # Update the current cell of the group
        return True

    def delete(self, kill_individuals=False):
        self.deleted = True

        if kill_individuals:
            for individual in list(self.individuals):
                individual.delete()  # Delete the individual if specified
        else:
            for individual in list(self.individuals):
                individual.remove_from_current_group()  # Remove the individual from the group

        self.all_groups.remove(self)  # Remove the group from the list of all groups
        self.remove_from_current_cell()  # Remove the group from the current cell

    def delete_if_no_members(self):
        if len(self.individuals) <= 0:
            self.delete()  # Delete the group if it has no members
            return True
        else:
            return False

    def live_day(self):
        # to be overridden by child classes
        pass

    @classmethod
    def name(cls):
        """
        Return the name of the entity class.
        This method is a class method that can be accessed without an instance.
        """
        return cls.__name__.lower()


class Herd(Group):
    def __init__(self, initiation_cell, *individuals: Erbast):
        super().__init__(initiation_cell, *individuals)

    def grazing(self):
        for individual in self.individuals:
            individual.graze()  # Perform grazing action for each individual in the herd

    def join_all(self):
        for group in list(self.current_cell.groups[self.__class__.__name__.lower()]):
            if group is self:
                continue
            self.join(group)  # Merge with other herds in the same cell

    def live_day(self):
        if self.delete_if_no_members() or self.deleted is True:
            return
        self.join_all()
        if self.movement():
            return
        self.grazing()


class Pride(Group):
    def __init__(self, initiation_cell, *individuals: Carviz):
        super().__init__(initiation_cell, *individuals)

    def get_average_social_attitude(self):
        if len(self.individuals) <= 0:
            return 0
        return sum(carviz.social_attitude for carviz in self.individuals) / len(self.individuals)

    def try_join_all(self):
        for pride in list(self.current_cell.groups[self.__class__.__name__.lower()]):
            if pride is self or pride.get_average_social_attitude() < 0.5 or self.get_average_social_attitude() < 0.5:
                continue
            self.join(pride)  # Merge with other prides in the same cell

    def initiate_fight(self):
        prides_pool = {}
        for pride in self.current_cell.groups[self.__class__.__name__.lower()]:
            prides_pool[pride] = sum(carviz.energy for carviz in pride.individuals)

        prides = list(prides_pool.keys())
        weights = list(prides_pool.values())
        winner = choices(prides, weights=weights, k=1)[0]  # Randomly select a pride based on their energy sum

        for pride in prides:
            if pride is not winner:
                pride.delete(kill_individuals=True)  # Delete the losing prides and kill the individuals

    def find_strongest_erbast(self) -> Erbast:
        strongest_erbast_instance = max(self.current_cell.population["erbast"], key=lambda instance: instance.energy)
        return strongest_erbast_instance  # Find the strongest Erbast instance in the cell

    def hunt(self):
        victim = self.find_strongest_erbast()  # Find the strongest Erbast in the cell

        received_energy = victim.energy
        energy_per_carviz = received_energy / len(self.individuals)

        for carviz in self.individuals:
            carviz.energy += energy_per_carviz  # Distribute the energy among the Carviz individuals

        victim.delete()  # Delete the hunted Erbast

    def live_day(self):
        if self.delete_if_no_members() or self.deleted:
            return
        self.try_join_all()
        if self.movement():
            return
        if len(self.current_cell.groups[self.name()]) > 1:
            self.initiate_fight()  # Initiate a fight among multiple prides in the same cell
        if self.deleted:
            return
        if len(self.current_cell.population["erbast"]) > 0:
            self.hunt()  # Hunt the strongest Erbast in the cell
