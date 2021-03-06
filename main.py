"""
4/9/2020

Purpose:
    The main file for the application
    Calculates the possible team composition combinations to create the .pickle file and the .db file if not created.
    else
    Runs the GUI if the .db and .pickle file are created.
"""
import os

from Teamfight_Tactics_Composition_Solver.TeamCompositionSolver import TeamCompositionSolver
from Teamfight_Tactics_Composition_Solver.TeamCompositionSolverGUI import TeamCompositionSolverGUI
from Teamfight_Tactics_Composition_Solver.constants import PATH_CHAMPIONS, PATH_TRAITS, \
    FILE_SQLITE_DB_CHAMPION_NAME_TEAM_COMPOSITION

if __name__ == '__main__':

    # Creates a team_composition solver object
    team_composition_solver = TeamCompositionSolver(PATH_CHAMPIONS, PATH_TRAITS)

    # Does calculation if necessary
    if not os.path.exists(FILE_SQLITE_DB_CHAMPION_NAME_TEAM_COMPOSITION):
        # Do not run this unless you want to calculate all possible useful team compositions
        team_composition_solver.run_complete_calculation_list_tuple(4)
        exit(0)

    print("Running GUI")
    team_composition_solver_gui = TeamCompositionSolverGUI(team_composition_solver)
