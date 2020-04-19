"""
3/21/2020

Purpose:
    The attribute given to a Champion

Reference:
    DataSet
        https://developer.riotgames.com/docs/tft#match-history_best-practices

"""


class Trait:
    def __init__(self, dict_trait: dict):
        """
        TFT Trait from the dict on that trait from the json file
        :param dict_trait: dict about the trait in the json file
        """
        self.key = ""  # type: str
        self.name = ""  # type: str
        self.description = ""  # type: str
        self.innate = ""  # type: str
        self.type = ""  # type: str

        self.list_divisions = []
        self.list_dict_divisions = {}

        self._load_initial_information(dict_trait)

    def _load_initial_information(self, dict_trait):
        """
        Given a dict of a TFT trait fill in the appropriate champion information

        :param dict_trait: dict based on the json file
        :return: None
        """
        self.key = dict_trait.get("key", "")
        self.name = dict_trait.get("name", "")
        self.description = dict_trait.get("description", "")
        self.innate = dict_trait.get("innate", "")
        self.type = dict_trait.get("type", "")
        self.list_dict_divisions = dict_trait.get("sets", [])

        for set_division in dict_trait["sets"]:  # type: dict
            for key, value in set_division.items():

                # Former ["min", "max"]
                if any(True for i in ["min"] if key == i):
                    self.list_divisions.append(value)

        self.list_divisions.sort()
