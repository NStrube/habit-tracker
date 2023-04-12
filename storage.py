import abc
from typing import Protocol
from habit import Habit
from pathlib import Path
from enum import StrEnum

class StorageKind(StrEnum):
    """
    An Enum used to specify the kind of StorageInterface to use.

    Current supported values:
        org
    """
    org = "Org"

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
    def read(self) -> list[Habit]:
        """Reads in the habits."""
        raise NotImplementedError

    def save(self, habits: list[Habit]):
        """Save the habits."""
        raise NotImplementedError

class OrgStorage:
    """
    A class used to parse org files as storage for habits.
    Implements StorageInterface.
    """
    file: Path

    def __init__(self, file: str):
        if not Path(file).suffix == ".org":
            print(f"WrongFileFormat: {file}")
            return
        self.file = Path(file)

    def read(self) -> list[Habit]:
        print("Read org.")
        print("OrgStorage.read not implemented yet")
        return list()

    def save(self, habits: list[Habit]):
        print("Save org.")
        print("OrgStorage.save not implemented yet")
