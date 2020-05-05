"""
4/3/2020


Purpose:
    DB handling for team composition combinations

Reference:
    Foreign keys in SQLite3 because it's more difficult than normal SQL
        https://www.techonthenet.com/sqlite/foreign_keys/foreign_keys.php

    SQLite Python
        https://www.sqlitetutorial.net/sqlite-python/

    SQLite Python Docs
        https://docs.python.org/3/library/sqlite3.html#sqlite3.Cursor.execute
        # fetch methods

    Can I pickle a python dictionary into a sqlite3 text field?
        https://stackoverflow.com/questions/198692/can-i-pickle-a-python-dictionary-into-a-sqlite3-text-field
        # Basically you do this...
            pickled_data = pickle.dumps(_whatever_, pickle.HIGHEST_PROTOCOL)
            curr.execute("INSERT INTO table_name VALUES (:data)", {'data': sqlite3.Binary(pickled_data)})

    SQL Join
        https://www.w3schools.com/sql/sql_join_inner.asp

    How often to commit
        https://stackoverflow.com/questions/36243538/python-sqlite3-how-often-do-i-have-to-commit

    SQLite insert
        https://www.sqlitetutorial.net/sqlite-insert/

    SQLite Intersect
        https://www.sqlitetutorial.net/sqlite-intersect/

    Python SQLite Tutorial: Complete Overview - Creating a Database, Table, and Running Queries
        https://www.youtube.com/watch?v=pd-0G0MigUA

    DO NOT USE UNIQUE in SQLite
        https://www.percona.com/blog/2013/07/15/why-unique-indexes-are-bad/
        # IT WASTES MORE SPACE

    SQLite USES B-tree
        https://www.sqlitetutorial.net/sqlite-index/
        # Balance Tree to keep height low

    SQlite foreign key
        https://www.sqlitetutorial.net/sqlite-foreign-key/

"""
import pickle
import sqlite3
from typing import Tuple, List

from Teamfight_Tactics_Composition_Solver.TeamCompositionContainer import TeamCompositionContainer
from Teamfight_Tactics_Composition_Solver.TeamCompositionContainerFactory import TeamCompositionContainerFactory
from Teamfight_Tactics_Composition_Solver.TraitPool import TraitPool
from Teamfight_Tactics_Composition_Solver.constants import \
    FILE_SQLITE_DB_CHAMPION_NAME_TEAM_COMPOSITION, TEAM_COMPOSITION_SIZE_MAX, TRAIT_COUNT_TOTAL_MAX, \
    TEAM_COMPOSITION_SIZE_MIN, TRAIT_COUNT_DISCRETE_TOTAL_MIN
from josephs_resources.Database.functions_data_base_formatter import format_db_input
from josephs_resources.Database.SQLite3Wrapper import SQLite3Wrapper

STRING_CHAMPION_COMPOSITIONS_TABLE_NAME = "team_composition_combination"


class SQLiteHandlerTeamCompositionSolver(SQLite3Wrapper):
    def __init__(self, team_composition_container_factory: TeamCompositionContainerFactory):
        """
        SQLite handler to access the database of TFT team composition combinations

        :param team_composition_container_factory:
        :return None
        """

        super().__init__(FILE_SQLITE_DB_CHAMPION_NAME_TEAM_COMPOSITION)

        self.team_composition_container_factory = team_composition_container_factory
        self.trait_pool = self.team_composition_container_factory.trait_pool
        self.champion_pool = self.team_composition_container_factory.champion_pool

    def add_list_tuple_compositions_combinations_to_table_team_composition_combination(
            self,
            list_tuple_compositions_combinations_all):
        """
        Given a list of tuples where the tuples are team composition combinations
        for each team_composition_index and tuple_composition in list_tuple_compositions_combinations_all
            call add_team_composition_index_to_table_team_composition_combination with the corresponding
            arguments

        Also assign the traits associated with the team composition index, also include the trait count discrete

        :param list_tuple_compositions_combinations_all: list of tuples of the team composition combinations
        :return: None
        """
        for team_composition_index, tuple_composition in enumerate(list_tuple_compositions_combinations_all):
            team_composition_container = self.team_composition_container_factory.get_team_composition_container(
                tuple_composition)

            self._add_team_composition_index_to_table_team_composition_combination(
                team_composition_index,
                self.team_composition_container_factory.get_tuple_team_composition_transformed_integer(
                    tuple_composition),
                len(tuple_composition),
                team_composition_container.get_trait_count_discrete_total()
            )

            # WARNING: ADDING TRAITS ADDS AN ADDITIONAL 30 MINUTES OR SOMETHING LIKE THAT.
            # self._add_team_composition_traits(team_composition_index,
            #                                   team_composition_container)

        self.connection.commit()

    def _add_team_composition_index_to_table_team_composition_combination(self,
                                                                          team_composition_index,
                                                                          tuple_composition,
                                                                          team_composition_size,
                                                                          trait_count_discrete_total):
        """
        Given the team_composition_index and pickled_tuple_team_composition_combination
        add the team_composition_index,
        add a binary version of the pickled_tuple_team_composition to the team_composition_combination table,
        add the size of the team composition

        :return: None
        """
        # Pickle the tuple
        pickled_tuple_team_composition_combination = pickle.dumps(tuple_composition,
                                                                  protocol=pickle.HIGHEST_PROTOCOL)

        self.cursor.execute(
            """
            INSERT INTO {} VALUES (
                :team_composition_index, 
                :pickled_tuple_team_composition, 
                :team_composition_size, 
                :trait_count_discrete_total
            );
            """.format(
                STRING_CHAMPION_COMPOSITIONS_TABLE_NAME
            ),
            {
                'team_composition_index': team_composition_index,
                'pickled_tuple_team_composition': sqlite3.Binary(pickled_tuple_team_composition_combination),
                'team_composition_size': team_composition_size,
                'trait_count_discrete_total': trait_count_discrete_total
            }
        )

    def _add_team_composition_traits(self,
                                     team_composition_index,
                                     team_composition_container: TeamCompositionContainer):

        for trait_name, trait_count_discrete in team_composition_container.dict_trait_count_discrete.items():
            trait_name_formatted = format_db_input(trait_name)

            self.cursor.execute(
                """
                INSERT INTO {} VALUES (
                    :team_composition_index,
                    :trait_count_discrete
                    
                );
                """.format(
                    trait_name_formatted
                ),
                {
                    'team_composition_index': team_composition_index,
                    'trait_count_discrete': trait_count_discrete
                }
            )

    def add_team_composition_index_to_table_champion(self, champion_name, team_composition_index):
        """
        Given the champion_name_formatted and team_composition_index, insert team_composition_index in the
        corresponding table based on the champion_name_formatted

        :param champion_name: champion_name
        :param team_composition_index: team_composition_index
        :return: None
        """
        champion_name_formatted = format_db_input(champion_name)

        self._add_team_composition_index_to_table_champion(champion_name_formatted, team_composition_index)

        self.connection.commit()

    def add_dict_key_champion_name_value_list_index_champion_composition(
            self,
            dict_key_champion_name_value_list_index_champion_composition: dict):

        """
        Given a dict that has the key champion_name and the value list_index_champion_composition
        for each champion_name
            for each item in the value for the champion_name
                insert the champion_name_formatted into the table

        :param dict_key_champion_name_value_list_index_champion_composition:
        :return: None
        """
        for champion_name, list_index_champion_composition in dict_key_champion_name_value_list_index_champion_composition.items():

            # Format the champion_name for the database
            champion_name_formatted = format_db_input(champion_name)

            for index_champion_composition in list_index_champion_composition:
                self._add_team_composition_index_to_table_champion(champion_name_formatted,
                                                                   index_champion_composition)

        self.connection.commit()

    def _add_team_composition_index_to_table_champion(self, champion_name_formatted, team_composition_index):
        """
        Given the champion_name_formatted and team_composition_index, insert team_composition_index in the
        corresponding table based on the champion_name_formatted

        :param champion_name_formatted: champion name formatted
        :param team_composition_index: index of the corresponding composition combination
        :return: None
        """
        self.cursor.execute(
            "INSERT INTO {} VALUES (:team_composition_index)".format(
                champion_name_formatted),
            {'team_composition_index': team_composition_index}
        )

    def get_pickled_list_tuple_champion_composition(self,
                                                    iter_team_composition_current: iter,
                                                    iter_team_composition_exclude: iter,
                                                    team_composition_size_min: int = TEAM_COMPOSITION_SIZE_MIN,
                                                    team_composition_size_max: int = TEAM_COMPOSITION_SIZE_MAX,
                                                    trait_count_discrete_total_min: int = TRAIT_COUNT_DISCRETE_TOTAL_MIN,
                                                    trait_count_discrete_total_max: int = TRAIT_COUNT_TOTAL_MAX
                                                    ) -> List[Tuple]:
        """
        Given a iterable of champion names, get a list of tuples containing the indices that corresponds to
        the team composition combination

        :param iter_team_composition_current:
        :param iter_team_composition_exclude:
        :param team_composition_size_min:
        :param team_composition_size_max:
        :param trait_count_discrete_total_min:
        :param trait_count_discrete_total_max:
        :return: list that contains tuples of the rows
        """

        # If iter_team_composition_current is empty THEN DON'T RUN BECAUSE TABLE IS MASSIVE
        if not iter_team_composition_current:
            return []

        # string for the selection
        string_query_select_base = "SELECT team_composition_index FROM {} "

        # Intersect keyword in sqlite
        string_intersect = "INTERSECT"

        string_query_intersect = "{} ".format(string_intersect).join(
            [string_query_select_base.format(format_db_input(champion_name)) for champion_name in
             iter_team_composition_current])

        string_except = "EXCEPT"

        string_query_except = string_except + " " + "{} ".format(string_except).join(
            [string_query_select_base.format(format_db_input(champion_name)) for champion_name in
             iter_team_composition_exclude])

        string_query_on = "ON {}.team_composition_index = temp_table.team_composition_index".format(
            STRING_CHAMPION_COMPOSITIONS_TABLE_NAME)

        string_query_join_champions = """
        JOIN
        (
            {}
            {}
        ) as temp_table
        {}\n
        """.format(string_query_intersect if iter_team_composition_current else "",
                   string_query_except if iter_team_composition_exclude else "",
                   string_query_on)

        string_query_select_traits = ", ".join(
            ["{}.trait_count_discrete".format(format_db_input(trait) + "_table") for trait in
             self.trait_pool.dict_trait_pool])
        string_query_select_traits_complete = ", " + string_query_select_traits

        string_query_select_base_left_join = "SELECT team_composition_index, trait_count_discrete FROM {} "

        string_query_join_trait_base = """
        LEFT JOIN
        (
            {}
        ) as {}
        {}
        """

        string_query_on_left_join = "ON {}.team_composition_index = {}.team_composition_index"

        string_query_join_traits_complete = "\n".join([string_query_join_trait_base.format(
            string_query_select_base_left_join.format(format_db_input(trait)),
            format_db_input(trait) + "_table",
            string_query_on_left_join.format(STRING_CHAMPION_COMPOSITIONS_TABLE_NAME,
                                             format_db_input(trait) + "_table"
                                             )
        ) for trait in self.trait_pool.dict_trait_pool])

        string_query_full = r"""
        SELECT {}.team_composition_index, pickled_tuple_team_composition, team_composition_size, trait_count_discrete_total{}
        FROM {} 
        {}
        {}
        WHERE {}.team_composition_size >= {}
        AND {}.team_composition_size <= {}
        AND {}.trait_count_discrete_total >= {}
        AND {}.trait_count_discrete_total <= {}
        ;
        """.format(
            STRING_CHAMPION_COMPOSITIONS_TABLE_NAME,
            # string_query_select_traits_complete,  # A LOT OF COLUMNS BASED ON THE BIG COSTLY JOIN!
            "",
            STRING_CHAMPION_COMPOSITIONS_TABLE_NAME,
            string_query_join_champions if iter_team_composition_current or iter_team_composition_exclude else "",
            # string_query_join_traits_complete,  # THE JOIN IS TOO COSTLY FOR A BIG DB, OPERATIONS WILL BE VERY SLOW
            "",
            STRING_CHAMPION_COMPOSITIONS_TABLE_NAME,
            team_composition_size_min,
            STRING_CHAMPION_COMPOSITIONS_TABLE_NAME,
            team_composition_size_max,
            STRING_CHAMPION_COMPOSITIONS_TABLE_NAME,
            trait_count_discrete_total_min,
            STRING_CHAMPION_COMPOSITIONS_TABLE_NAME,
            trait_count_discrete_total_max
        )

        # print(string_query_full)

        self.cursor.execute(string_query_full)

        return self._get_pickled_list_tuple_champion_composition_format(self.cursor.fetchall(), 1)

    def _get_pickled_list_tuple_champion_composition_format(self, list_fetch: list, pickle_data_position) -> list:
        """
        load the pickled data in the list of tuples of rows

        :param list_fetch: cursor.fetchall()
        :return: list fetch modified
        """
        for index in range(len(list_fetch)):
            list_fetch[index] = list(list_fetch[index])

            list_fetch[index][pickle_data_position] = pickle.loads(list_fetch[index][pickle_data_position])

            list_fetch[index][
                pickle_data_position] = self.team_composition_container_factory.get_tuple_team_composition_transformed_name(
                list_fetch[index][pickle_data_position])

        return list_fetch

    def get_index_list_tuple_champion_composition(self, iter_champion_names: iter) -> List[Tuple]:
        """
        Given a iterable of champion names, get a list of tuples containing the indices that corresponds to
        the team composition combination

        :param iter_champion_names: iterable of champions
        :return: list that contains tuples of the rows
        """

        # string for the selection
        string_column_table_base = "SELECT team_composition_index FROM {}"

        # Intersect keyword in sqlite
        string_intersect = "INTERSECT"

        self._get_from_table_team_composition_combination(string_column_table_base,
                                                          string_intersect,
                                                          iter_champion_names)

        return [pickle.loads(i[0]) for i in self.cursor.fetchall()]

    def _get_from_table_team_composition_combination(self,
                                                     string_column_table_base: str,
                                                     operation: str,
                                                     iter_champion_names: iter):
        """
        Given the string_column_table_base, SQLite operation, and the iter_champion_names
        Execute that query

        :param string_column_table_base:
        :param operation:
        :param iter_champion_names:
        :return: None
        """

        string_query = " {} ".format(operation).join(
            [string_column_table_base.format(format_db_input(champion_name)) for champion_name in iter_champion_names])

        self.cursor.execute(string_query)


def _create_db_champion_tables(champion_pool_dict: dict, trait_pool_dict: dict):
    """
    Given a dict containing the key champion_name with the value of list_index_champion_composition
        create a table that contains the amount of champions available in TFT (as in names of champions)
        with 1 column that contains the index which corresponds to the team composition combination

        create a table that contains the index which corresponds the the team composition combination and
        a blob which contains the binary representation of the pickled (serialized) team composition combination tuple

    :param dict_key_champion_name_value_list_index_team_composition:
    :return: None
    """

    string_query_complete = """
    CREATE TABLE {}(
        team_composition_index INT PRIMARY KEY NOT NULL, 
        pickled_tuple_team_composition BLOB NOT NULL,
        team_composition_size INT NOT NULL,
        trait_count_discrete_total INT NOT NULL
        
    );\n
    """.format(STRING_CHAMPION_COMPOSITIONS_TABLE_NAME)

    string_query_base_champion = """
    CREATE TABLE {}(
        team_composition_index INT NOT NULL,
        FOREIGN KEY (team_composition_index)
            REFERENCES {}(team_composition_index)
    );\n
    """

    string_query_base_trait = """
    CREATE TABLE {}(
        team_composition_index INT NOT NULL,
        trait_count_discrete,
        FOREIGN KEY (team_composition_index)
            REFERENCES {}(team_composition_index)
    );\n
    """

    connection = sqlite3.connect(FILE_SQLITE_DB_CHAMPION_NAME_TEAM_COMPOSITION)

    cursor = connection.cursor()

    for champion_name, champion_object in champion_pool_dict.items():
        string_query_complete += string_query_base_champion.format("{}".format(format_db_input(champion_name)),
                                                                   STRING_CHAMPION_COMPOSITIONS_TABLE_NAME,
                                                                   STRING_CHAMPION_COMPOSITIONS_TABLE_NAME)

    for trait_name, trait_object in trait_pool_dict.items():
        string_query_complete += string_query_base_trait.format("{}".format(format_db_input(trait_name)),
                                                                STRING_CHAMPION_COMPOSITIONS_TABLE_NAME,
                                                                STRING_CHAMPION_COMPOSITIONS_TABLE_NAME)

    cursor.executescript(string_query_complete)

    connection.commit()
    connection.close()


"""

SELECT team_composition_combination.team_composition_index, pickled_tuple_team_composition, team_composition_size, trait_count_discrete_total,
Star_Guardian_table.team_composition_index,
Sniper_table.team_composition_index
 
FROM team_composition_combination 

JOIN
(
    SELECT team_composition_index FROM Ashe 
) as temp_table
ON team_composition_combination.team_composition_index = temp_table.team_composition_index

LEFT JOIN
(
    SELECT team_composition_index, trait_count_discrete FROM Star_Guardian
) as Star_Guardian_table
ON team_composition_combination.team_composition_index = Star_Guardian_table.team_composition_index

LEFT JOIN
(
    SELECT team_composition_index, trait_count_discrete FROM Sniper
) as Sniper_table
ON team_composition_combination.team_composition_index = Sniper_table.team_composition_index
 
 
WHERE team_composition_combination.team_composition_size >= 0
AND team_composition_combination.team_composition_size <= 9
AND team_composition_combination.trait_count_discrete_total >= 0
AND team_composition_combination.trait_count_discrete_total <= 100
;



"""
