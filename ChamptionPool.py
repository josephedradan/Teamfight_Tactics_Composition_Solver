"""
3/22/2020

Important Note:
    Recall that python dict after 3.6 are insertion ordered and use memory

Purpose:
    Champion pool for the Champion objects
"""
from typing import Dict

from Teamfight_Tactics_Composition_Solver.Champion import Champion
from Teamfight_Tactics_Composition_Solver.Pool import Pool


class ChampionPool(Pool):
    def __init__(self, path):
        """
        Given a path to the champion json file make Champion objects based on that file and put them into a dict
        :param path: None
        """
        super().__init__(path)

        self.dict_champion_pool_name = {}  # type: Dict[str, Champion]

        self.dict_champion_pool_index_dict_position = {}  # type: Dict[int, Champion]

        self._add_champions()

    def _add_champions(self):
        """
        Create champion object and add it to the dict
        :return:
        """
        list_champions = super().get_list_from_json_file()

        for dict_index_position_id, dict_champion in enumerate(list_champions):
            champion_object = Champion(dict_champion, dict_index_position_id)

            self.dict_champion_pool_name[champion_object.name] = champion_object
            self.dict_champion_pool_index_dict_position[champion_object.index_dict_position] = champion_object

        # print(self.dict_champion_pool_name)
        # print(self.dict_champion_pool_index_dict_position)