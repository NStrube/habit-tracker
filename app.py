from habit import Habit
from storage import StorageInterface

class HabitTracker:
    """
    The state of the app.

    Attributes
    ----------
    habits: list[Habit]
        All habits known by the app.
    storage: StorageInterface
        Handles read and save of habits.
        See 'help(StorageInterface)' for more information.

    Methods
    -------
    read():
        Uses self.storage to read in habits into self.habits.
    save():
        Uses self.storage to save self.habits.
    read_from(file: str):
        !! Not Implemented Yet !!
        Reads in habits from the given file.
    save_as(file: str):
        !! Not Implemented Yet !!
        Saves habits to given file.

    """
    habits: list[Habit] = list()
    storage: StorageInterface

    # TODO: If file taken out of read and save, take in enum and for read_from save_as as well
    def __init__(self, storage: StorageInterface):
        """
        App constructor

        Takes in a StorageInterface to use as primary storage medium.
        """
        self.storage = storage
        self.read()

    def read(self):
        """
        Uses self.storage to read in habits into self.habits.
        """
        self.habits = self.storage.read(self.storage.file)


    def read_from(self, file: str):
        """
        !! Not Implemented Yet !!
        Reads in habits from the given file.
        """
        # TODO: mypy not recognizing Exception
        # raise Exception('NotImplementedYet')
        print("HabitTracker.read_from not implemented yet.")

    def save(self):
        """
        Uses self.storage to save self.habits.
        """
        self.storage.save(self.storage.file, self.habits)

    def save_as(self, file: str):
        """
        !! Not Implemented Yet !!
        Saves habits to given file.
        """
        # TODO: mypy not recognizing Exception
        # raise Exception('NotImplementedYet')
        print("HabitTracker.save_as implemented yet.")
