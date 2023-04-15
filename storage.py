"""Provides storage interface and implementations for habit tracker."""
from typing import Protocol, Optional
from pathlib import Path
from enum import StrEnum
from datetime import datetime
import sys

from habit import Habit, PeriodLength, StreakPeriod
from log import log

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
        if Path(file).suffix != ".org":
            sys.exit(f"Wrong File Format: Expected org, got: {file}")
        self.file = Path(file)

    def read(self) -> list[Habit]:
        """Read in habits from an org file."""
        with open(self.file, "r") as f:
            habits: list[Habit] = list()

            name = None
            symbol = None
            completed = None
            created = None
            streak = None
            longest_streak = None
            period = None
            completed_times: list[datetime] = []

            # If longest_streak has been read or not
            read_ls = False

            AlreadyAdded = False

            def hb(read_ls: bool, completed_times: list[datetime]) -> Optional[Habit]:
                """
                A helper method for building a Habit if every necessary field has a value.
                """
                # log("hb compl times: " + str(completed_times))
                if not AlreadyAdded and name and symbol and period and created and streak is not None and read_ls and completed is not None:
                    read_ls = False
                    return Habit(name, symbol, period, created, streak, completed, completed_times, longest_streak)
                return None

            for line in f:
                # log(f"'{line.rstrip()}': read_ls: {read_ls}")
                # log("\n\nLocals:\n" + repr(locals()) + "\n\n")
                # NOTE: line keeps newline character
                if line.startswith(':PROP') or line.startswith(':END') or line.startswith('# '):
                    continue

                # Completed, symbol, name
                if line.startswith('* '):
                    # NOTE: Only relevant if not newline separated Habits
                    h = hb(read_ls, completed_times)
                    if not AlreadyAdded and h is not None:
                        habits.append(h)
                        completed_times = list()
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
                        sys.exit(f"Unkown completed state in file: {self.file}")

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
                    read_ls = True
                    _, _, rest = line.partition(' ')
                    _, _, rest = rest.partition(' ')
                    if rest.strip() == "None":
                        continue
                    nr, _, rest = rest.partition(' ')
                    d1, _, d2 = rest.partition(';')
                    # log("d1 " + d1)
                    # log("d1 slice" + d1[1:-1])
                    dt1 = datetime.strptime(d1[1:-1], "%Y-%m-%d %H:%M:%S")
                    # log("d2" + d2)
                    # log("d2 slice" + d2[1:-2])
                    dt2 = datetime.strptime(d2[1:-2], "%Y-%m-%d %H:%M:%S")
                    longest_streak = StreakPeriod(int(nr), dt1, dt2)

                # Period length
                elif line.startswith(':period: '):
                    start = line.find(' ') + 1
                    l = line[start:-1]
                    if l == "Daily":
                        period = PeriodLength.daily
                    elif l == "Weekly":
                        period = PeriodLength.weekly
                    else:
                        sys.exit(f"Unkown PeriodLength in file: {self.file}")

                # Completed times
                elif line.startswith('- '):
                    _, _, dt = line.partition(' ')
                    # log(dt)
                    completed_times.append(datetime.strptime(dt[1:-2], "%Y-%m-%d %H:%M:%S"))
                    # sys.exit("Impl completed times")

                elif line.strip() == "":
                    h = hb(read_ls, completed_times)
                    if h is not None:
                        habits.append(h)
                        AlreadyAdded = True
                        completed_times = list()

        h = hb(read_ls, completed_times)
        if h is not None:
            habits.append(h)

        return habits

    def save(self, habits: list[Habit]):
        """Saves habits to an org file."""
        with open(self.file, "w") as f:
        
            for h in habits:
                # log(str(h))
                if h.completed:
                    t = "DONE"
                else:
                    t = "TODO"
                org = f"""
* {t} {h.symbol} {h.name}
:PROPERTIES:
:created: [{h.creation_date}]
:streak: {h.streak_length}
:longest streak: {h.longest_streak}
:period: {h.period_length}
:END:
"""
                f.write(org)
                for time in h.completed_times:
                    time = time.replace(microsecond=0)
                    f.write(f"- [{time}]\n")
