from habit import Habit, PeriodLength
from storage import StorageInterface, StorageKind, OrgStorage
from pathlib import Path
from typing import Optional
from datetime import datetime

from log import log

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

    def __init__(self, store_kind: StorageKind, file: Optional[str] = None):
        """
        App constructor

        Takes in a StorageKind and a file if needed to use as primary storage implementation.
        """
        # TODO: Reusable? Own function?
        if store_kind == StorageKind.org:
            if file:
                self.storage = OrgStorage(file)
            else:
                print("OrgStorage requires a file")
                return
        else:
            print("Unknown StorageKind")
            return
        self.read()

    def read(self):
        """
        Uses self.storage to read in habits into self.habits.
        """
        # TODO: Ensure habit names are unique
        self.habits = self.storage.read()

    def save(self):
        """
        Uses self.storage to save self.habits.
        """
        self.storage.save(self.habits)

    def read_from(self, file: str, store_kind: StorageKind):
        """
        !! Not Implemented Yet !!
        Reads in habits from the given file using giving Storage implementation.
        """
        print("HabitTracker.read_from not implemented yet.")

    def save_as(self, file: str, store_kind: StorageKind):
        """
        !! Not Implemented Yet !!
        Saves habits to given file using giving Storage implementation.
        """
        print("HabitTracker.save_as implemented yet.")

    def get_completed_str(self) -> list[str]:
        comp = list()
        for h in self.habits:
            if h.completed:
                comp.append(repr(h))
        return comp

    def get_uncompleted_str(self) -> list[str]:
        uncomp = list()
        for h in self.habits:
            if not h.completed:
                uncomp.append(repr(h))
        return uncomp

    def complete(self, n: str):
        log("Habit to be marked complete:" + n)
        for h in self.habits:
            if n == repr(h):
                h.completed_times.append(datetime)
                h.completed = True
                log("After marked:\n" + str(h))
                break

    def addHabit(self, name: str, symbol: str, period_length: PeriodLength):
        self.habits.append(Habit.new(name, symbol, period_length))

    def deleteHabit(self, n: str):
        for h in self.habits:
            if n == repr(h):
                self.habits.remove(h)
