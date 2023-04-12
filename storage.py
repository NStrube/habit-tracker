import abc
from typing import Protocol
from habit import Habit
from pathlib import Path

class StorageInterface(Protocol):
    """
    The storage interface for the habit tracking app.

    Attributes
    ----------

    Methods
    ------
    read(str) -> list[Habit]:
        Reads habits.
    save(str) -> list[Habit]:
        Saves habits.
    """
    # TODO: can't take file cuz DB don't use that? So remove it?
    @staticmethod
    def read(file: Path) -> list[Habit]:
        """Reads in the habits from file 'file'."""
        raise NotImplementedError

    # TODO: can't take file cuz DB don't use that? So remove it?
    @staticmethod
    def save(file: Path, habits: list[Habit]):
        """Save the habits to file 'file'."""
        raise NotImplementedError

class OrgStorage:
    """
    A class used to parse org files as storage for habits.
    Implements StorageInterface.
    """
    file: Path

    def __init__(self, file: str):
        if not Path(file).suffix == ".org":
            # raise Expection('WrongFileFormat')
            print(f"WrongFileFormat: {file}")
            return
        self.file = Path(file)

    # TODO: Depending on what StorageInterface becomes use self.file
    @staticmethod
    def read(file: Path) -> list[Habit]:
        print("Read org.")
        # TODO: mypy not recognizing Exception
        # raise Exception('NotImplementedYet')
        print("OrgStorage.read not implemented yet")
        return list()

    # TODO: Depending on what StorageInterface becomes use self.file
    @staticmethod
    def save(file: Path, habits: list[Habit]):
        print("Save org.")
        # TODO: mypy not recognizing Exception
        # raise Exception('NotImplementedYet')
        print("OrgStorage.save not implemented yet")
