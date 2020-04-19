"""
4/9/2020

Purpose:
    The main file for the application

"""
import os

from Teamfight_Tactics_Composition_Solver.TeamCompositionSolver import TeamCompositionSolver
from Teamfight_Tactics_Composition_Solver.TeamCompositionSolverGUI import TeamCompositionSolverGUI
from Teamfight_Tactics_Composition_Solver.constants import PATH_CHAMPIONS, PATH_TRAITS, \
    FILE_SQLITE_DB_CHAMPION_NAME_TEAM_COMPOSITION

if __name__ == '__main__':
    team_composition_solver = TeamCompositionSolver(PATH_CHAMPIONS, PATH_TRAITS)

    if not os.path.exists(FILE_SQLITE_DB_CHAMPION_NAME_TEAM_COMPOSITION):
        # Do not run this unless you want to calculate all possible useful team compositions
        team_composition_solver.run_complete_calculation_list_tuple(4)
        exit(0)

    print("Running GUI")
    team_composition_solver_gui = TeamCompositionSolverGUI(team_composition_solver)

