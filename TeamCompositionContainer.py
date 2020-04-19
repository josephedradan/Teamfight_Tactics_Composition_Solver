"""
3/22/2020

Purpose:
    Container for A TFT team composition combination

"""
from collections import defaultdict
from typing import Dict, Tuple

from Teamfight_Tactics_Composition_Solver.ChamptionPool import ChampionPool


class TeamCompositionContainer:
    __slots__ = ['tuple_team_composition',
                 'dict_trait_count',
                 'dict_trait_count_discrete',
                 'dict_trait_count_discrete_difference'
                 ]

    def __init__(self, tuple_team_composition: Tuple[str]):
        """
        Container for a TFT team composition combination

        :param tuple_team_composition: TFT team composition
        """
        # Tuple of the given team composition combination
        self.tuple_team_composition = tuple_team_composition  # type: Tuple[str]

        """
        Dict of the traits and the synergy count
        defaultdict sets the initial value of the key to 0
        """
        self.dict_trait_count = defaultdict(int)  # type: Dict[str, int]

        """
        Dict of the traits and the discrete synergy count
        defaultdict sets the initial value of the key to 0
        """
        self.dict_trait_count_discrete = defaultdict(int)  # type: Dict[str, int]

        # Dict of the traits and the difference between
        self.dict_trait_count_discrete_difference = {}  # type: Dict[str, int]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        string = "{}\n{}\n{}".format(self.tuple_team_composition,
                                     self.dict_trait_count,
                                     self.dict_trait_count_discrete)

        return string

    def get_trait_count_discrete_total(self):
        """
        Return the sum of the dict_trait_count_discrete
        :return:
        """
        return sum(value for key, value in self.dict_trait_count_discrete.items())
