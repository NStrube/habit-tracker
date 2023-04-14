from habit import Habit, PeriodLength, StreakPeriod
from storage import StorageInterface, StorageKind, OrgStorage
from pathlib import Path
from typing import Optional
from datetime import datetime
import sys

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

    def __next__(self):
        return next(self.iter)

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
        return [repr(h) for h in self.habits if h.completed]

    def get_uncompleted_str(self) -> list[str]:
        return [repr(h) for h in self.habits if not h.completed]

    def complete(self, n: str):
        # log("Habit to be marked complete:" + n)
        for h in self.habits:
            if n == repr(h):
                now = datetime.now().replace(microsecond=0)
                h.completed_times.append(now)
                h.completed = True
                if h.streak_length > 0:
                    h.longest_streak.length += 1
                    h.longest_streak.end = now
                else:
                    h.longest_streak = StreakPeriod(1, now, now)
                h.streak_length += 1
                # log("After marked:\n" + str(h))
                break

    def addHabit(self, name: str, symbol: str, period_length: PeriodLength):
        self.habits.append(Habit.new(name, symbol, period_length))

    def deleteHabit(self, n: str):
        for h in self.habits:
            if n == repr(h):
                self.habits.remove(h)
    
    def getHabit(self, n: str) -> Optional[Habit]:
        for h in self.habits:
            if n == repr(h):
                return h
        return None

    def nrDailyHabits(self) -> int:
        return len([h for h in self.habits if h.period_length == PeriodLength.daily])

    def nrWeaklyHabits(self) -> int:
        return len([h for h in self.habits if h.period_length == PeriodLength.weakly])

    def currentLongestStreak(self) -> str:
        streak=lambda h : h.streak_length
        l = max(iter(self.habits), key=streak)
        return f"{l.name}: {l.streak_length}"

    def currentLongestDailyStreak(self) -> str:
        streak=lambda h : h.streak_length
        l = max(iter(self.get_daily()), key=streak)
        return f"{l.name}: {l.streak_length}"

    def currentLongestWeaklyStreak(self) -> str:
        streak=lambda h : h.streak_length
        l = max(iter(self.get_weakly()), key=streak)
        return f"{l.name}: {l.streak_length}"

    def longestEverStreak(self) -> str:
        def lstreak(h: Habit) -> int:
            if h.longest_streak is None:
                return 0
            else:
                return h.longest_streak.length
        l = max(iter(self.habits), key=lstreak)
        if l.longest_streak is None or l.longest_streak == 0:
            return "None"
        else:
            return f"{l.name}: {l.longest_streak}"

    def longestEverDailyStreak(self) -> str:
        def lstreak(h: Habit) -> int:
            if h.longest_streak is None:
                return 0
            else:
                return h.longest_streak.length
        l = max(iter(self.get_daily()), key=lstreak)
        if l.longest_streak is None or l.longest_streak == 0:
            return "None"
        else:
            return f"{l.name}: {l.longest_streak}"

    def longestEverWeaklyStreak(self) -> str:
        def lstreak(h: Habit) -> int:
            if h.longest_streak is None:
                return 0
            else:
                return h.longest_streak.length
        l = max(iter(self.get_weakly()), key=lstreak)
        if l.longest_streak is None or l.longest_streak == 0:
            return "None"
        else:
            return f"{l.name}: {l.longest_streak}"

    def get_weakly(self) -> list[Habit]:
        return [h for h in self.habits if h.period_length == PeriodLength.weakly]

    def get_daily(self) -> list[Habit]:
        return [h for h in self.habits if h.period_length == PeriodLength.daily]

    def check_names_unique(self) -> bool:
        names = [h.name for h in self.habits]
        for n in names:
            if names.count(n) != 1:
                return False
        return True
            
    def check_name_unique(self, n: str) -> bool:
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
               or (h.period_length == PeriodLength.weakly and\
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
