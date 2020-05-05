"""
4/7/2020

Purpose:
    GUI for the whole thing

Important Note:
    Anything related to tkinter must be ran on the main thread

Reference:
    Errors
        https://www.programcreek.com/python/example/59684/tkinter.TclError

    Bindings
        https://effbot.org/tkinterbook/tkinter-events-and-bindings.htm

    Check if element is in queue (Not used)
        https://stackoverflow.com/questions/16506429/check-if-element-is-already-in-a-queue
        # If a callable was passed as an item then let the item tell you if it's in the queue

"""
import os
import time
from queue import Queue
from threading import Thread, Lock
from tkinter import Tk, Frame, Button, PhotoImage, END, TclError, StringVar, ACTIVE, NORMAL, IntVar
from tkinter.ttk import Scrollbar, Treeview, Style, Label, Entry, Checkbutton
from typing import Dict, Tuple

from Teamfight_Tactics_Composition_Solver.Champion import Champion
from Teamfight_Tactics_Composition_Solver.TeamCompositionSolver import TeamCompositionSolver
from Teamfight_Tactics_Composition_Solver.constants import DIR_CHAMPION_ICONS, TEAM_COMPOSITION_SIZE_MAX, \
    TRAIT_COUNT_TOTAL_MAX
from josephs_resources.Database.functions_data_base_formatter import format_db_input
from josephs_resources.Decorators.V2.Timer import timer

FONT_BUTTON_TEXT = ('Arial', 6, 'bold')

FRAME_RATE_CAP = 60
TIME_PER_FRAME = 1 / FRAME_RATE_CAP

FONT_DEFAULT = 'Arial 12 bold'

COLUMN_LIMIT = 17


class CallablePreservedContainer:
    __slots__ = ["callable_given", "args", "kwargs"]

    def __init__(self, callable_given: callable, *args, **kwargs):
        """
        Callable container that stores the callable and it's arguments

        :param callable_given: callable
        :param args: args
        :param kwargs: kwargs
        """
        self.callable_given = callable_given
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        Run the callable with it's arguments
        :return: callable(*args, **kwargs)
        """
        return self.callable_given(*self.args, **self.kwargs)


class Integer:
    __slots__ = ["value", "default"]

    def __init__(self, value):
        """
        Integer object because it uses references

        :param value: value of the integer
        """
        self.value = value
        self.default = value

    def get(self) -> int:
        """
        get self.value

        :return: self.value
        """
        return self.value

    def set(self, int_given: int):
        """
        set the self.value

        :param int_given:
        :return: None
        """
        self.value = int_given

    def get_default(self) -> int:
        """
        Get the original parameter given

        :return: self.default
        """
        return self.default

    def __call__(self):
        """
        Return self.value

        :return: self.value
        """
        return self.value


class TeamCompositionSolverGUI:

    def __init__(self, team_composition_solver: TeamCompositionSolver):
        """
        The GUI for the TeamCompositionSolver object.

        :param team_composition_solver: None
        """

        # ---- Main Thread ----

        # TeamCompositionSolver Object
        self.team_composition_solver = team_composition_solver

        # Using the names of the champions based on their images as the key and a Champion object as the value
        self.dict_champion_pool_transformed = {}  # type: Dict[str, Champion]

        # Current set of champions selected by the GUI
        self.set_team_composition_current = set()

        # Set that excludes champions from the db query
        self.set_team_composition_exclusion = set()

        # List of tuples given obtained by the database
        self.list_tuple_db_result = []

        # List of tuples (filtered and sorted to be inserted into the Treeview)
        self.list_tuples_to_be_inserted = []

        # TODO: NOT USED, USED IN self.threaded_format_list_tuples_to_be_inserted()
        # State of the clickable column names
        self.int_sort_by_team_composition_name = 1
        self.int_sort_by_team_composition_size = 0
        self.int_sort_by_trait_count_total = 2

        # State of the clickable column names (dynamic system)
        self.dict_key_column_name_formatted_value_index_state = {}

        # dict of the index state and it's the additional text that is associated with the state
        self.dict_key_index_state_value_state_text = {}

        # dict key champion name, dict champion containers
        self.dict_key_champion_name_value_button_champion_container = {}  # type: Dict[str, ButtonChampionContainer]

        # dict of trait names formatted and full trait name
        self.dict_key_trait_name_value_trait_name_full = {}  # type: Dict[str, str]

        # dict with the column name formatted and the full name of column name
        self.dict_key_column_name_formatted_value_column_name_full = {}

        # Values for the Entry widgets (Initial values)
        self.integer_team_composition_size_min = Integer(TEAM_COMPOSITION_SIZE_MAX)
        self.integer_team_composition_size_max = Integer(TEAM_COMPOSITION_SIZE_MAX)
        self.integer_trait_count_total_min = Integer(14)
        self.integer_trait_count_total_max = Integer(TRAIT_COUNT_TOTAL_MAX)

        # Checkbutton state (It exists because the .get() of the IntVar object must be in the main thread)
        self.int_checkbutton_trait_count_total = 0

        # Check if load_team_compositions is in the Queue because you can't check in a queue.
        self.bool_load_team_compositions_queued = False

        # Queue for the main thread to enforce sequential calls and prevent race conditions
        self.queue_main_thread_methods = Queue()
        # ---- Thread ----

        # Check if the threaded_method_handler is running
        self.threaded_method_handler_running = False

        # Lock for threading
        self.threading_lock = Lock()

        # Queue for thread to enforce sequential calls and prevent race conditions
        self.queue_threaded_methods = Queue()

        # Root for Tkinter
        self.root = Tk()

        # Background color
        self.root.config(background='white')

        # Title
        self.root.title("TFT Team Composition Combination Solver")

        # Default Minimum resolution
        self.root.minsize(1400, 800)

        # Default Resolution
        self.root.geometry("1400x800")

        # Style
        self.style = Style(self.root)

        # self.style.theme_use("vista")
        self.style.configure("Treeview",
                             background="white",
                             fieldbackground="white",
                             foreground="black")

        # Frames
        self.frame_main = Frame()
        self.frame_top = Frame(self.frame_main, background="white")
        self.frame_left = Frame(self.frame_main, background="white")
        self.frame_right = Frame(self.frame_main, background="white")
        self.tree_view = Treeview(self.frame_right)
        self.scrollbar_y = Scrollbar(self.frame_right, orient="vertical")
        self.scrollbar_x = Scrollbar(self.frame_right, orient="horizontal")

        # self.root.mainloop()
        self.mainloop_custom()

    def _load_pre_values(self):

        # Assign the the index state with state text
        self.dict_key_index_state_value_state_text = {
            0: "",
            1: "(Ascending)",
            2: "(Descending)"
        }

        # Format dict_champion_pool_transformed to match the names of the images of the champions
        self._format_champion_pool()

        # For every trait name in the trait_pool.dict_trait_pool make a dict key trait_name value trait_name_full
        for i in self.team_composition_solver.trait_pool.dict_trait_pool:
            self.dict_key_trait_name_value_trait_name_full[format_db_input(i)] = i

    def _load_initial_values(self):
        """
        A method to update the values of the GUI
        :return:
        """

        # Set the initial checkbutton state
        self.int_var_checkbutton.set(1)

        # Set initial Column name states
        self.dict_key_column_name_formatted_value_index_state["team_composition"] = 1
        self.dict_key_column_name_formatted_value_index_state["team_composition_size"] = 0
        self.dict_key_column_name_formatted_value_index_state["trait_count_total"] = 2

        # Add format SQLite query's result to to queue for threads to be executed by a thread
        self.queue_threaded_methods.put(
            CallablePreservedContainer(self.threaded_get_team_composition_based_on_current_set_from_db))

    def mainloop_custom(self):
        """
        Custom main loop to introduce more flexibility
        :return: None
        """

        # Load data for frames
        self._load_frame_data()

        try:
            while True:

                # Locking frame rate
                time.sleep(TIME_PER_FRAME)

                # If the threaded method is not running
                if not self.threaded_method_handler_running:
                    """
                    The threaded_method_handler should say when it's running because the main loop could be faster than 
                    the initialization the threaded_method_handler itself which would allow for multiple threads to be
                    running which is not ideal since the methods in the self.queue_threaded_methods should be sequential
                    """
                    # Allow for only 1 method to handle the queue of methods that can be threaded.
                    self.threaded_method_handler_running = True

                    # Method to handle threaded calls
                    Thread(target=self.threaded_method_handler).start()

                if not self.queue_main_thread_methods.empty():
                    # Method to handle main thread calls
                    self.main_thread_method_handler()

                # Update tkinter
                self.root.update_idletasks()
                self.root.update()

        # Handle update even though program is is dead
        except TclError as e:
            print(e)

    def threaded_method_handler(self):
        """
        Method to handle methods that can be threaded

        :return: None
        """

        # If the queue for threaded methods is not empty then run
        while not self.queue_threaded_methods.empty():
            # Run all callables in the queue
            callable_preserved_container = self.queue_threaded_methods.get()  # type: CallablePreservedContainer
            callable_preserved_container.run()
            self.queue_threaded_methods.task_done()

        # Thread should say when it's done
        self.threaded_method_handler_running = False

    def main_thread_method_handler(self):
        """
        Method to handle methods that must be ran on the main thread

        :return: None
        """
        # If the thread lock is not taken
        if not self.threading_lock.locked():
            """
            Even though the main thread is not lockable, you can still acquire the lock from the threads to prevent
            accessing instance variables being wrote to or read at the same time. Basically this prevents 
            Race conditions
            """

            # Acquire the thread lock
            # self.threading_lock.acquire()

            with self.threading_lock:
                # If the queue for the main thread is not empty
                while not self.queue_main_thread_methods.empty():
                    # Run all callables in the queue
                    callable_preserved_container = self.queue_main_thread_methods.get()  # type: CallablePreservedContainer
                    callable_preserved_container.run()
                    self.queue_main_thread_methods.task_done()

            # Release the thread lock
            # self.threading_lock.release()

    def _format_champion_pool(self):
        """
        Transforms the dict from the champion pool object to use the names based on the image files for the champions
        based on Riot's DataSet
        :return: None
        """
        for champion_name, champion_object in self.team_composition_solver.champion_pool.dict_champion_pool_name.items():
            self.dict_champion_pool_transformed[champion_object.name_simple] = champion_object

    def _load_frame_data(self):
        """
        loads the data for the frames used in the GUI
        :return:
        """

        self._load_pre_values()

        # Load the frames individually
        self._load_frame_setting()  # Top frame
        self._load_frame_images_and_buttons()  # Left frame
        self._load_frame_tree_view()  # Right frame

        # Load initial values
        self._load_initial_values()

        # Pack all frames
        self.frame_top.pack(side="top")
        self.frame_left.pack(side="top")
        self.frame_right.pack(side="bottom",
                              expand=True,
                              fill="both")
        self.scrollbar_y.pack(side="right",
                              fill="y")
        self.scrollbar_x.pack(side="bottom",
                              fill="x")
        self.tree_view.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.frame_main.pack(side="left",
                             expand=True,
                             fill="both")

    def _add_tkinter_buttons_champions_from_path(self, path_abs: str, position: Tuple[int, int]):
        """
        Create ButtonChampionContainer object based on the abs path of the champion image, position for the button on its
        corresponding frame, this object, and a champion object based on the name of the image from it's abs path
        :param path_abs: path to champion image
        :param position: position of the button on the grid
        :return: None
        """
        path_abs = os.path.abspath(path_abs)

        path_name = os.path.basename(path_abs)

        champion_name = str(path_name.split(".")[0])

        champion_object = self.dict_champion_pool_transformed.get(champion_name, None)

        # If the champion object does not exist then return False
        if champion_object is None:
            return False

        # Create a ButtonChampionContainer object
        temp_button_container = ButtonChampionContainer(self,
                                                        champion_object,
                                                        path_abs,
                                                        position
                                                        )

        # Add the ButtonChampionContainer object to the list to the dict that contains those objects
        self.dict_key_champion_name_value_button_champion_container[champion_name] = temp_button_container

        return True

    def _load_frame_images_and_buttons(self):
        """
        Gets the images for the champions in TFT and assigns their position on the frame that it will be on and their
        path to the image itself to a method to create a ButtonChampionContainer object.

        :return: None
        """
        row = 0
        column = 0

        # Walk through directory containing champion icons/images
        for dir_name, dir_sub_list, file_list in os.walk(DIR_CHAMPION_ICONS):
            for file in file_list:

                # Check the file is an image
                if any(file_format in file for file_format in ('.jpeg', '.png')):

                    # Create a ButtonChampionContainer object and check if it was successful
                    boolean = self._add_tkinter_buttons_champions_from_path(os.path.join(dir_name, file),
                                                                            (row, column)
                                                                            )
                    # If successful then increment grid positioning
                    if boolean:
                        column += 1
                        if column == COLUMN_LIMIT:
                            column = 0
                            row += 1

    def _load_frame_tree_view(self):
        """
        Load all Treeview related stuff

        Reference:
            Treeview's Column arguments
                https://docs.python.org/3/library/tkinter.ttk.html

        :return: None
        """
        # Create a scrollbar for the Treeview on y
        self.scrollbar_y.config(command=self.tree_view.yview)

        # Attach scrollbar_y to the Treeview
        self.tree_view.config(yscrollcommand=self.scrollbar_y.set, style="Treeview")

        # Create a scrollbar for the Treeview on x
        self.scrollbar_x.config(command=self.tree_view.xview)

        # Attach scrollbar_x to the Treeview
        self.tree_view.config(xscrollcommand=self.scrollbar_x.set, style="Treeview")

        # Allow for only showing headings
        self.tree_view["show"] = 'headings'

        # Bind clicking on the Treeview to allow for handling clicking
        self.tree_view.bind("<Double-Button-1>", lambda event: self._on_double_click_handle_event(event))
        self.tree_view.bind("<ButtonRelease-1>", lambda event: self._on_button_release_1_handle_event_v2(event))

        # Assigning the column names to reference
        self.tree_view["columns"] = ["team_composition", "team_composition_size", "trait_count_total",
                                     *self.dict_key_trait_name_value_trait_name_full]

        for column_name in self.tree_view["columns"]:
            self.dict_key_column_name_formatted_value_index_state[column_name] = 0

        self.dict_key_column_name_formatted_value_column_name_full = {
            "team_composition": "Team Composition",
            "team_composition_size": "Team Composition Size",
            "trait_count_total": "Trait Count Total"
        }

        self.dict_key_column_name_formatted_value_column_name_full.update(
            self.dict_key_trait_name_value_trait_name_full)

        # Hidden column
        self.tree_view.heading("#0", text="Hidden text", anchor="w")
        self.tree_view.column("#0", anchor="center", minwidth=0, stretch=True)

        # Assign the information for the team_composition column
        self.tree_view.heading("team_composition",
                               text=self.dict_key_column_name_formatted_value_column_name_full["team_composition"],
                               anchor="center")
        self.tree_view.column("team_composition", anchor="w", minwidth=500, stretch=True)

        # Assign the information for the team_composition_size column
        self.tree_view.heading("team_composition_size",
                               text=self.dict_key_column_name_formatted_value_column_name_full[
                                   "team_composition_size"],
                               anchor="center")
        self.tree_view.column("team_composition_size", anchor="center", minwidth=35, width=35, stretch=True)

        # Assign the information for the trait_count_total column
        self.tree_view.heading("trait_count_total",
                               text=self.dict_key_column_name_formatted_value_column_name_full[
                                   "trait_count_total"],
                               anchor="center")
        self.tree_view.column("trait_count_total", anchor="center", minwidth=35, width=35, stretch=True)

        for trait_name, trait_name_full in self.dict_key_trait_name_value_trait_name_full.items():
            self.tree_view.heading(trait_name, text=trait_name_full, anchor="w")
            self.tree_view.column(trait_name, anchor="center", minwidth=35, width=35, stretch=True)

    def _load_frame_setting(self):
        """
        Lead the top frame stuff

        Reference:
            Understanding trace's callback on StringVar()
                https://stackoverflow.com/questions/29690463/what-are-the-arguments-to-tkinter-variable-trace-method-callbacks

            Entry validateCommand
                https://www.tcl.tk/man/tcl8.5/TkCmd/entry.htm#M-validate
                https://stackoverflow.com/questions/8959815/restricting-the-value-in-tkinter-entry-widget

            Blold Label text
                https://stackoverflow.com/questions/46495160/make-a-label-bold-tkinter

            Checkbutton and it's documentation
                http://effbot.org/tkinterbook/checkbutton.htm

        :return: None
        """

        # Labels for the Entries
        self.label_team_composition_size = Label(self.frame_top,
                                                 text="Team Composition Min/Max",
                                                 font=FONT_DEFAULT).grid(row=0, column=0)

        self.label_trait_count_total = Label(self.frame_top,
                                             text="Trait Count Total Min/Max",
                                             font=FONT_DEFAULT).grid(row=0, column=3)

        """
        Creation of StringVars and modifying them to call a method with their corresponding instance var and itself
        """
        self.string_var_team_composition_size_min = StringVar()
        self.string_var_team_composition_size_min.set(self.integer_team_composition_size_min.get())
        self.string_var_team_composition_size_min.trace(
            "w", lambda internal_variable_name,
                        index,
                        operation: self._string_var_handler(internal_variable_name,
                                                            index,
                                                            operation,
                                                            self.string_var_team_composition_size_min,
                                                            self.integer_team_composition_size_min
                                                            )
        )

        self.string_var_team_composition_size_max = StringVar()
        self.string_var_team_composition_size_max.set(self.integer_team_composition_size_max.get())
        self.string_var_team_composition_size_max.trace(
            "w", lambda internal_variable_name,
                        index,
                        operation: self._string_var_handler(internal_variable_name,
                                                            index,
                                                            operation,
                                                            self.string_var_team_composition_size_max,
                                                            self.integer_team_composition_size_max
                                                            )
        )

        self.string_var_trait_count_total_min = StringVar()
        self.string_var_trait_count_total_min.set(self.integer_trait_count_total_min.get())
        self.string_var_trait_count_total_min.trace(
            "w", lambda internal_variable_name,
                        index,
                        operation: self._string_var_handler(internal_variable_name,
                                                            index,
                                                            operation,
                                                            self.string_var_trait_count_total_min,
                                                            self.integer_trait_count_total_min
                                                            )
        )

        self.string_var_trait_count_total_max = StringVar()
        self.string_var_trait_count_total_max.set(self.integer_trait_count_total_max.get())
        self.string_var_trait_count_total_max.trace(
            "w", lambda internal_variable_name,
                        index,
                        operation: self._string_var_handler(internal_variable_name,
                                                            index,
                                                            operation,
                                                            self.string_var_trait_count_total_max,
                                                            self.integer_trait_count_total_max
                                                            )
        )

        """
        Creation of Entries and assigning them their corresponding StringVar and location on the grid as well as their
        setting
        
        """
        self.entry_team_composition_size_min = Entry(self.frame_top,
                                                     width=5,
                                                     # validatecommand=self._validate_entry_int,
                                                     textvariable=self.string_var_team_composition_size_min
                                                     ).grid(row=0, column=1)

        self.entry_team_composition_size_max = Entry(self.frame_top,
                                                     width=5,
                                                     textvariable=self.string_var_team_composition_size_max
                                                     ).grid(row=0, column=2)

        self.entry_trait_count_total_min = Entry(self.frame_top,
                                                 width=5,
                                                 textvariable=self.string_var_trait_count_total_min
                                                 ).grid(row=0, column=4)

        self.entry_trait_count_total_max = Entry(self.frame_top,
                                                 width=5,
                                                 textvariable=self.string_var_trait_count_total_max
                                                 ).grid(row=0, column=5)

        # Label for the Checkbutton object
        self.label_trait_count_total = Label(self.frame_top,
                                             text="Trait Count Total Discrete",
                                             font=FONT_DEFAULT)

        self.label_trait_count_total.grid(row=0, column=6)

        # IntVar object with the state of the Checkbutton object
        self.int_var_checkbutton = IntVar()

        # Checkbutton object
        self.checkbutton_trait_count_total = Checkbutton(self.frame_top,
                                                         command=self._checkbutton_trait_count_total_handler,
                                                         variable=self.int_var_checkbutton,
                                                         )

        self.checkbutton_trait_count_total.grid(row=0, column=7)

    def _checkbutton_trait_count_total_handler(self):
        """
        Handles the Checkbutton object self.checkbutton_trait_count_total and its state

        It's the reason why self.int_checkbutton_trait_count_total exists
        because self.int_var_checkbutton.get() cannot run out of the main thread

        :return: None
        """

        # State of the Checkbutton object
        state_checkbutton_trait_count_total = self.int_var_checkbutton.get()

        if state_checkbutton_trait_count_total == 1:
            # self.label_trait_count_total.config(text="Trait Count Total Discrete")
            self.int_checkbutton_trait_count_total = 1

        elif state_checkbutton_trait_count_total == 0:
            # self.label_trait_count_total.config(text="Trait Count Total Discrete")
            self.int_checkbutton_trait_count_total = 0

        self.queue_threaded_methods.put(
            CallablePreservedContainer(self.threaded_format_list_tuples_to_be_inserted_v2))

    @staticmethod
    def _validate_entry_int(action: int, index: int, value_if_allowed: str, prior_value: str, text: str,
                            validation_type, trigger_type, widget_name):
        """
        Validate the text inside of the Entry, not used.

        Reference:
            Restricting value on Tkinter Entry via validatecommand
                https://stackoverflow.com/questions/8959815/restricting-the-value-in-tkinter-entry-widget

            validatecommand's arguments
                https://www.tcl.tk/man/tcl8.5/TkCmd/entry.htm#M-validate

        :param action: Type of action: 1 for insert, 0 for delete, or -1 for focus, forced or textvariable validation.
        :param index: Index of char string to be inserted/deleted, if any, otherwise -1.
        :param value_if_allowed: The value of the entry if the edit is allowed. If you are configuring the entry widget
                                    to have a new textvariable, this will be the value of that textvariable.
        :param prior_value: The current value of entry prior to editing.
        :param text: The text string being inserted/deleted, if any, {} otherwise.
        :param validation_type: The type of validation currently set.
        :param trigger_type: The type of validation that triggered the callback (key, focusin, focusout, forced).
        :param widget_name: The name of the entry widget.
        :return: None
        """

        if value_if_allowed.isnumeric():
            return True
        return False

    def _string_var_handler(self, internal_variable_name, index, operation, string_var: StringVar,
                            integer_object: Integer):
        """
        Handle StringVar's on change method calls, those that call this method do not give an event as an argument which
        is why they don't have an on handle type method

        Reference:
            Event call back on StringVar trace method, How do I get an event callback when a Tkinter Entry widget is modified?
                https://stackoverflow.com/questions/6548837/how-do-i-get-an-event-callback-when-a-tkinter-entry-widget-is-modified

            Arguments given by StringVar.trace()'s callback
                https://stackoverflow.com/questions/29690463/what-are-the-arguments-to-tkinter-variable-trace-method-callbacks

        :param internal_variable_name: Internal variable name
        :param index: Index into that list of of the first argument?
        :param operation: The operation given by the callback
        :param string_var: StringVar object
        :param integer_object: Integer object
        :return: None
        """
        # print(internal_variable_name, index, operation, string_var.get(), type(instance_var))

        # Get the value given by StringVar
        string_var_value = string_var.get()

        # All for empty entry
        if string_var_value == "":
            pass

        # Allow only ints as the value of the string_var_value
        elif string_var_value.isnumeric():

            # Make string as a int
            int_value = int(string_var_value)

            # Set the Integer object's int value
            integer_object.set(int_value)

            # Add SQlite query method to queue for threads to be executed by a thread
            self.queue_threaded_methods.put(
                CallablePreservedContainer(self.threaded_get_team_composition_based_on_current_set_from_db))

        # Replace string_var_value value with the integer_object.get() if letters are given
        else:
            string_var.set(integer_object.get())

    def clear_tree_view(self):
        """
        Must be called the main thread
        Clears all children in the Treeview

        :return: None
        """

        [self.tree_view.delete(child) for child in self.tree_view.get_children()]

    # TODO: NOT USED, REPLACED WITH v2
    def _on_button_release_1_handle_event(self, event):
        """
        Handle all single click related events on the Treeview

        Reference:
            Clickable on Treeview handling
                https://stackoverflow.com/questions/38666326/treeview-tkinter-widget-clickable-links

        :param event: event given by the thing that called this method
        :return: None
        """
        # Event object passed
        # print(event)

        # Get the clicked child's input_id tuple
        input_id_tuple = self.tree_view.selection()
        # print(input_id_tuple)

        # Get the child's values based on the input_id
        input_item = self.tree_view.item(input_id_tuple)
        # print(input_item)

        # Get the name of the region that was clicked
        region_name = self.tree_view.identify("region", event.x, event.y)  # type: str
        # print(region_name)

        # Get the column number with starting with a #
        column_number = self.tree_view.identify_column(event.x)  # type: str
        # print(column_number)

        # The input_id
        input_id = self.tree_view.identify_row(event.y)  # type: str
        # print(input_id)

        if region_name == "heading" and column_number == "#1":
            self.int_sort_by_team_composition_name = (self.int_sort_by_team_composition_name + 1) % 3
            # print(self.int_sort_by_champion_name)
            self.queue_threaded_methods.put(
                CallablePreservedContainer(self.threaded_format_list_tuples_to_be_inserted_v2))

        # Handles column team_composition_size
        if region_name == "heading" and column_number == "#2":
            self.int_sort_by_team_composition_size = (self.int_sort_by_team_composition_size + 1) % 3
            # print(self.int_sort_by_team_composition_size)
            self.queue_threaded_methods.put(
                CallablePreservedContainer(self.threaded_format_list_tuples_to_be_inserted_v2))

        # Handles column trait_count_total
        if region_name == "heading" and column_number == "#3":
            self.int_sort_by_trait_count_total = (self.int_sort_by_trait_count_total + 1) % 3
            # print(self.int_sort_by_trait_count_total)
            self.queue_threaded_methods.put(
                CallablePreservedContainer(self.threaded_format_list_tuples_to_be_inserted_v2))

    def _on_button_release_1_handle_event_v2(self, event):
        """
           Handle all single click related events on the Treeview

           Reference:
               Clickable on Treeview handling
                   https://stackoverflow.com/questions/38666326/treeview-tkinter-widget-clickable-links

           :param event: event given by the thing that called this method
           :return: None
           """
        # Event object passed
        # print(event)

        # Get the clicked child's input_id tuple
        input_id_tuple = self.tree_view.selection()
        # print(input_id_tuple)

        # Get the child's values based on the input_id
        input_item = self.tree_view.item(input_id_tuple)
        # print(input_item)

        # Get the name of the region that was clicked
        region_name = self.tree_view.identify("region", event.x, event.y)  # type: str
        # print(region_name)

        # Get the column number with starting with a #
        column_number = self.tree_view.identify_column(event.x)  # type: str
        # print(column_number)

        # The input_id
        input_id = self.tree_view.identify_row(event.y)  # type: str
        # print(input_id)

        # For each index with column_name and index_state
        for index, tuple_column_name_and_index_state in enumerate(
                self.dict_key_column_name_formatted_value_index_state.items()):

            """
            If the region name of a Treeview is a heading and the Treeview column_number == index + 1 
            because #0 is not a column actual by the Treeview object
            """
            if region_name == "heading" and column_number == "#{}".format(index + 1):
                # column_name based on Treeview's reference
                column_name = format_db_input(tuple_column_name_and_index_state[0])

                # Increment self.dict_key_column_name_value_index_state's index_state
                self.dict_key_column_name_formatted_value_index_state[column_name] = \
                    (self.dict_key_column_name_formatted_value_index_state[column_name] + 1) % len(
                        self.dict_key_index_state_value_state_text)

                # Add to threaded queue self.threaded_format_list_tuples_to_be_inserted_v2
                self.queue_threaded_methods.put(
                    CallablePreservedContainer(self.threaded_format_list_tuples_to_be_inserted_v2))

        return event, input_id_tuple, input_item, region_name, column_number, input_id

    def _on_double_click_handle_event(self, event):
        """
        Handles all double click related events on the Treeview

        Reference:
            Clickable on Treeview handling
                https://stackoverflow.com/questions/38666326/treeview-tkinter-widget-clickable-links

        :param event: event given by the thing that called this method
        :return: None
        """
        # Event object passed
        # print(event)

        # Get the clicked child's input_id tuple
        input_id_tuple = self.tree_view.selection()
        # print(input_id_tuple)

        # Get the child's values based on the input_id
        input_item = self.tree_view.item(input_id_tuple)
        # print(input_item)

        # Get the name of the region that was clicked
        region_name = self.tree_view.identify("region", event.x, event.y)  # type: str
        # print(region_name)

        # Get the column number with starting with a #
        column_number = self.tree_view.identify_column(event.x)  # type: str
        # print(column_number)

        # The input_id
        input_id = self.tree_view.identify_row(event.y)  # type: str
        # print(input_id)

        return event, input_id_tuple, input_item, region_name, column_number, input_id

    # TODO: NOT USED
    def add_champion_to_set_team_composition_current(self, champion_name):
        """
        Add the champion name to self.set_team_composition_current based on the champion name given which is
        primarily called by the champion button

        :param champion_name: champion name
        :return: None
        """

        # Add champion name to self.set_team_composition_current
        self.set_team_composition_current.add(champion_name)

        # Add SQlite query method to queue for threads to be executed by a thread
        self.queue_threaded_methods.put(
            CallablePreservedContainer(self.threaded_get_team_composition_based_on_current_set_from_db))

    # TODO: NOT USED
    def remove_champion_from_set_team_composition_current(self, champion_name):
        """
        Remove the champion name to self.set_team_composition_current based on the champion name given which is
        primarily called by the champion button

        :param champion_name: champion name
        :return: None
        """

        # Remove champion name from self.set_team_composition_current
        self.set_team_composition_current.remove(champion_name)

        # Add SQlite query method to queue for threads to be executed by a thread
        self.queue_threaded_methods.put(
            CallablePreservedContainer(self.threaded_get_team_composition_based_on_current_set_from_db))

    # TODO: NOT USED
    def add_champion_to_set_team_composition_exclusion(self, champion_name):
        """
        Add the champion name to the self.set_team_composition_exclusion based on the champion name given which is
        primarily called by the champion button

        :param champion_name: champion name
        :return: None
        """

        # Add champion name to self.set_team_composition_exclusion
        self.set_team_composition_exclusion.add(champion_name)

        # Add SQlite query method to queue for threads to be executed by a thread
        self.queue_threaded_methods.put(
            CallablePreservedContainer(self.threaded_get_team_composition_based_on_current_set_from_db))

    # TODO: NOT USED
    def remove_champion_from_set_team_composition_exclusion(self, champion_name):
        """
        Remove the champion name to the self.set_team_composition_exclusion based on the champion name given which is
        primarily called by the champion button

        :param champion_name: champion name
        :return: None
        """

        # Remove champion name to self.set_team_composition_exclusion
        self.set_team_composition_exclusion.remove(champion_name)

        # Add SQlite query method to queue for threads to be executed by a thread
        self.queue_threaded_methods.put(
            CallablePreservedContainer(self.threaded_get_team_composition_based_on_current_set_from_db))

    @timer
    def threaded_get_team_composition_based_on_current_set_from_db(self):
        """
        This should be threaded
        Get the team composition from the database based on the self.set_team_composition_selected
        :return: None
        """

        print("Running DB Query")

        # Acquire thread lock
        # self.threading_lock.acquire()

        with self.threading_lock:
            # Run database query
            self.list_tuple_db_result = self.team_composition_solver.sqlite_handler_team_composition_solver.get_pickled_list_tuple_champion_composition(
                self.set_team_composition_current,
                self.set_team_composition_exclusion,
                self.integer_team_composition_size_min.get(),
                self.integer_team_composition_size_max.get(),
                self.integer_trait_count_total_min.get(),
                self.integer_trait_count_total_max.get()
            )

            # Add format SQlite query's result to to queue for threads to be executed by a thread
            self.queue_threaded_methods.put(
                CallablePreservedContainer(self.threaded_format_list_tuples_to_be_inserted_v2))

        # Release thread lock
        # self.threading_lock.release()

    # TODO: NOT USED, REPLACED WITH v2
    def threaded_format_list_tuples_to_be_inserted(self):
        """
        This should be threaded

        Format the results of the SQLite query to be inserted into the Treeview

        :return: None
        """
        self.list_tuples_to_be_inserted = []

        t1_a = time.time()

        # Format the tuples from self.list_tuple_db_result
        for tuple_db_result in self.list_tuple_db_result:  # type: list
            list_temp = []

            # Tuple of the team composition sorted by name then cost
            tuple_team_composition_sorted = self.team_composition_solver.team_composition_container_factory.sort_tuple_team_composition(
                tuple_db_result[1])

            # String of the team composition names
            team_composition_names = ", ".join(tuple_team_composition_sorted)

            # Team composition
            list_temp.append(team_composition_names)  # Column 1 on Treeview

            # Team Composition Size
            list_temp.append(tuple_db_result[2])  # Column 2 on Treeview

            # Trait Count Total
            list_temp.append(tuple_db_result[3])  # Column 3 on Treeview

            # WARNING: THIS IS USED ONLY IF TRAITS ARE ADDED TO THE DB
            # for i in range(2, len(tuple_db_result)):
            #     list_temp.append(tuple_db_result[i])

            # Temporary TeamCompositionContainer object for it's traits
            tuple_team_composition_container = self.team_composition_solver.team_composition_container_factory.get_team_composition_container(
                tuple_db_result[1])

            """
            It's actually faster to make a TeamCompositionContainer object then get its traits rather than
            the massive join table in SQLite as it's load time is very long.
            """
            # For each index with trait from the trait_pool
            for index, trait in enumerate(self.team_composition_solver.trait_pool.dict_trait_pool):

                """
                # += 4 because the first 3 index are 
                Team composition, Team Composition Size, and Trait Count Total
                """
                index += 4

                # Team composition trait
                team_composition_trait = tuple_team_composition_container.dict_trait_count_discrete.get(trait, False)

                # If the Team composition has the trait
                if team_composition_trait is not False:
                    list_temp.append(str(team_composition_trait))

                # If it does not have the trait then leave it empty
                else:
                    list_temp.append("")

            # Add the tuple to list of tuples to tbe inserted
            self.list_tuples_to_be_inserted.append(list_temp)

        t1_b = time.time()
        print("t1 Read from self.list_tuple_db_result", t1_b - t1_a)

        t2_a = time.time()
        # TODO: CAN SIMPLIFY via dict and method
        # Sort list_inserted_information by Team Composition (Ascending)
        if self.int_sort_by_team_composition_name == 1:

            # Sort the list of tuples by the tuple's first item using python's sorting algorithm
            self.list_tuples_to_be_inserted.sort(key=lambda list_item: list_item[0])

            # Update the appropriate column name
            self.queue_main_thread_methods.put(CallablePreservedContainer(self.tree_view.heading,
                                                                          "team_composition",
                                                                          text="Team Composition (Ascending)"))
        # Sort list_inserted_information by Team Composition (Descending)
        elif self.int_sort_by_team_composition_name == 2:

            # Sort the list of tuples by the tuple's first item in reverse using python's sorting algorithm
            self.list_tuples_to_be_inserted.sort(key=lambda list_item: list_item[0], reverse=True)

            # Update the appropriate column name
            self.queue_main_thread_methods.put(CallablePreservedContainer(self.tree_view.heading,
                                                                          "team_composition",
                                                                          text="Team Composition (Descending)"))
        else:
            # Update the appropriate column name
            self.queue_main_thread_methods.put(CallablePreservedContainer(self.tree_view.heading,
                                                                          "team_composition",
                                                                          text="Team Composition"))
        t2_b = time.time()

        print("t2 Sort by Team Composition", t2_b - t2_a)

        t3_a = time.time()
        # TODO: CAN SIMPLIFY via dict and method
        # Sort list_inserted_information by Team Composition Size (Ascending)
        if self.int_sort_by_team_composition_size == 1:

            # Sort the list of tuples by the tuple's second item using python's sorting algorithm
            self.list_tuples_to_be_inserted.sort(key=lambda list_item: list_item[1])

            # Update the appropriate column name
            self.queue_main_thread_methods.put(CallablePreservedContainer(self.tree_view.heading,
                                                                          "team_composition_size",
                                                                          text="Team Composition Size (Ascending)"))

        # Sort list_inserted_information by Team Composition Size (Descending)
        elif self.int_sort_by_team_composition_size == 2:

            # Sort the list of tuples by the tuple's second item in reverse using python's sorting algorithm
            self.list_tuples_to_be_inserted.sort(key=lambda list_item: list_item[1], reverse=True)

            # Update the appropriate column name
            self.queue_main_thread_methods.put(CallablePreservedContainer(self.tree_view.heading,
                                                                          "team_composition_size",
                                                                          text="Team Composition Size (Descending)"))
        else:
            # Update the appropriate column name
            self.queue_main_thread_methods.put(CallablePreservedContainer(self.tree_view.heading,
                                                                          "team_composition_size",
                                                                          text="Team Composition Size"))
        t3_b = time.time()

        print("t3 Sort by Team Composition size", t3_b - t3_a)

        t4_a = time.time()
        # TODO: CAN SIMPLIFY via dict and method
        # Sort list_inserted_information by Trait Count Total (Ascending)
        if self.int_sort_by_trait_count_total == 1:

            # Sort the list of tuples by the tuple's third item using python's sorting algorithm
            self.list_tuples_to_be_inserted.sort(key=lambda list_item: list_item[2])

            # Update the appropriate column name
            self.queue_main_thread_methods.put(CallablePreservedContainer(self.tree_view.heading,
                                                                          "trait_count_total",
                                                                          text="Trait Count Total (Ascending)"))

        # Sort list_inserted_information by Trait Count Total (Descending)
        elif self.int_sort_by_trait_count_total == 2:

            # Sort the list of tuples by the tuple's third item in reverse using python's sorting algorithm
            self.list_tuples_to_be_inserted.sort(key=lambda list_item: list_item[2], reverse=True)

            # Update the appropriate column name
            self.queue_main_thread_methods.put(CallablePreservedContainer(self.tree_view.heading,
                                                                          "trait_count_total",
                                                                          text="Trait Count Total (Descending)"))
        else:
            # Update the appropriate column name
            self.queue_main_thread_methods.put(CallablePreservedContainer(self.tree_view.heading,
                                                                          "trait_count_total",
                                                                          text="Trait Count Total"))
        t4_b = time.time()

        print("t4 Sort by Trait Count Total", t4_b - t4_a)

        # Add load_team_compositions to queue for the main thread
        self.add_load_team_compositions_to_thread_main_queue()

    def threaded_format_list_tuples_to_be_inserted_v2(self):
        """
         This should be threaded

         Format the results of the SQLite query to be inserted into the Treeview

         :return: None
        """
        self.list_tuples_to_be_inserted = []

        t1_a = time.time()

        # Format the tuples from self.list_tuple_db_result
        for tuple_db_result in self.list_tuple_db_result:  # type: list
            list_temp = []

            # Tuple of the team composition sorted by name then cost
            tuple_team_composition_sorted = self.team_composition_solver.team_composition_container_factory.sort_tuple_team_composition(
                tuple_db_result[1])

            # String of the team composition names
            team_composition_names = ", ".join(tuple_team_composition_sorted)

            # Team composition
            list_temp.append(team_composition_names)  # Column 1 on Treeview

            # Team Composition Size
            list_temp.append(tuple_db_result[2])  # Column 2 on Treeview

            # Trait Count Total
            list_temp.append(tuple_db_result[3])  # Column 3 on Treeview

            # Temporary TeamCompositionContainer object for it's traits
            tuple_team_composition_container = self.team_composition_solver.team_composition_container_factory.get_team_composition_container(
                tuple_db_result[1])

            """
            It's actually faster to make a TeamCompositionContainer object then get its traits rather than
            the massive join table in SQLite as it's load time is very long.
            """
            # For each index with trait from the trait_pool
            for index, trait in enumerate(self.team_composition_solver.trait_pool.dict_trait_pool):

                """
                # += 4 because the first 3 index are 
                Team composition, Team Composition Size, and Trait Count Total
                """
                index += 4

                # Team composition trait
                team_composition_trait = None

                # Use the dict_trait_count
                if self.int_checkbutton_trait_count_total == 0:
                    # Team composition trait
                    team_composition_trait = tuple_team_composition_container.dict_trait_count.get(trait, False)

                # Use the dict_trait_count_discrete
                elif self.int_checkbutton_trait_count_total == 1:
                    # Team composition trait
                    team_composition_trait = tuple_team_composition_container.dict_trait_count_discrete.get(trait,
                                                                                                            False)
                # If the Team composition has the trait
                if team_composition_trait is not False:
                    list_temp.append(str(team_composition_trait))

                # If it does not have the trait then leave the cell empty
                else:
                    list_temp.append("")

            # Add the tuple to list of tuples to tbe inserted
            self.list_tuples_to_be_inserted.append(list_temp)

        # Enumerate each tuple containing the column_name_formatted and index_state
        for index, tuple_column_name_index_state in enumerate(
                self.dict_key_column_name_formatted_value_index_state.items()):

            # Get the column name from the tuple to match the Treeview's Column name
            column_name_formatted = tuple_column_name_index_state[0]

            # print(self.dict_key_column_name_formatted_value_index_state.get(column_name_formatted))
            # print(index)

            # Handle the state 0 (No sort on column)
            state_0 = 0
            # Check the index_state of the given column_name
            if self.dict_key_column_name_formatted_value_index_state.get(column_name_formatted) == state_0:
                # Queue a self.tree_view.heading text change
                self.queue_main_thread_methods.put(CallablePreservedContainer(
                    self.tree_view.heading,
                    column_name_formatted,
                    text="{} {}".format(
                        self.dict_key_column_name_formatted_value_column_name_full.get(
                            column_name_formatted),
                        self.dict_key_index_state_value_state_text.get(state_0))))

            # Handle the state 0 (Sort Ascending)
            state_1 = 1
            # Check the index_state of the given column_name
            if self.dict_key_column_name_formatted_value_index_state.get(column_name_formatted) == state_1:
                # Sort the list of tuples by the tuple's index item using python's sorting algorithm
                self.list_tuples_to_be_inserted.sort(key=lambda list_item: list_item[index])

                # Queue a self.tree_view.heading text change
                self.queue_main_thread_methods.put(CallablePreservedContainer(
                    self.tree_view.heading,
                    column_name_formatted,
                    text="{} {}".format(
                        self.dict_key_column_name_formatted_value_column_name_full.get(
                            column_name_formatted),
                        self.dict_key_index_state_value_state_text.get(state_1))))

            # Handle the state 0 (Sort Descending)
            state_2 = 2
            # Check the index_state of the given column_name
            if self.dict_key_column_name_formatted_value_index_state.get(column_name_formatted) == state_2:
                # Sort the list of tuples by the tuple's index item in reverse using python's sorting algorithm
                self.list_tuples_to_be_inserted.sort(key=lambda list_item: list_item[index], reverse=True)

                # Queue a self.tree_view.heading text change
                self.queue_main_thread_methods.put(CallablePreservedContainer(
                    self.tree_view.heading,
                    column_name_formatted,
                    text="{} {}".format(
                        self.dict_key_column_name_formatted_value_column_name_full.get(
                            column_name_formatted),
                        self.dict_key_index_state_value_state_text.get(state_2))))

        # Add load_team_compositions to queue for the main thread
        self.add_load_team_compositions_to_thread_main_queue()

    def clear_values(self):
        """
        Clear the Treeview values and the list_tuples_to_be_inserted that are used to be inserted into the Treeview

        :return: None
        """
        self.clear_tree_view()

    @timer
    def load_team_compositions(self):
        """
        Insert the list of tuples that will be in the Treeview

        Updating the view
        :return: None
        """
        self.clear_values()

        t5_a = time.time()

        # Insert the tuples into Treeview
        for i in self.list_tuples_to_be_inserted:
            self.tree_view.insert("", END, text="test thing", values=i)
        t5_b = time.time()

        print("t5 Insert into Treeview", t5_b - t5_a)

        # Boolean to show if this method is out of the queue for the main thread
        self.bool_load_team_compositions_queued = False

    def add_load_team_compositions_to_thread_main_queue(self):
        """
        Put self.load_team_compositions in queue only if it's not in queue

        :return: None
        """

        # If load_team_compositions is not in the queue for the main thread
        if not self.bool_load_team_compositions_queued:
            # State that the method is in the queue
            self.bool_load_team_compositions_queued = True

            # Add the method to the queue
            self.queue_main_thread_methods.put(CallablePreservedContainer(self.load_team_compositions))


class ButtonChampionContainer:
    def __init__(self,
                 team_composition_solver_gui: TeamCompositionSolverGUI,
                 champion: Champion,
                 path_abs: str,
                 position: tuple):
        """
        Champion object, Button, and Image container

        :param team_composition_solver_gui: TeamCompositionSolverGUI to access it's commands and variables
        :param champion: champion object
        :param path_abs: path to champion image
        :param position: position of the button on the grid
        """
        self.team_composition_solver_gui = team_composition_solver_gui
        self.champion = champion

        self.tk_photo_image = PhotoImage(file=path_abs)
        self.tk_button = Button(team_composition_solver_gui.frame_left)

        self.tk_button.grid(row=position[0], column=position[1])

        self.button_state = 0

        self.tk_button.config(text=self.champion.name,
                              image=self.tk_photo_image,
                              command=self.toggle_selected_switch,
                              borderwidth=6,
                              compound="center",
                              fg="white",
                              font=FONT_BUTTON_TEXT,
                              bg="black")

        # Alternative bind
        # self.tk_button.bind('<Button-1>', self.toggle_selected_switch)

    def toggle_selected_switch(self, *args):
        """
        Explicit toggle switch to determine if the button is toggled or not

        :param args: additional arguments if given such as event
        :return: self.toggle
        """

        self.button_state = (self.button_state + 1) % 3

        if self.button_state == 0:
            self.tk_button.config(bg="black")

            # Remove champion from set_team_composition_exclusion
            # self.team_composition_solver_gui.remove_champion_from_set_team_composition_exclusion(self.champion.name)

            self.team_composition_solver_gui.set_team_composition_exclusion.remove(self.champion.name)

        elif self.button_state == 1:
            self.tk_button.config(bg="yellow")

            # Add champion to set_team_composition_current
            # self.team_composition_solver_gui.add_champion_to_set_team_composition_current(self.champion.name)

            self.team_composition_solver_gui.set_team_composition_current.add(self.champion.name)

        elif self.button_state == 2:
            self.tk_button.config(bg="red")

            # Remove champion from set_team_composition_current
            # self.team_composition_solver_gui.remove_champion_from_set_team_composition_current(self.champion.name)

            self.team_composition_solver_gui.set_team_composition_current.remove(self.champion.name)

            # Add champion to set_team_composition_exclusion
            # self.team_composition_solver_gui.add_champion_to_set_team_composition_exclusion(self.champion.name)

            self.team_composition_solver_gui.set_team_composition_exclusion.add(self.champion.name)

        # Add SQlite query method to queue for threads to be executed by a thread
        self.team_composition_solver_gui.queue_threaded_methods.put(
            CallablePreservedContainer(
                self.team_composition_solver_gui.threaded_get_team_composition_based_on_current_set_from_db))

        # Return toggle value
        return self.button_state
