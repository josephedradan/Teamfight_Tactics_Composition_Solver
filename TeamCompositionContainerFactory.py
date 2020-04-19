"""
3/21/2020

Purpose:
    Find all the team composition combinations for Teamfight Tactics for League of legends and their respective


"""
from typing import List, Iterable

from Teamfight_Tactics_Composition_Solver.ChamptionPool import ChampionPool
from Teamfight_Tactics_Composition_Solver.TeamCompositionContainer import TeamCompositionContainer
from Teamfight_Tactics_Composition_Solver.TraitPool import TraitPool
from josephs_resources.Decorators.V2.Timer import timer


class TeamCompositionContainerFactory:

    def __init__(self, champion_pool: ChampionPool, trait_pool: TraitPool):
        """
        Factory to make team composition combinations

        :param champion_pool: champion pool object
        :param trait_pool: trait pool object
        """
        self.champion_pool = champion_pool  # type: ChampionPool

        self.trait_pool = trait_pool  # type: TraitPool

    def get_team_composition_container(self, list_composition_combination: Iterable[str]) -> TeamCompositionContainer:
        """
        Get an object of TeamCompositionContainer given list_composition_combination

        :param list_composition_combination: list of champions in the team composition
        :return: an object of the TeamCompositionContainer type
        """
        team_composition_container = TeamCompositionContainer(
            tuple(list_composition_combination))  # type: TeamCompositionContainer

        for champion_name in list_composition_combination:
            champion_object = self.champion_pool.dict_champion_pool_name.get(champion_name)

            """
            For each trait in champion_object, add that trait to team_composition_container, if it doesn't exist in
            the dict then add it to the dict and assign it a value of 0
            """
            for trait in champion_object.list_traits:
                """
                If key is not in the dict then add it to the dict and assign it a value of 0.
                
                from collections import defaultdict
                defaultdict(int) disregards the code below, it's inside of the TeamCompositionContainer
                """
                # if team_composition_container.dict_trait_count.get(trait, False) is False:
                #     team_composition_container.dict_trait_count[trait] = 0
                #     team_composition_container.dict_trait_count_discrete[trait] = 0

                team_composition_container.dict_trait_count[trait] += 1

                trait_object = self.trait_pool.dict_trait_pool.get(trait)

                """
                FOR OPTIMIZATION 4
                Add a few seconds and space in calculation
                """
                # for i in reversed(range(len(trait_object.list_divisions))):
                #     if team_composition_container.dict_trait_count[trait] >= trait_object.list_divisions[i]:
                #         team_composition_container.dict_trait_count_discrete[trait] = trait_object.list_divisions[i]
                #         if len(trait_object.list_divisions) == i + 1:
                #             team_composition_container.dict_trait_count_discrete_difference[trait] = 0
                #         else:
                #             team_composition_container.dict_trait_count_discrete_difference[trait] = \
                #                 trait_object.list_divisions[i + 1] - team_composition_container.dict_trait_count[trait]
                #         break

                """
                USED FOR ANYTHING THAT ISN'T OPTIMIZATION 4
                SLIGHTLY FASTER, no team_composition_container.dict_trait_count_discrete_difference[trait]
                """
                for trait_division in trait_object.list_divisions:
                    if team_composition_container.dict_trait_count[trait] >= trait_division:
                        team_composition_container.dict_trait_count_discrete[trait] = trait_division

        return team_composition_container

    def sort_tuple_team_composition(self, tuple_team_composition: iter) -> tuple:
        """
        Sort given team composition by unit cost

        :param tuple_team_composition:
        :return: None
        """

        # Slightly faster optimization
        if not isinstance(tuple_team_composition, list):
            tuple_team_composition = list(tuple_team_composition)

        tuple_team_composition.sort(
            key=lambda champion_name: (
                self.champion_pool.dict_champion_pool_name.get(champion_name).name_simple,
                self.champion_pool.dict_champion_pool_name.get(champion_name).cost,
            )
        )
        return tuple(tuple_team_composition)

    # TODO: NOT USED
    # @timer(show_arguments=False)
    def get_list_all_team_composition_containers(self, list_list_composition_combination: List[List[tuple]]) -> List[
        TeamCompositionContainer]:
        """
        Get a list of TeamCompositionContainer objects based on list_list_composition_combination
        :return: None
        """

        list_all_team_composition_containers = []
        for list_composition_combination in list_list_composition_combination:
            list_all_team_composition_containers.append(
                self.get_team_composition_container(list_composition_combination))

        return list_all_team_composition_containers

    def get_tuple_team_composition_transformed_integer(self, tuple_team_composition: tuple):
        return tuple([self.champion_pool.dict_champion_pool_name[champion_name].index_dict_position for champion_name in
                     tuple_team_composition])

    def get_tuple_team_composition_transformed_name(self, tuple_team_composition_transformed_integer: tuple):
        return tuple([self.champion_pool.dict_champion_pool_index_dict_position[integer].name for integer in
                     tuple_team_composition_transformed_integer])
