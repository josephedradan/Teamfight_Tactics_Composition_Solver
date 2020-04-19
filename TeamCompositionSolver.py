"""
3/30/2020


Purpose:
    Intermediate between the TeamCompositionContainerFactory, TeamCompositionCombinationsSearcher,
    ChampionPool, TraitPool, and SQLiteHandlerTeamCompositionSolver.

"""
import os
import pickle
from collections import defaultdict
from concurrent.futures.process import ProcessPoolExecutor
from typing import Set, FrozenSet, Tuple, List

from Teamfight_Tactics_Composition_Solver.ChamptionPool import ChampionPool
from Teamfight_Tactics_Composition_Solver.SQLiteHandlerTeamCompositionSolver import \
    SQLiteHandlerTeamCompositionSolver, _create_db_champion_tables
from Teamfight_Tactics_Composition_Solver.TeamCompositionCombinationsSearcher import \
    TeamCompositionCombinationsSearcher
from Teamfight_Tactics_Composition_Solver.TeamCompositionContainerFactory import \
    TeamCompositionContainerFactory
from Teamfight_Tactics_Composition_Solver.TraitPool import TraitPool
from Teamfight_Tactics_Composition_Solver.constants import PICKLE_SET_FROZENSET_NAME, \
    PICKLE_LIST_TUPLE_NAME
from josephs_resources.Decorators.V1.MemoryUsage import memory_usage
from josephs_resources.Decorators.V2.Timer import timer


class TeamCompositionSolver:

    def __init__(self, path_champions: str, path_traits: str):
        """
        Creates the TeamCompositionCombinationsSearcher to get the TFT team composition combinations,
        accesses the SQLiteHandlerTeamCompositionSolver and serves as the intermediate between the database and all
        other objects.

        :param path_champions: path to json file of champions
        :param path_traits: path to json file to traits of the champions
        """

        # ChampionPool object
        self.champion_pool = ChampionPool(path_champions)  # type: ChampionPool

        # TraitPool object
        self.trait_pool = TraitPool(path_traits)  # type: TraitPool

        # Print Trait and it's divisions
        for h, i in self.trait_pool.dict_trait_pool.items():
            print(i.name)
            print(i.list_divisions)

        # TeamCompositionContainerFactory object
        self.team_composition_container_factory = TeamCompositionContainerFactory(self.champion_pool,
                                                                                  self.trait_pool)  # type: TeamCompositionContainerFactory

        # TeamCompositionCombinationsSearcher object
        self.team_composition_combinations_searcher = TeamCompositionCombinationsSearcher(
            self.team_composition_container_factory)  # type: TeamCompositionCombinationsSearcher

        # SQLiteHandlerTeamCompositionSolver object
        self.sqlite_handler_team_composition_solver = SQLiteHandlerTeamCompositionSolver(
            self.team_composition_container_factory)

        # Set of frozensets that are the compositions
        self.set_frozenset_compositions_combinations = set()  # type: Set[FrozenSet]

        # List of tuples that are the compositions
        self.list_tuple_compositions_combinations = []  # type: List[Tuple]

        # Dict of champion names and the frozensets they are in
        self.dict_key_champion_name_value_frozenset = {}  # type: dict

        # Dict of champion names and a list of the indices that corresponds to the tuples they are in
        self.dict_key_champion_name_value_list_index_champion_composition = {}  # type: dict

    def create_set_frozenset_compositions_combinations_pickle(self, composition_size=9):
        """
        Ask the user if they want to run the _create_set_frozenset_compositions_combinations_pickle method
        :return:
        """
        # Ask user if they are sure they should do the operation
        user_response = input(
            "Are you sure you want to calculate all TFT team compositions set of frozensets (yes/no): ")

        # If yes
        if user_response == "yes":

            # Thread or Process Pool the callable (Will Lock up until done)
            with ProcessPoolExecutor() as executor:
                # Future of the callable
                future_callable = executor.submit(self._create_set_frozenset_compositions_combinations_pickle_helper,
                                                  composition_size)

            # Thread or Process Pool the callable (Will Ignore Lock up until done)
            # executor = ProcessPoolExecutor(1)

            # Future of the callable
            # future_callable = executor.submit(self._create_set_frozenset_compositions_combinations_pickle,
            #                                   composition_size)

            # Check if future_callable has finished
            if future_callable.done():
                print("{} has finished pickling and writing to file!".format(
                    self.create_set_frozenset_compositions_combinations_pickle.__name__))

            else:
                print("{} did not complete properly!".format(
                    self.create_set_frozenset_compositions_combinations_pickle.__name__))

        else:
            print(
                "{} has not been executed!".format(self.create_set_frozenset_compositions_combinations_pickle.__name__))

    def _create_set_frozenset_compositions_combinations_pickle_helper(self, composition_size):
        """
        Do not call this method unless you know what you are doing!

        Loads all useful TFT team compositions based on the TeamCompositionCombinationsSearcher algorithm
        Then it pickles the list of champion composition combinations into a file based on the name NAME_PICKLE_BASE

        Running this will take approximately 9 hours until complete!

        :return: None
        """
        # Simplify the callable name
        get_set_frozenset_all_compositions_combinations_callable = self.team_composition_combinations_searcher.get_set_frozenset_compositions_combinations

        # Callable's arguments
        get_set_frozenset_all_compositions_combinations_args = (
            composition_size,)  # 9 for champion composition size limit
        # get_set_frozenset_all_compositions_combinations_args = (4, ["Ahri", "Syndra", "Zoe"], "and")

        # Get the Results of the callable
        set_frozenset_all_compositions_combinations_call = get_set_frozenset_all_compositions_combinations_callable(
            *get_set_frozenset_all_compositions_combinations_args)

        # Write pickled result to file
        with open(PICKLE_SET_FROZENSET_NAME, "wb") as file:
            pickle.dump(set_frozenset_all_compositions_combinations_call, file)

    def _create_list_tuple_compositions_combinations_pickle(self, composition_size=9):
        """
        Ask the user if they want to run the _create_set_frozenset_compositions_combinations_pickle method
        :return: None
        """
        # Ask user if they are sure they should do the operation
        user_response = input("Are you sure you want to calculate all TFT team compositions list of tuples (yes/no): ")

        # If yes
        if user_response == "yes":

            # Thread or Process Pool the callable (Will Lock up until done)
            with ProcessPoolExecutor() as executor:
                # Future of the callable
                future_callable = executor.submit(self._create_pickle_list_tuple_compositions_combinations,
                                                  composition_size)

            # Thread or Process Pool the callable (Will Ignore Lock up until done)
            # executor = ProcessPoolExecutor(1)

            # Future of the callable
            # future_callable = executor.submit(self._create_tft_champion_combinations_pickle_all)

            # Check if future_callable has finished
            if future_callable.done():
                print("{} has finished pickling and writing to file!".format(
                    self._create_list_tuple_compositions_combinations_pickle.__name__))

            else:
                print("{} did not complete properly!".format(
                    self._create_list_tuple_compositions_combinations_pickle.__name__))

        else:
            print("{} has not been executed!".format(self._create_list_tuple_compositions_combinations_pickle.__name__))

    def _create_pickle_list_tuple_compositions_combinations(self, composition_size):
        """
        Do not call this method unless you know what you are doing!

        Loads all useful TFT team compositions based on the TeamCompositionCombinationsSearcher algorithm
        Then it pickles the list of champion composition combinations into a file based on the name NAME_PICKLE_BASE

        Running this will take approximately 9 hours until complete!

        :return: None
        """
        # Simplify the callable name
        get_list_tuple_all_compositions_combinations_callable = self.team_composition_combinations_searcher.get_list_tuple_compositions_combinations

        # Callable's arguments
        get_list_tuple_all_compositions_combinations_args = (composition_size,)  # 9 for champion composition size limit
        # get_list_tuple_all_compositions_combinations_args = (4, ["Ahri", "Syndra", "Zoe"], "and")

        # Get the Results of the callable
        list_tuple_all_compositions_combinations_call = get_list_tuple_all_compositions_combinations_callable(
            *get_list_tuple_all_compositions_combinations_args)

        # Write pickled result to file
        with open(PICKLE_LIST_TUPLE_NAME, "wb") as file:
            pickle.dump(list_tuple_all_compositions_combinations_call, file)

    def load_pickle_set_frozenset_compositions_combinations(self):
        """
        Loads the pickle file based on the name PICKLE_SET_FROZENSET_NAME that contains the list of TFT team composition
        combinations into self.set_frozenset_all_compositions_combinations_callable

        :return: None
        """
        try:
            with open(PICKLE_SET_FROZENSET_NAME, "rb") as file:
                set_frozenset_compositions_combinations_all = pickle.load(file)

        except FileNotFoundError as e:
            print(e)
            print("Does {} exists?".format(PICKLE_SET_FROZENSET_NAME))

        # for i in set_frozenset_compositions_combinations_all:
        #     print(i)

        self.set_frozenset_compositions_combinations = set_frozenset_compositions_combinations_all

    @timer
    @memory_usage
    def load_pickle_list_tuple_compositions_combinations(self):
        """
        Loads the pickle file based on the name PICKLE_LIST_TUPLE_NAME that contains the list of TFT team composition
        combinations into self.set_frozenset_all_compositions_combinations_callable

        :return: None
        """
        try:
            with open(PICKLE_LIST_TUPLE_NAME, "rb") as file:
                list_tuple_compositions_combinations = pickle.load(file)

        except FileNotFoundError as e:
            print(e)
            print("Does {} exists?".format(PICKLE_LIST_TUPLE_NAME))

        # for i in list_tuple_compositions_combinations:
        #     print(i)

        self.list_tuple_compositions_combinations = list_tuple_compositions_combinations

    def _transform_set_frozenset_compositions_combinations(self):
        """
        Transforms self.set_frozenset_compositions_combinations into a dict where the key is the champion name
        and the value is a set that contains the indices

        :return:
        """

        dict_temp = defaultdict(set)

        try:
            # For frozenset_given in self.set_frozenset_compositions_combinations_all
            for index, frozenset_given in enumerate(self.set_frozenset_compositions_combinations):

                # For champion_name in frozenset_given
                for champion_name in frozenset_given:

                    """
                    The below code is commented out because of the default dict
                    """
                    # # If champion_name does not exist in dict_temp
                    # if dict_temp.get(champion_name, False) is False:
                    #     # Add champion_name and set to dict_temp
                    #     dict_temp[champion_name] = set()

                    # Add frozenset_given to set based on champion_name
                    dict_temp[champion_name].add(frozenset_given)

        except Exception as e:
            print(e)
            print("Has {} been initialized?".format(self.set_frozenset_compositions_combinations))

        self.dict_key_champion_name_value_frozenset = dict_temp

    @timer
    @memory_usage
    def _transform_list_tuple_compositions_combinations_all(self):
        """
        Transforms self.list_tuple_compositions_combinations_all into a dict where the key is the champion name
        and the value is a set that contains the indices

        Memory Usage:
            Memory (Before):                                             6056.3046875 Mb
            Running Callable transform_list_tuple_compositions_combinations_all ...
            Memory (After):                                              10830.56640625 Mb
            Memory Difference:                                           4774.26171875 Mb
            Callable: TeamCompositionSolver.transform_list_tuple_compositions_combinations_all
            Callable ran in 72.66071796417236 Sec

        :return:
        """

        dict_temp = defaultdict(list)

        try:
            # For tuple_composition_combination in self.set_frozenset_compositions_combinations_all
            for index, tuple_composition_combination in enumerate(self.list_tuple_compositions_combinations):

                # For champion_name in tuple_composition_combination
                for champion_name in tuple_composition_combination:

                    """
                    The below code is commented out because of the default dict
                    """
                    # # If champion_name does not exist in dict_temp
                    # if dict_temp.get(champion_name, False) is False:
                    #     # Add champion_name and set to dict_temp
                    #     dict_temp[champion_name] = []

                    # Add tuple_composition_combination to set based on champion_name
                    dict_temp[champion_name].append(index)

        except Exception as e:
            print(e)
            print("Has {} been initialized?".format(self.list_tuple_compositions_combinations))

        self.dict_key_champion_name_value_list_index_champion_composition = dict_temp

    def get_set_frozenset_compositions_given_list_champion_names(self, iter_champion_names: iter) -> Set[FrozenSet]:
        """
        Given a iterable of champion names, get a set of frozensets containing the champions in iter_champion_names

        :param iter_champion_names: iterable of champion names
        :return: None
        """

        """
        Set containing the first frozenset in set_frozenset_compositions_iter_champion_names is iter_champion_names[0]
        """
        set_frozenset_compositions_iter_champion_names = self.dict_key_champion_name_value_frozenset.get(
            iter_champion_names[0])

        # For index in 1 to the last champion_name in iter_champion_names
        for index in range(1, len(iter_champion_names)):
            # Do the intersection of the frozensets to get the frozensets that contain all iter_champion_names
            set_frozenset_compositions_iter_champion_names = set_frozenset_compositions_iter_champion_names.intersection(
                self.dict_key_champion_name_value_frozenset.get(iter_champion_names[index]))

        return set_frozenset_compositions_iter_champion_names

    # @timer
    # @memory_usage
    # def get_list_tuple_compositions_given_list_champion_names_db(self,
    #                                                              iter_champion_names: iter,
    #                                                              team_composition_size_start=0,
    #                                                              team_composition_size_end=9) -> List[Tuple]:
    #     """
    #     Given a iterable of champion names, get a list of tuples containing the champions in iter_champion_names
    #     from the database
    #
    #     Big db file (11 GB) with slightly slower retrieval (Maybe) and less memory usage
    #
    #     Memory (Before):                                             17.01953125 Mb
    #     Running Callable get_list_tuple_compositions_given_list_champion_names_db ...
    #     Memory (After):                                              194.71484375 Mb
    #     Memory Difference:                                           177.6953125 Mb
    #     Callable: TeamCompositionSolver.get_list_tuple_compositions_given_list_champion_names_db
    #     Callable ran in 11.148115158081055 Sec
    #
    #     :param team_composition_size_start:
    #     :param team_composition_size_end:
    #     :param iter_champion_names: iterable of champion names
    #     :return: None
    #     """
    #
    #     # List containing tuples of the rows based on iter_champion_names
    #     list_tuple_row = self.sqlite_handler_team_composition_solver.get_pickled_list_tuple_champion_composition(
    #         iter_champion_names,
    #         team_composition_size_start,
    #         team_composition_size_end)
    #
    #     return list_tuple_row if list_tuple_row is not None else []
    #
    # @timer
    # @memory_usage
    # def get_list_tuple_compositions_given_list_champion_names_var(self, iter_champion_names: iter) -> List[Tuple]:
    #     """
    #     Given a iterable of champion names, get a list of tuples containing the champions in iter_champion_names
    #     from the instance variable self.list_tuple_compositions_combinations using the database to do the intersection
    #
    #     Faster and more memory intensive than the db version, but no massive db file (11 GB)
    #
    #     Memory (Before):                                             16.94140625 Mb
    #     Running Callable get_list_tuple_compositions_given_list_champion_names_var ...
    #     Memory (Before):                                             16.94921875 Mb
    #     Running Callable load_list_tuple_compositions_combinations_pickle ...
    #     Memory (After):                                              6056.58984375 Mb
    #     Memory Difference:                                           6039.640625 Mb
    #     Callable: TeamCompositionSolver.load_list_tuple_compositions_combinations_pickle
    #     Callable ran in 10.748010635375977 Sec
    #     Memory (After):                                              6061.72265625 Mb
    #     Memory Difference:                                           6044.78125 Mb
    #     Callable: TeamCompositionSolver.get_list_tuple_compositions_given_list_champion_names_var
    #     Callable ran in 20.25756001472473 Sec
    #
    #     :param iter_champion_names: iterable of champion names
    #     :return: None
    #     """
    #
    #     # If list_tuple_compositions_combinations_all is empty then load it
    #     if not self.list_tuple_compositions_combinations:
    #         self.load_pickle_list_tuple_compositions_combinations()
    #
    #     # List containing tuples of the rows based on iter_champion_names
    #     list_tuple_row = self.sqlite_handler_team_composition_solver.get_index_list_tuple_champion_composition(
    #         iter_champion_names)
    #
    #     return [self.list_tuple_compositions_combinations[tuple_composition_combination[0]] for
    #             tuple_composition_combination in list_tuple_row]

    @timer
    @memory_usage
    def _add_list_tuple_compositions_combinations_all_to_db(self):
        """
        Add the list of tuples that are the team composition combinations into the db

        Callable: TeamCompositionSolver.add_list_tuple_compositions_combinations_all_to_db
        Callable ran in 523.2395713329315 Sec

        db size approximately 11 GB

        :return:
        """
        self.sqlite_handler_team_composition_solver.add_list_tuple_compositions_combinations_to_table_team_composition_combination(
            self.list_tuple_compositions_combinations)

    @timer
    @memory_usage
    def _add_dict_key_champion_name_value_list_index_champion_composition_to_db(self):
        """
        Add the the dict of champions and their list that containing the index that represents which composition they
        are into the db

        Callable: TeamCompositionSolver.add_dict_key_champion_name_value_list_index_champion_composition_to_db
        Callable ran in 849.225474357605 Sec

        db size approximately 11 GB

        :return: None
        """
        self.sqlite_handler_team_composition_solver.add_dict_key_champion_name_value_list_index_champion_composition(
            self.dict_key_champion_name_value_list_index_champion_composition)

    @timer
    @memory_usage
    def run_complete_calculation_list_tuple(self, team_composition_size=9):
        """
        DO NOT RUN THIS UNLESS YOU KNOW WHAT YOU ARE DOING

        This will
            1.  Calculate all useful tft team composition combinations as a list of tuples and then pickle it
                (Up to 40 GB in memory when calculating and 9 hours of computation)
            2.  Load that pickle into self.list_tuple_compositions_combinations_all (6 GB when loaded into a var)
            3.  Transform that list into a dict with the champion_name as a key and indices representing the value
                (So... like another 6 Gb)
            4.  Put the list and the dict into a a SQLite database (11 GB)

        Run Time:
            8 to 10 hours run.

        Memory:
            6 GB to 50 GB used.

        :return: None
        """
        # Ask user if they are sure they should do the operation
        user_response = input("Are you sure you want to\n"
                              "1. Calculate all useful tft team composition combinations\n"
                              "2. Load that pickle into self.list_tuple_compositions_combinations_all\n"
                              "3. Transform that list into a dict with the champion_name as a key and indices representing the value\n"
                              "4. Create the SQLite database and put the list and the dict into the SQLite database\n"
                              "Recommended 64 GB memory for team composition size of 9 for 8 to 10 hours (yes/no): ")

        # If yes
        if user_response == "yes":

            # If the pickle file does not exist
            if not os.path.exists(PICKLE_LIST_TUPLE_NAME):
                # Calculate all useful tft team compositions and pickle it into a file
                self._create_list_tuple_compositions_combinations_pickle(team_composition_size)

            else:
                print("{} already exists!".format(os.path.basename(PICKLE_LIST_TUPLE_NAME)))

            self._run_complete_calculation_list_tuple_faster_operations()

    def _run_complete_calculation_list_tuple_faster_operations(self):
        """
        The faster operations of run_complete_calculation_list_tuple if you already have a pickle of the list of tuples
        that are the list of team composition combinations.

        :return: None
        """
        # Load the pickle into a var
        self.load_pickle_list_tuple_compositions_combinations()

        # Transform the var into dict containing champion names and what composition they are in via index
        self._transform_list_tuple_compositions_combinations_all()

        # Create database
        _create_db_champion_tables(self.champion_pool.dict_champion_pool_name, self.trait_pool.dict_trait_pool)

        # Add the index of the list composition combinations and the list itself into the db
        self._add_list_tuple_compositions_combinations_all_to_db()

        # Add the tables based on champion name and their compositions they are in based on index
        self._add_dict_key_champion_name_value_list_index_champion_composition_to_db()
