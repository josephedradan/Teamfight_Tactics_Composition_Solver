"""
2/22/2020

Purpose:
    Calculates all useful TFT Team Compositions given initial conditions

Important Notes:
    If you use this to find team compositions with max team composition of 9 it will take around 9 hours and use up to
    40 GBs of memory
    Example:
        Memory (Before):                                             16.98828125 Mb
        Running Function get_set_frozenset_all_compositions_combinations ...
        Total amount of team Compositions: 48731399
        Callable: TeamCompositionCombinationsSearcher.get_set_frozenset_all_compositions_combinations ran in 30914.107093811035 Sec
        Memory (After):                                              39833.74609375 Mb
        Memory Difference:                                           39816.7578125 Mb

Notes:
    Combination formula:
        C(n,r) = n!/(r!(n-r)!)
        where   n = number of objects
                r = sample size

    All possible team compositions is
        Summation from r = 0 to 9 of (51!)/(r!(51-r)!)
        where   n = 51 = the number of champions (number of objects)
                r = sample size
                Summation because of the power set
                0 to 9 because you can only have up to 9 champions... most of the time...


        solution = 3,815,481,072
        That is really big

    Power set size = 2^n
        where   n = number of members

    So (Summation from r = 0 to 51 of (51!)/(r!(51-r)!)) = 2^51 = 2,251,799,813,685,248

Optimizations:
    OPTIMIZATION 1:
        Instead of getting every possible combination of n champions which is given by the below equation.
        (It's the power set)
        (Summation from r = 0 to n of (n!)/(r!(n-r)!)) = 2251799813685248 combinations
            where   n = number of champions in tft
                    n = 50

        Know that there is a limit on the maximum amount of champions on the field, in other words
        Get the maximum amount of combinations based on the amount of champions allowed on the field.
        (It's the power set with a size limit)

        Example:
            Champion limit = In game TFT level = 9 (In General)
            (Summation from r = 0 to 9 of (51!)/(r!(51-r)!)) = 3815481072 combinations

    OPTIMIZATION 2:
        Notice that you want Champion synergies that are useful to the current team composition,
        this will remove a lot of combinations that are useless for now...

        Example:
            Given an 8 champ cap
            size:  9143027
            Function get_set_frozenset_compositions_combinations ran in:    5414.366466522217 Sec

            So 90 MINUTES to calculate all useful team composition combinations

    OPTIMIZATION 3:
        Notice when you have the maximum amount of champions on the field, the last champ added to the composition
        probably needs to contribute the existing synergies or your team composition is probably sub optimal in terms
        of synergies.

        Example:
            team_composition_selected = ["Ahri", "Syndra", "Zoe"] and team_composition_size = 6.

            Without the optimization
                Memory (Before):                                             14.859375 Mb
                Running Function get_set_frozenset_compositions_combinations ...
                Total amount of team Compositions: 2862
                Function get_set_frozenset_compositions_combinations ran in:      1.2907438278198242 Sec
                Memory (After):                                              15.82421875 Mb
                Memory Difference:                                           0.96484375 Mb
                Callable: TeamCompositionContainerFactory._get_set_frozenset_compositions_combinations Call Count: 2863

            With the optimization
                Memory (Before):                                             14.91015625 Mb
                Running Function get_set_frozenset_compositions_combinations ...
                Total amount of team Compositions: 2243
                Function get_set_frozenset_compositions_combinations ran in:      1.0419845581054688 Sec
                Memory (After):                                              15.578125 Mb
                Memory Difference:                                           0.66796875 Mb
                Callable: TeamCompositionContainerFactory._get_set_frozenset_compositions_combinations Call Count: 2244

    OPTIMIZATION 4 (IT'S SLOWER PAST team_composition_size = 5 AND A MEMORY HOGGER BECAUSE IT GOES DEEP IN A
    BRANCH RATHER THAN PRIMARILY FLAT WHEN FINDING THE TEAM COMPOSITION):
        Assume that a champion only has 1 trait.
        Notice when you have a composition and in that composition the champions you have give a
        discrete value that gives the the team synergy trait bonus. If there is a higher level for that synergy trait
        like Star Guardian from 3 to 6, you need 3 more Star Guardian units until you can reach that level. If
        the team composition size is limited to 5 and you already have 3 Star Guardians then you realize that getting
        6 Star Guardians is impossible. That means that any further addition of a Star Guardian will never get you
        6 Star Guardians and therefore you skip adding any further Star Guardians because they don't add value.
        Obviously it's more complicated than that since champions generally have 2 traits like with Champions that are
        both Star Guardian and Sorcerer and Sorcerer's discrete values are 2, 4, and 6.
        Also a team composition can have more than just 1 trait bonus just look at Star Guardian and Sorcerer for example.
        Basically, allow for compositions that have the potential to get more and higher level synergies and that have
        a trait count total higher than that of the current team composition size.

        Example (team_composition_size = 5):
            team_composition_size = 5       NO team_composition_selected

            NO OPTIMIZATION
                Memory (Before):                                             14.9375 Mb
                Running Function get_set_frozenset_compositions_combinations ...
                Total amount of team Compositions: 40258
                Function get_set_frozenset_compositions_combinations ran in:      26.64392113685608 Sec
                Memory (After):                                              18.90625 Mb
                Memory Difference:                                           3.96875 Mb
                Function get_list_all_team_composition_containers ran in:    27.14017391204834 Sec
                Callable: TeamCompositionContainerFactory._get_set_frozenset_compositions_combinations Call Count: 40259


            WITH OPTIMIZATION
                Memory (Before):                                             14.86328125 Mb
                Running Function get_set_frozenset_compositions_combinations ...
                Total amount of team Compositions: 11898
                Function get_set_frozenset_compositions_combinations ran in:      8.450071096420288 Sec
                Memory (After):                                              16.2734375 Mb
                Memory Difference:                                           1.41015625 Mb
                Function get_list_all_team_composition_containers ran in:    8.597201108932495 Sec
                Callable: TeamCompositionContainerFactory._get_set_frozenset_compositions_combinations Call Count: 11899


            Notice that when a team composition has a lot of champions but no synergy then why would ever have that
            composition the only benefits of that composition is that you will get a lot of synergies later on... maybe.
            So why not remove those team compositions where the synergy trait count discrete is less than the amount of
            champions you have in your composition? Like with Ezeral, Ahri, and Aurelion Sol there are no synergies.

            WITH OPTIMIZATION AND WITH REMOVAL OF COMPOSITIONS WITH LOW TRAIT COUNT DISCRETE
                Memory (Before):                                             14.90234375 Mb
                Running Function get_set_frozenset_compositions_combinations ...
                Total amount of team Compositions: 25526
                Function get_set_frozenset_compositions_combinations ran in:      17.940165519714355 Sec
                Memory (After):                                              18.16015625 Mb
                Memory Difference:                                           3.2578125 Mb
                Function get_list_all_team_composition_containers ran in:    18.253734350204468 Sec
                Callable: TeamCompositionContainerFactory._get_set_frozenset_compositions_combinations Call Count: 25527

        Example (team_composition_size = 6)
            team_composition_size = 6       NO team_composition_selected

            NO OPTIMIZATION
                Memory (Before):                                             14.8984375 Mb
                Running Function get_set_frozenset_compositions_combinations ...
                Total amount of team Compositions: 243840
                Function get_set_frozenset_compositions_combinations ran in:      115.73514914512634 Sec
                Memory (After):                                              40.34765625 Mb
                Memory Difference:                                           25.44921875 Mb
                Function get_list_all_team_composition_containers ran in:    118.16569066047668 Sec
                Callable: TeamCompositionContainerFactory._get_set_frozenset_compositions_combinations
                Callable Call Count: 243841

            WITH OPTIMIZATION
                Memory (Before):                                             14.953125 Mb
                Running Function get_set_frozenset_compositions_combinations ...
                Total amount of team Compositions: 192360
                Function get_set_frozenset_compositions_combinations ran in:      152.60903787612915 Sec
                Memory (After):                                              35.078125 Mb
                Memory Difference:                                           20.125 Mb
                Function get_list_all_team_composition_containers ran in:    155.71874237060547 Sec
                Callable: TeamCompositionContainerFactory._get_set_frozenset_compositions_combinations
                Callable Call Count: 192361

        EXAMPLE (team_composition_size = 7)
            team_composition_size = 7       NO team_composition_selected

            NO OPTIMIZATION
                Memory (Before):                                             14.87109375 Mb
                Running Function get_set_frozenset_compositions_combinations ...
                Total amount of team Compositions: 1463888
                Function get_set_frozenset_compositions_combinations ran in:      759.7755148410797 Sec
                Memory (After):                                              175.11328125 Mb
                Memory Difference:                                           160.2421875 Mb
                Function get_list_all_team_composition_containers ran in:    777.5406668186188 Sec
                Callable: TeamCompositionContainerFactory._get_set_frozenset_compositions_combinations
                Callable Call Count: 1463889

            WITH OPTIMIZATION
                Memory (Before):                                             14.90234375 Mb
                Running Function get_set_frozenset_compositions_combinations ...
                Total amount of team Compositions: 1178816
                Function get_set_frozenset_compositions_combinations ran in:      1050.6679754257202 Sec
                Memory (After):                                              143.58984375 Mb
                Memory Difference:                                           128.6875 Mb
                Function get_list_all_team_composition_containers ran in:    1072.6780829429626 Sec
                Callable: TeamCompositionContainerFactory._get_set_frozenset_compositions_combinations
                Callable Call Count: 1178817

        EXAMPLE (team_composition_size = 9)
            team_composition_size = 9       NO team_composition_selected

            NO OPTIMIZATION
                Memory (Before):                                             14.90625 Mb
                Running Function get_set_frozenset_compositions_combinations ...
                ...
                Total amount of team Compositions: 48731399
                Function get_set_frozenset_compositions_combinations ran in:      30937.304706573486 Sec
                Memory (After):                                              6048.50390625 Mb
                Memory Difference:                                           6033.59765625 Mb
                Function get_list_all_team_composition_containers ran in:    31788.17203116417 Sec
                Callable: TeamCompositionContainerFactory._get_set_frozenset_compositions_combinations Call Count: 48731400


            WITH OPTIMIZATION
                Memory (Before):                                             15.00390625 Mb
                Running Function get_set_frozenset_compositions_combinations ...
                ...
                Total amount of team Compositions: 44010252
                Function get_set_frozenset_compositions_combinations ran in:      47554.773388147354 Sec
                Memory (After):                                              5465.76953125 Mb
                Memory Difference:                                           5450.765625 Mb
                Function get_list_all_team_composition_containers ran in:    48671.00490140915 Sec
                Callable: TeamCompositionContainerFactory._get_set_frozenset_compositions_combinations Call Count: 44010253


CALCULATING APPROXIMATIONS:
    Time Approximation using Optimizations (1, 2, 3)
        Derived Equation from team_composition_size from 1 to 7 using Excel:
            y = 0.0013e^(1.8958x)

        Approximating for team composition team_composition_size = 9
            y = 0.0013e^(1.8958x) where x = 9
            y = 33416.6 Sec = 9.2823888888888888888888888888889‬ Hours

        Actual
            Function get_set_frozenset_compositions_combinations ran in:      30937.304706573486 Sec
            30937.304706573486 Sec = 8.59369575182596833 Hours

        Percent Error:
            +8.014 percent

    Amount of Team Compositions using Optimizations (1, 2, 3)
        Derived Equation from team_composition_size from 1 to 7 using Excel:
            y = 6.8378e^(1.7404x)

        Approximating for team composition team_composition_size = 9
            y = 6.8378e^(1.7404x) where x = 9
            y = 43404200
        Actual
            Total amount of team Compositions: 48731399

        Percent Error:
            -10.93 percent

"""
import threading
from typing import List, Tuple, FrozenSet, Set

from Teamfight_Tactics_Composition_Solver.TeamCompositionContainer import TeamCompositionContainer
from Teamfight_Tactics_Composition_Solver.TeamCompositionContainerFactory import \
    TeamCompositionContainerFactory
from Teamfight_Tactics_Composition_Solver.constants import TEAM_COMPOSITION_SIZE_MAX

from josephs_resources.Decorators.V1.CallableCalledCount import callable_called_count
from josephs_resources.Decorators.V1.MemoryUsage import memory_usage
from josephs_resources.Decorators.V2.Timer import timer


class TeamCompositionCombinationsSearcher:

    def __init__(self, team_composition_container_factory: TeamCompositionContainerFactory):
        """
        Searcher to find all useful TFT composition combinations

        :param team_composition_container_factory: Factory to make team composition containers
        """
        self.team_composition_container_factory = team_composition_container_factory
        self.champion_pool = self.team_composition_container_factory.champion_pool
        self.trait_pool = self.team_composition_container_factory.trait_pool

        self.team_composition_size = TEAM_COMPOSITION_SIZE_MAX

    @memory_usage
    @timer(show_arguments=False)
    def get_list_tuple_compositions_combinations(self,
                                                 team_composition_size: int = None,
                                                 team_composition_selected: list = None,
                                                 search_type: str = "and") -> List[Tuple]:
        """
        Wrapper over the get_set_frozenset_compositions_combinations to get a list tuple version from the
        set frozenset version

        :param team_composition_size: team comp size
        :param team_composition_selected: list of a team composition
        :param search_type: use and or or when searching based on team_composition_selected
        :return: list_tuple_shared_solutions
        """
        set_frozenset_shared_solutions = self.get_set_frozenset_compositions_combinations(team_composition_size,
                                                                                          team_composition_selected,
                                                                                          search_type)

        list_tuple_shared_solutions = [tuple(i) for i in set_frozenset_shared_solutions]

        return list_tuple_shared_solutions

    @memory_usage
    @timer(show_arguments=False)
    def get_set_frozenset_compositions_combinations(self,
                                                    team_composition_size: int = None,
                                                    team_composition_selected: list = None,
                                                    search_type: str = "and") -> Set[FrozenSet]:
        """
         Get a set of frozensets of the possible useful team composition combinations given the initial conditions

         :param team_composition_size: team comp size
         :param team_composition_selected: list of a team composition
         :param search_type: use and or or when searching based on team_composition_selected
         :return: list_tuple_shared_solutions
         """
        if team_composition_size is None:
            team_composition_size = self.team_composition_size

        # Set containing frozensets which are solutions
        set_frozenset_shared_solutions = set()  # type: Set[FrozenSet]

        # A Temp list that can potentially be a solution
        list_temp_shared_generic_solution = []  # type: list

        # Loop through dict pool of champions to get a list of champion objects
        list_champions_objects_temp = [value for key, value in self.champion_pool.dict_champion_pool_name.items()]

        # Sort champion objects by champion cost
        list_champions_objects_temp.sort()

        # Get the name (or dict_index_position_id for space saving) of the champion objects into a list
        list_champions_temp = [i.name for i in list_champions_objects_temp]

        # Transform the champion name to it's dict_index_position_id equivalent for space saving
        # team_composition_selected = [self.champion_pool.dict_champion_pool_name.get(i) for i in team_composition_selected]

        # Recursive call
        self._get_set_frozenset_compositions_combinations(list_temp_shared_generic_solution,
                                                          list_champions_temp,
                                                          set_frozenset_shared_solutions,
                                                          None,
                                                          team_composition_size,
                                                          team_composition_selected,
                                                          search_type)

        print("Total amount of team Compositions:", len(set_frozenset_shared_solutions))

        return set_frozenset_shared_solutions

    @callable_called_count
    def _get_set_frozenset_compositions_combinations(self,
                                                     list_temp_shared_generic_solution: list,
                                                     list_remaining_items: list,
                                                     set_frozenset_shared_solutions: set,
                                                     team_composition_container_temp_old: TeamCompositionContainer,
                                                     team_composition_size: int,
                                                     team_composition_selected: list,
                                                     search_type: str
                                                     ) -> None:
        """
        Recursive DFS of all permutations of a List, but making them unique via frozen set

        :param list_temp_shared_generic_solution: temporary List of the current permutation (temp List is shared)
        :param list_remaining_items: List of remaining items that need to be added to list_temp
        :param set_frozenset_shared_solutions: set of frozensets that are part of the power set
        :return:
        """
        # Loop through the remaining List
        for index in range(len(list_remaining_items)):

            # New champion to add
            name_new = list_remaining_items[index]

            # Add the indexed item into the temp List
            list_temp_shared_generic_solution.append(name_new)

            # Create a copy of list_remaining_items
            list_remaining_items_new = list_remaining_items.copy()

            # Pop off the item with the index number
            list_remaining_items_new.pop(index)

            # Set the traits given by current team composition
            if team_composition_container_temp_old is not None:
                dict_composition_traits_old = team_composition_container_temp_old.dict_trait_count
            else:
                dict_composition_traits_old = {}

            # Temp team composition container
            team_composition_container_temp_new = self.team_composition_container_factory.get_team_composition_container(
                list_temp_shared_generic_solution)

            # Dict of traits for the current composition
            dict_composition_traits_new = team_composition_container_temp_new.dict_trait_count

            length_list_temp_shared_generic_solution = len(list_temp_shared_generic_solution)

            """
            OPTIMIZATION 1
            If the length of list_temp_shared_generic_solution is greater than team_composition_size then
            skip that composition
            """
            if length_list_temp_shared_generic_solution > team_composition_size:
                # Skip the recursive call
                list_temp_shared_generic_solution.pop()
                continue

            # If a Team composition selected was given to be searched via "and" or "or"
            if team_composition_selected:
                if search_type == "or":
                    """
                    Check if list_temp_shared_generic_solution should contain champions from team_composition_selected via or
                     
                    If search_type == "or" then you are looking for champions in list_temp_shared_generic_solution that 
                    contain any of the champions listed in team_composition_selected
    
                    """

                    if all([True if i not in list_temp_shared_generic_solution else
                            False for i in team_composition_selected]):
                        list_temp_shared_generic_solution.pop()
                        continue

                    # Alternative
                    # if not any([True if i in list_temp_shared_generic_solution else
                    #             False for i in team_composition_selected]):
                    #     list_temp_shared_generic_solution.pop()
                    #     continue

                elif search_type == "and":
                    """
                    Check if list_temp_shared_generic_solution should contain champions from team_composition_selected via and
                    
                    If search_type == "and" then you are looking for champions in list_temp_shared_generic_solution that
                    contain all of the champions listed in team_composition_selected
                    """
                    name_not_in_list_temp_shared_generic_solution = False

                    """
                    If the current team composition does not have all the listed given champions then skip the current team
                    composition            
                    
                    index_2 is required because you want to check when you have team composition size that can support more
                    champions. Basically when you want Ahri and Syndra in the same composition you can't say they both need
                    to be in the composition at all times, because this callable is recursive which means you build the
                    team composition starting from no champion to the maximum amount of champions on the field.
                    """
                    for index_2, champion_name in enumerate(team_composition_selected):
                        if champion_name not in list_temp_shared_generic_solution and length_list_temp_shared_generic_solution >= index_2 + 1:
                            name_not_in_list_temp_shared_generic_solution = True
                            break

                    # If champion_name is not in the team composition
                    if name_not_in_list_temp_shared_generic_solution:
                        list_temp_shared_generic_solution.pop()
                        continue

            # Make a frozen set of the list_temp_shared_generic_solution
            frozenset_temp = frozenset(list_temp_shared_generic_solution)

            # If frozenset_temp is not in set_frozenset_shared_solutions (This prevents duplicate runs)
            if frozenset_temp not in set_frozenset_shared_solutions:

                # Var to determine if the trait for the current composition has increased
                trait_increased = False

                """
                OPTIMIZATION 2
                Only allow for a combination if it contributes to increasing the existing trait count/counts
                This allows for only champion synergies starting from the first champion then following champions
                It also means that the amount of combinations is less than 
                (Summation from r = 0 to 9 of (51!)/(r!(51-r)!))
                """
                for trait_key_old, trait_value_old in dict_composition_traits_old.items():
                    trait_value_new = dict_composition_traits_new.get(trait_key_old)

                    bool_value_increased = trait_value_new > trait_value_old

                    remaining_units_till_max_comp_size = team_composition_size - length_list_temp_shared_generic_solution

                    """
                    OPTIMIZATION 4
                    If the given discrete_difference is less than the remaining_units_till_max_comp_size then False
                    
                    If all of the given discrete_difference AT LEAST give a False then the current team composition
                    has potential to increase the value in the dict_trait_count_discrete
                    
                    If all of the given discrete_difference ALL give a True then the current team composition
                    may be efficient (in terms of get_discrete_count_total being high)
                    where you might reach AT LEAST 1 AND POSSIBLY MORE trait_count_discrete being achieved and have
                    a trait_count_discrete_difference to the next level even though you've reached the
                    team_composition_size OR you may not be efficient (in terms of get_discrete_count_total being low)
                    where the amount of units you have is greater than the get_discrete_count_total() in other words,
                    you have little to no synergies. (*** NOTE THAT SINCE THIS CALLABLE IS RECURSIVE, THE COMPOSITION
                    MIGHT NOT BE EFFICIENT NOW, BUT LATTER IT MIGHT BE AND MIGHT BE CAUGHT)
                    
                    AND
                    
                    get_discrete_count_total() IS LOWER THAN length_list_temp_shared_generic_solution
                    
                    THIS MEANS THAT ONLY TEAM COMPOSITIONS THAT MAY BE EFFICIENT WHERE 
                    get_discrete_count_total() >= length_list_temp_shared_generic_solution AND
                    THAT HAVE THE POTENTIAL TO increase the value in the dict_trait_count_discrete ARE ALLOWED TO BYPASS 
                    THIS IF STATEMENT
                    
                    """
                    # if all([False if discrete_difference <= remaining_units_till_max_comp_size else True for
                    #         key, discrete_difference in
                    #         team_composition_container_temp_new.dict_trait_count_discrete_difference.items()]) and team_composition_container_temp_new.get_discrete_count_total() < length_list_temp_shared_generic_solution:
                    #     # print("remaining_units_till_max_comp_size", remaining_units_till_max_comp_size)
                    #     # print(team_composition_container_temp_new.tuple_team_composition)
                    #     # print(team_composition_container_temp_new.dict_trait_count)
                    #     # print(team_composition_container_temp_new.dict_trait_count_discrete)
                    #     # print(team_composition_container_temp_new.dict_trait_count_discrete_difference)
                    #     # print(team_composition_container_temp_new.get_discrete_count_total())
                    #     # print()
                    #     break

                    """
                    OPTIMIZATION 3
                    If the size of team composition is max size and the last additional unit does contribute to 
                    increasing the existing trait count then don't add that composition
                    
                    Without bool_value_increased here, you will add a suboptimal composition for no reason.
                    For example:                    
                        Forcing a composition with both 'Ahri' and 'Syndra' and limiting the team composition size to 3.
                        
                        With it, you will get team compositions that contribute to the existing composition traits
                        which are Star Guardian and Sorcerer such as 
                            ['Ahri', 'Syndra', 'Poppy']
                            {'Star Guardian': 3, 'Sorcerer': 2, 'Vanguard': 0}
                            
                        Without it, you can add additional sub optimal composition such as 
                            ['Ahri', 'Syndra', 'Miss Fortune']
                            {'Star Guardian': 0, 'Sorcerer': 2, 'Valkyrie': 0, 'Mercenary': 1, 'Blaster': 0}
                        which is unnecessary
                                                
                    """
                    if length_list_temp_shared_generic_solution == team_composition_size and bool_value_increased:
                        dict_composition_traits_discrete_new = team_composition_container_temp_new.get_trait_count_discrete_total()
                        dict_composition_traits_discrete_old = team_composition_container_temp_old.get_trait_count_discrete_total()
                        """
                        If the sum of the dict_composition_traits_discrete_new is greater than the
                        sum of the dict_composition_traits_discrete_old then trait has increased.
                        Two conditions must be meet or else
                        """
                        if dict_composition_traits_discrete_new > dict_composition_traits_discrete_old:
                            # This guarantees that the frozenset_temp will be added to set_frozenset_shared_solutions
                            trait_increased = True
                        # Break off this branch
                        break

                    if bool_value_increased:
                        # The below guarantees that the frozenset_temp will be added to set_frozenset_shared_solutions
                        trait_increased = True
                        break

                # If a current trait in a composition has increased of if dict_composition_traits_old empty
                if trait_increased or not dict_composition_traits_old:

                    # if team_composition_container_temp_new.dict_trait_count_discrete[
                    #     "Star Guardian"] >= 6 and dict_composition_traits_old:
                    #     print("\t", team_composition_container_temp_new.tuple_team_composition)
                    #     print("\t", team_composition_container_temp_new.dict_trait_count)
                    #     print("\t", team_composition_container_temp_new.dict_trait_count_discrete)
                    #     print("\t", team_composition_container_temp_new.get_discrete_count_total())
                    #     print()

                    # if team_composition_container_temp_new.get_discrete_count_total() >= 19:
                    #     print("\t", team_composition_container_temp_new.tuple_team_composition)
                    #     print("\t", team_composition_container_temp_new.dict_trait_count)
                    #     print("\t", team_composition_container_temp_new.dict_trait_count_discrete)
                    #     print("\t", team_composition_container_temp_new.get_discrete_count_total())
                    #     print()

                    # Add frozenset_temp to set_frozenset_shared_solutions
                    set_frozenset_shared_solutions.add(frozenset_temp)

                    """
                    Small optimization
                    Don't recursive call if list_remaining_items_new is empty because len(list_remaining_items) is empty
                    
                    and length_list_temp_shared_generic_solution <= team_composition_size is not needed here because
                    the length_list_temp_shared_generic_solution > team_composition_size at the beginning of this
                    callable prevented anything larger than team_composition_size from passing in the first place.
                    """
                    if list_remaining_items_new:
                        # Recursive call into this function
                        self._get_set_frozenset_compositions_combinations(list_temp_shared_generic_solution,
                                                                          list_remaining_items_new,
                                                                          set_frozenset_shared_solutions,
                                                                          team_composition_container_temp_new,
                                                                          team_composition_size,
                                                                          team_composition_selected,
                                                                          search_type
                                                                          )
            # If the frozenset_temp already exists
            else:
                # Skip the recursive call
                list_temp_shared_generic_solution.pop()
                continue

            # Pop from list_temp_permutation for a new permutation
            list_temp_shared_generic_solution.pop()
