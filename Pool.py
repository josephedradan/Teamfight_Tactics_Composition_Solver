"""
3/30/2020

Purpose:
    Abstract Pool for Pool type objects

"""
import json


class Pool:

    def __init__(self, path):
        """
        Parent class for pool type classes
        :param path: json file
        """
        self.path_json = path

    def get_list_from_json_file(self):
        """
        Read the json file
        :return: None
        """
        with open(self.path_json, "r") as file:
            temp_list = json.load(file)
            return temp_list
