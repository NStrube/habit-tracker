import abc
from typing import Protocol
from habit import Habit, PeriodLength, StreakPeriod
from pathlib import Path
from enum import StrEnum
from datetime import datetime

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

    Attributes
    ----------
    file: Path
        the Path to the file that will be read from and saved to.
    """
    file: Path

    def __init__(self, file: str):
        """
        Constructor for Orgstorage.
        Checks if file is an org file (by checking extension (so not actually xD)),
        if so sets self.file to given file.
        """
        if not Path(file).suffix == ".org":
            print(f"WrongFileFormat: {file}")
            return
        self.file = Path(file)

    def read(self) -> list[Habit]:
        f = open(self.file, "r")
        habits: list[Habit] = list()

        name = None
        symbol = None
        completed = None
        created = None
        streak = None
        longest_streak = None
        period = None
        completed_times: list[datetime] = []

        AlreadyAdded = False

        for line in f:
            # NOTE: line keeps newline character
            if line.startswith(':PROP') or line.startswith(':END') or line.startswith('# '):
                continue

            # Completed, symbol, name
            elif line.startswith('* '):
                # NOTE: Only relevant if not newline separated Habits
                # TODO: Raise exception if not ... ?
                if not AlreadyAdded and name and symbol and period and created and streak and completed != None:
                    # NOTE: Because mypy complains about Optional[bool] otherwise
                    if completed == True:
                        comp = True
                    else:
                        comp = False
                    new_habit = Habit(name, symbol, period, created, streak, comp, completed_times, longest_streak)
                    habits.append(new_habit)
                AlreadyAdded = False

                [_, _,rest] = line.partition(' ')
                [t, _, rest] = rest.partition(' ')
                [symbol, _, name] = rest.partition(' ')
                name = name[:-1]
                if t == "TODO":
                    completed = False
                elif t == "DONE":
                    completed = True
                else:
                    print(f"Unkown completed state in file: {self.file}")

            # Creation date
            elif line.startswith(':created: ['):
                [_, _, date] = line.partition(':created: [')
                end = date.find(']\n')
                created = datetime.strptime(date[:end], "%Y-%m-%d %H:%M:%S")

            # Streak
            elif line.startswith(':streak: '):
                start = line.find(' ')
                streak = int(line[start:])

            # Longest streak
            elif line.startswith(':longest streak: '):
                _, _, rest = line.partition(' ')
                _, _, rest = rest.partition(' ')
                nr, _, rest = rest.partition(' ')
                d1, _, d2 = rest.partition(';')
                dt1 = datetime.strptime(d1[1:-2], "%Y-%m-%d %H:%M")
                dt2 = datetime.strptime(d2[1:-2], "%Y-%m-%d %H:%M")
                longest_streak = StreakPeriod(nr, dt1, dt2)

            # Period length
            elif line.startswith(':period: '):
                start = line.find(' ') + 1
                l = line[start:-1]
                if l == "Daily":
                    period = PeriodLength.daily
                elif l == "Weakly":
                    period = PeriodLength.weakly
                else:
                    print(f"Unkown PeriodLength in file: {self.file}")

            # Completed times
            elif line.startswith('- '):
                print("Impl completed times")


            elif line.strip() == "":
                # TODO: Raise exception if not ... ?
                if name and symbol and period and created and streak and completed != None:
                    # NOTE: Because mypy complains about Optional[bool] otherwise
                    if completed == True:
                        comp = True
                    else:
                        comp = False
                    new_habit = Habit(name, symbol, period, created, streak, comp, completed_times, longest_streak)
                    habits.append(new_habit)
                    AlreadyAdded = True

        f.close()

        # TODO: Raise exception if not ... ?
        if name and symbol and period and created and streak and completed != None:
            # NOTE: Because mypy complains about Optional[bool] otherwise
            if completed == True:
                comp = True
            else:
                comp = False
            new_habit = Habit(name, symbol, period, created, streak, comp, completed_times, longest_streak)
            habits.append(new_habit)

        return habits

    def save(self, habits: list[Habit]):
        f = open(self.file, "w")
        
        for h in habits:
            print(h)
            if h.completed:
                t = "DONE"
            else:
                t = "TODO"
            # TODO: How to print tuple
            org = f"""
* {t} {h.symbol} {h.name}
:PROPERTIES:
:created: [{h.creation_date}]
:streak: {h.streak_length}
:longest_streak: {h.longest_streak}
:period: {h.period_length}
:END:
"""
            f.write(org)
            for time in h.completed_times:
                f.write(f"- [{time}]")

        f.close()
