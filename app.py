"""This module provides the main logic of the habit tracker."""
from typing import Optional
from datetime import datetime
import sys

from habit import Habit, PeriodLength, StreakPeriod
from storage import StorageInterface, StorageKind, OrgStorage
from log import log

def streak(h: Habit):
    """Helper method for getting streak length for max function"""
    return h.streak_length

def lstreak(h: Habit) -> int:
    """Helper method for getting longest_streak length for max function"""
    if h.longest_streak is None:
        return 0
    return h.longest_streak.length

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
    read()
    save()
    read_from(file: str) !! Not Implemented Yet !!
    save_as(file: str) !! Not Implemented Yet !!
    get_completed_str() -> list[str]
    get_uncompleted_str() -> list[str]
    complete(n: str)
    addHabit(name: str, symbol: str, period_length: PeriodLength)
    deleteHabit(n: str)
    getHabit(n: str) -> Optional[Habit]
    nrDailyHabits() -> int
    nrWeaklyHabits() -> int
    currentLongestStreak() -> str
    currentLongestDailyStreak() -> str
    currentLongestWeaklyStreak() -> str
    longestEverStreak() -> str
    longestEverDailyStreak() -> str
    longestEverWeaklyStreak() -> str
    get_weekly() -> list[Habit]
    get_daily() -> list[Habit]
    check_names_unique() -> bool
    check_name_unique(n: str) -> bool
    update()
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
        self.habits = self.storage.read()
        if not self.check_names_unique():
            # Ensure habit names are unique
            sys.exit("A habit name is not unique. Pls fix.")
        self.update()

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
        """
        Returns a list of repr(Habit) of all completed habits.
        """
        return [repr(h) for h in self.habits if h.completed]

    def get_uncompleted_str(self) -> list[str]:
        """
        Returns a list of repr(Habit) of all uncompleted habits.
        """
        return [repr(h) for h in self.habits if not h.completed]

    def complete(self, n: str):
        """
        Marks a habit as completed.
        """
        # log("Habit to be marked complete:" + n)
        for h in self.habits:
            if n == repr(h):
                now = datetime.now().replace(microsecond=0)
                h.completed_times.append(now)
                h.completed = True
                if h.longest_streak is not None and h.streak_length > h.longest_streak.length:
                    # TODO: This doesn't work correctly.
                    h.longest_streak.length += 1
                    h.longest_streak.end = now
                else:
                    h.longest_streak = StreakPeriod(1, now, now)
                h.streak_length += 1
                # log("After marked:\n" + str(h))
                break

    def addHabit(self, name: str, symbol: str, period_length: PeriodLength):
        """
        Adds a new habit with given name, symbol and period_length to be tracked.
        """
        self.habits.append(Habit.new(name, symbol, period_length))

    def deleteHabit(self, n: str):
        """
        Deletes the habit where repr(Habit) == n.
        """
        for h in self.habits:
            if n == repr(h):
                self.habits.remove(h)
    
    def getHabit(self, n: str) -> Optional[Habit]:
        """
        Returns a habit where repr(Habit) == n, if it exists.
        Otherwise returns None.
        """
        for h in self.habits:
            if n == repr(h):
                return h
        return None

    def nrDailyHabits(self) -> int:
        """
        Returns the number of daily habits tracked.
        """
        return len([h for h in self.habits if h.period_length == PeriodLength.daily])

    def nrWeaklyHabits(self) -> int:
        """
        Returns the number of weekly habits tracked.
        """
        return len([h for h in self.habits if h.period_length == PeriodLength.weekly])

    def currentLongestStreak(self) -> str:
        """
        Returns the name and the streak length of the habit with the longest, ongoing streak.
        """
        l = max(iter(self.habits), key=streak)
        return f"{l.name}: {l.streak_length}"

    def currentLongestDailyStreak(self) -> str:
        """
        Returns the name and the streak length of the daily habit with the longest, ongoing streak.
        """
        l = max(iter(self.get_daily()), key=streak)
        return f"{l.name}: {l.streak_length}"

    def currentLongestWeaklyStreak(self) -> str:
        """
        Returns the name and the streak length of the weekly habit with the longest, ongoing streak.
        """
        l = max(iter(self.get_weekly()), key=streak)
        return f"{l.name}: {l.streak_length}"

    def longestEverStreak(self) -> str:
        """
        Returns the name and the streak length of the habit with the longest streak recorded.
        """
        l = max(iter(self.habits), key=lstreak)
        if l.longest_streak is None or l.longest_streak == 0:
            return "None"
        return f"{l.name}: {l.longest_streak}"

    def longestEverDailyStreak(self) -> str:
        """
        Returns the name and the streak length of the daily habit with the longest streak recorded.
        """
        l = max(iter(self.get_daily()), key=lstreak)
        if l.longest_streak is None or l.longest_streak == 0:
            return "None"
        return f"{l.name}: {l.longest_streak}"

    def longestEverWeaklyStreak(self) -> str:
        """
        Returns the name and the streak length of the weekly habit with the longest streak recorded.
        """
        l = max(iter(self.get_weekly()), key=lstreak)
        if l.longest_streak is None or l.longest_streak == 0:
            return "None"
        return f"{l.name}: {l.longest_streak}"

    def get_weekly(self) -> list[Habit]:
        """
        Returns the list of tracked weekly habits.
        """
        return [h for h in self.habits if h.period_length == PeriodLength.weekly]

    def get_daily(self) -> list[Habit]:
        """
        Returns the list of tracked daily habits.
        """
        return [h for h in self.habits if h.period_length == PeriodLength.daily]

    def check_names_unique(self) -> bool:
        """
        Returns true if the names of all tracked habits are unique.
        """
        names = [h.name for h in self.habits]
        for n in names:
            if names.count(n) != 1:
                return False
        return True
            
    def check_name_unique(self, n: str) -> bool:
        """
        Checks if the name n is unique agains all other tracked habits.
        """
        return len([1 for h in self.habits if h.name == n]) == 0
            
    def update(self):
        """
        Updates all habits according to their period length
        if a new day or new week has started
        """
        for h in self.habits:
            log("H:" + repr(h))
            log("Ct:")
            for ct in h.completed_times:
                log(repr(ct))
            log(f"Lcd: {h.last_completed_date()}")
            log("")
        for h in self.habits:
            lcd = h.last_completed_date()
            if lcd is None:
                log("Lcd is None")
                continue
            now = datetime.now()
            now = now.replace(microsecond=0)
            if h.streak_length > 0 and lcd is None:
                sys.exit("Unreachable: lcd should never be None if streak length > 0")
            log(f"Streak length: {h.streak_length}")
            if h.streak_length > 0:
                log(f"Type Lcd: {type(lcd)}")
                log(f"Type now: {type(now)}")
                log(f"Period length:       {h.period_length}")
                log(f"Date now:            {now}")
                log(f"Lcd:                 {lcd}")
                log(f"lcd < now:           {lcd.day < now.day}")
                log(f"lcd.week < now.week: {lcd.isocalendar().week < now.isocalendar().week}")
            if h.streak_length > 0 and\
               ((h.period_length == PeriodLength.daily and lcd.day < now.day)\
               or (h.period_length == PeriodLength.weekly and\
               lcd.isocalendar().week < now.isocalendar().week)):
                # New week/day
                # If streak == 0, not completed and thus do nothing
                if h.completed:
                    # Was completed and thus streak already increased by 1
                    # and completed_times was already added,
                    # so only set to False
                    h.completed = False
                else:
                    # Was not completed, so reset streak
                    h.streak_length = 0
