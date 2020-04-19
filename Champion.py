"""
3/22/2020

Purpose:
    A Champion container for TFT

Reference:
    DataSet
        https://developer.riotgames.com/docs/tft#match-history_best-practices

"""
from typing import List


class Champion:
    def __init__(self, dict_champion: dict, index_dict_position: int):
        """
        Champion object that stores information about the champion in TFT given dict of that champion

        :param dict_champion: dict information of the champion
        :param index_dict_position: index of that champion in the dict of all the champions given from ChampionPool
        """
        # Recall that python dict after 3.6 are insertion ordered
        self.index_dict_position = index_dict_position

        self.name = ""  # type: str
        self.champion_id = ""  # type: str
        self.cost = 0  # type: int
        self.list_traits = []  # type: List[str]

        # Lowercase name and no special characters to
        self.name_simple = ""  # type: str

        self._load_information(dict_champion)

    def _load_information(self, dict_champion):
        """
        Given a dict of a TFT champion fill in the appropriate champion information

        :param dict_champion: dict based on the json file
        :return: None
        """
        self.name = dict_champion["name"]
        self.champion_id = dict_champion["championId"]
        self.cost = dict_champion["cost"]
        self.list_traits = dict_champion["traits"]

        self.name_simple = self.name.replace("'", "").replace("`", "").replace(" ", "").lower()

    def __str__(self):
        """
        String representation of the champion object
        :return: None
        """
        string = "{}".format(self.name)

        return string

    def __repr__(self):
        """
        String representation of the champion object
        :return: None
        """
        return self.__str__()

    def __hash__(self):
        """
        Hash of the this object based on the champion name
        :return:
        """
        return hash(self.name)

    def __lt__(self, other):
        if isinstance(other, Champion):
            return self.cost < other.cost

        if isinstance(other, int):
            return self.self.cost < other.cost

        if isinstance(other, str):
            return self.name < other.name

    def __le__(self, other):
        if isinstance(other, Champion):
            return self.cost <= other.cost

        if isinstance(other, int):
            return self.self.cost <= other.cost

        if isinstance(other, str):
            return self.name <= other.name

    def __eq__(self, other):
        if isinstance(other, Champion):
            return self.__hash__() == other.__hash__()

    def __ne__(self, other):
        if isinstance(other, Champion):
            return self.__hash__() == other.__hash__()

    def __gt__(self, other):
        if isinstance(other, Champion):
            return self.cost > other.cost

        if isinstance(other, int):
            return self.self.cost > other.cost

        if isinstance(other, str):
            return self.name > other.name

    def __ge__(self, other):
        if isinstance(other, Champion):
            return self.cost >= other.cost

        if isinstance(other, int):
            return self.self.cost >= other.cost

        if isinstance(other, str):
            return self.name >= other.name
