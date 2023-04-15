"""This provides the habit class for the habit tracker."""
# NOTE: Used for returning Habit inside definition
from __future__ import annotations

from datetime import datetime
from typing import Optional
from enum import StrEnum

from log import log

class PeriodLength(StrEnum):
    """
    An Enum used to specify the period lengths of habits.

    Current supported values:
        daily
        weekly
    """
    daily = "Daily"
    weekly = "Weekly"

class StreakPeriod:
    """
    A class used to represent longest streak of habit

    Attributes
    ----------
    length: int
        Length of  streak for quick identification.
    begin: datetime
        Beginning of the streak.
    end: datetime
        Beginning of the streak.

    Because fuck tuples. Can't index them for some reason.
    """
    length: int
    begin: datetime
    end: datetime

    def __init__(self, length, begin, end):
        self.length = length
        self.begin = begin
        self.end = end

    def __str__(self):
        return f"{self.length} [{self.begin}];[{self.end}]"

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
    longest_streak: Optional[StreakPeriod]
        An optional StreakPeriod for representing how long the longest streak was.
    period_length: PeriodLength
        A PeriodLength used to identify the period length for a habit.
    completed: bool
        A boolean to quickly check if a habit has been completed for the current period already.
        This could be removed but since python is slow used for quick checking.
    completed_times: list[datetime]
        A list of datetimes storing every time a habit was completed.

    Methods
    -------
    new(name: str, symbol: str, period_length: PeriodLength) -> Habit
    last_completed_date() -> Optional[datetime]
    """
    name: str
    symbol: str
    creation_date: datetime
    streak_length: int = 0
    longest_streak: Optional[StreakPeriod] = None
    period_length: PeriodLength
    completed: bool = False
    completed_times: list[datetime] = list()


    def __init__(self, name: str, symbol: str, period_length: PeriodLength,
                 creation_date: datetime, streak_length: int,
                 completed: bool, completed_times: list[datetime],
                 longest_streak: Optional[StreakPeriod] = None):
        """
        Constructer for a Habit.
        """
        self.name = name
        self.symbol = symbol
        self.period_length = period_length
        self.creation_date = creation_date.replace(microsecond=0)
        self.streak_length = streak_length
        self.longest_streak = longest_streak
        self.completed = completed
        self.completed_times = completed_times
        self.completed_times.sort()

    @staticmethod
    def new(name: str, symbol: str, period_length: PeriodLength) -> Habit:
        """
        Creates a new habit.
        Takes a name string, symbol string and a PeriodLength to create a new Habit
        with creation_date set to now (using datetime.now()).
        """
        return Habit(name, symbol, period_length, datetime.now(), 0, False, list())
    
    def __str__(self):
        """
        How to represent a Habit as a string (useful for print).
        """
        return f"""[{self.symbol}] {self.name}:
Period: {self.period_length}
Completed: {self.completed}
Streak: {self.streak_length}
Longest Streak: {self.longest_streak}
Creation Date: {self.creation_date}"""

    def __repr__(self):
        return f"{self.symbol} {self.name}: {self.period_length}, Streak: {self.streak_length}"

    def last_completed_date(self) -> Optional[datetime]:
        """
        A helper function that returns the last time a Habit was completed.
        If the habit was never completed, returns None.
        """
        log(f"Lcd(): {self.completed_times}")
        if self.completed_times is None or len(self.completed_times) == 0:
            return None
        return self.completed_times[-1]

    def complete(self):
        """Sets self.longest_streak if necessary after completing habit."""
        now = datetime.now().replace(microsecond=0)
        self.completed_times.append(now)
        self.completed = True
        self.streak_length += 1

        if len(self.completed_times) == 1:
            self.longest_streak = StreakPeriod(1, now, now)
            return

        tmp = now
        # Iterate in reverse (ie. newest to oldest)
        length = 1
        for dt in reversed(self.completed_times):
            timedelta = tmp - dt
            if (self.period_length == PeriodLength.daily and timedelta.days > 1)\
            or (self.period_length == PeriodLength.weekly and timedelta.days > 7):
                break
            beginning = tmp
            tmp = dt
            length += 1

        newstreak = StreakPeriod(length, beginning, now)
        if newstreak.length >= self.longest_streak.length:
            self.longest_streak = newstreak

            
