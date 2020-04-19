"""
3/22/2020

Purpose:
    Pool of attributes

"""
from Teamfight_Tactics_Composition_Solver.Pool import Pool
from Teamfight_Tactics_Composition_Solver.Trait import Trait


class TraitPool(Pool):
    def __init__(self, path):
        """
        Trait pool containing all the TFT traits
        :param path: path to the json file of the TFT traits
        """
        super().__init__(path)

        self.dict_trait_pool = {}  # type: dict[str, Trait]

        self._add_traits()

    def _add_traits(self):
        """
        Get the trait dicts from json file and make trait objects from those trait dicts
        :return: None
        """
        list_traits = super().get_list_from_json_file()

        for dict_given in list_traits:
            self.add_traits(Trait(dict_given))

    def add_traits(self, trait: Trait):
        """
        Add trait object to the trait pool
        :param trait:
        :return:
        """
        self.dict_trait_pool[trait.name] = trait
