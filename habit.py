from datetime import datetime
from typing import Optional, Literal
from enum import StrEnum

# TODO: These kinda suck
class PeriodLength(StrEnum):
    """
    An Enum used to specify the period lengths of habits.

    Current supported values are:
        daily
        weakly
    """
    daily = "Daily"
    weakly = "Weakly"

class Habit():
    """
    A class used to represent habits.

    Attributes
    ----------
    name: str
        A string used to uniquely identify a habit.
    symbol: str
        A short string used to symbolize a habit
        and make it easier to differentiate it from others.
    creation_date: datetime
        The date and time of creation of a habit.
    streak_length: int
        An integer used to quickly identify how long a habit has not been broken.
    longest_streak: Optional[tuple[int, datetime, datetime]]
        A tuple of an integer, and 2 datetimes.
        The integer is used for quick identification of length.
        The datetimes are stored for analysis purposes.
    period_length: PeriodLength
        A string used to identify the period length for a habit.
    completed: bool
        A boolean to quickly check if a habit has been completed for the current period already.
        This could be removed but since python is slow used for quick checking.
    completed_times: list[datetime]
        A list of datetimes storing every time a habit was completed.
    """
    # TODO: Check if python can take references for longest_streak datetimes
    name: str
    symbol: str
    creation_date: datetime
    streak_length: int = 0
    longest_streak: Optional[tuple[int, datetime, datetime]] = None
    period_length: str
    completed: bool = False
    completed_times: list[datetime] = list()


    def __init__(self, name: str, symbol: str, period_length: PeriodLength):
        """
        Constructer for a Habit.
        Takes a name string, symbol string and a PeriodLength to create a new Habit
        with creation_date set to now (using datetime.now()).
        """
        self.name = name
        self.symbol = symbol
        self.period_length = period_length

        self.creation_date = datetime.now()
    
    def __str__(self):
        """
        How to represent a Habit as a string (useful for print).
        """
        # TODO: Make this code prettier?
        return f"""[{self.symbol}] {self.name}:
    Period: {self.period_length}
    Completed: {self.completed}
    Streak: {self.streak_length}
    Longest Streak: {self.longest_streak}
    Creation Date: {self.creation_date}"""
