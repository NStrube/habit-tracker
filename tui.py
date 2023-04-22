"""This method provides the TUI for the habit tracker."""
from enum import StrEnum
from typing import Optional
from itertools import zip_longest
import string
import sys

from blessed import Terminal

from app import HabitTracker
from storage import StorageKind
from habit import PeriodLength

from log import log

class TuiPage(StrEnum):
    """
    An Enum to specify which page the Tui is currently on.

    Possible values:
        homepage
        analytics
        info
    """
    homepage = "Home Page"
    analytics = "Analytics"
    info = "Habit Information"

def printTable(term: Terminal, lhs: list[str], rhs: list[str]):
    """
    Prints a table with 2 columns (lhs and rhs) on term
    """
    printRow(term, "TODO", "DONE")
    # divider
    print(term.ljust('', fillchar='-'))
    for l, r in zip_longest(lhs, rhs, fillvalue=""):
        printRow(term, l, r)

# NOTE:
# Why print rows instead of columns?
# Terminal draws from top to bottom, left ro right,
# thus better to go left to right, than down.
# With columns have to go to middle for every rhs with isn't great..
def printRow(term: Terminal, lhs: str, rhs: str):
    """
    Prints a row of a table with lhs on the complete left and rhs starting in the middle
    of the terminal.
    """
    w = term.width // 2
    print(term.move_x(0) + term.ljust(term.truncate(lhs, width=w - 3), width=w - 3) + " | "\
           + term.ljust(term.truncate(rhs, width=w), width=w))

class Tui:
    """
    The class for drawing the Tui for my Habit Tracker.

    Atttributes
    -----------
    page: TuiPage
    term: Terminal
    quit: bool
    cursor: int
    on_todos: bool
    filter: Optional[PeriodLength]

    habit_tracker: HabitTracker
    completed: list[str]
    uncompleted: list[str]

    Methods
    -------
    run()
    draw()
    input()
    getHabits()
    get_str(prompt: str) -> str
    get_period() -> PeriodLength
    confirm() -> bool
    warn(warning: str)
    analyticsInput(inp: str)
    homepageInput(inp: str)
    infoInput(inp: str)
    drawHomepage()
    drawAnalytics()
    drawInfopage()
    """
    page: TuiPage = TuiPage.homepage
    term: Terminal
    quit: bool = False
    cursor: int = 0
    on_todos: bool = True
    filter: Optional[PeriodLength] = None

    habit_tracker: HabitTracker
    completed: list[str]
    uncompleted: list[str]

    def getHabits(self):
        """
        Updates the self.completed and self.uncompleted lists.
        """
        self.habit_tracker.update()
        self.uncompleted = self.habit_tracker.get_uncompleted_str()
        self.completed = self.habit_tracker.get_completed_str()

    def run(self):
        """
        Run the habit tracker.

        Sets up the habit_tracker and terminal,
        then calls draw and input repeatedly
        """
        self.habit_tracker = HabitTracker(StorageKind.org, "habits.org")
        self.term = Terminal()
        self.getHabits()
        for h in self.habit_tracker.habits:
            log(repr(h))
        
        with self.term.fullscreen(), self.term.cbreak():
            while not self.quit:
                self.draw()
                self.input()

    def draw(self):
        """
        Draw the Tui once.
        """
        if self.page == TuiPage.homepage:
            self.drawHomepage()
        elif self.page == TuiPage.analytics:
            self.drawAnalytics()
        else:
            self.drawInfopage()

    def input(self):
        """
        Handle one input.
        """
        inp = self.term.inkey().lower()
        # log("input: " + inp)
        if self.page == TuiPage.analytics:
            self.analyticsInput(inp)
        elif self.page == TuiPage.homepage:
            self.homepageInput(inp)
        else:
            self.infoInput(inp)

    def get_str(self, prompt: str) -> str:
        """
        Helper method to prompt the user for a string.
        """
        s = ""
        # log("Getting str.")
        while True:
            print(self.term.move_xy(0, self.term.height - 1) + self.term.clear_eol() + prompt + s, end='', flush=True)
            ch = self.term.getch()
            # Enter
            if ch == '\n':
                # log(s)
                if len(s) > 0:
                    return s
            # Backspace
            elif ch == chr(263):
                s = s[:-1]
            elif ch in string.printable:
                s += ch

    def get_period(self) -> PeriodLength:
        """
        Helper method to prompt user for a PeriodLength.
        """
        while True:
            p = self.get_str("Period length [d/daily/w/weekly]:")
            match p.lower():
                case "d" | "daily":
                    return PeriodLength.daily
                case "w" | "weekly":
                    return PeriodLength.weekly

    def confirm(self, prompt: str) -> bool:
        """
        Helper method to prompt user to confirm their choice.
        """
        # log("Confirming...")
        while True:
            print(self.term.move_xy(0, self.term.height - 1) + self.term.clear_eol() + prompt + " [y/n] ", end='', flush=True)
            match self.term.getch().lower():
                case "y":
                    return True
                case "n":
                    return False

    def warn(self, warning: str):
        """
        Helper function to warn the user.
        """
        print(self.term.move_xy(0, self.term.height - 1) + self.term.clear_eol() + warning, end='', flush=True)

    def analyticsInput(self, inp: str):
        """
        The inputs for the analytics page.
        """
        match inp:
            case 'q':
                self.quit = True
                self.habit_tracker.save()
            case 'o':
                log("Pressed 'o'")
                self.habit_tracker.read()
                self.getHabits()
            case 's':
                log("Pressed 's'")
                self.habit_tracker.save()
            case ' ' | '\t' | '\n':
                self.page = TuiPage.homepage

    def homepageInput(self, inp: str):
        """
        The inputs for the home page.
        """
        match inp:
            case 'q':
                self.quit = True
                self.habit_tracker.save()
            case 'o':
                log("Pressed 'o'")
                self.habit_tracker.read()
                self.getHabits()
            case 's':
                log("Pressed 's'")
                self.habit_tracker.save()
            case 'h' | 'l' | 'key_right' | 'key_left':
                self.on_todos = not self.on_todos
                # log("On Todo: " + repr(self.on_todos))
                if self.on_todos and self.cursor > len(self.uncompleted) - 1:
                    self.cursor = len(self.uncompleted) - 1
                elif not self.on_todos and self.cursor > len(self.completed) - 1:
                    self.cursor = len(self.completed) - 1
                self.cursor = max(self.cursor, 0)
            case 'j' | 'key_down':
                # log(f"Press j: on todo: {self.on_todos}; cursor: {self.cursor}; len: {len(self.uncompleted)}")
                if self.on_todos:  
                    max_cursor_pos = len(self.uncompleted)
                else:
                    max_cursor_pos = len(self.completed)
                self.cursor = min(self.cursor + 1, max(max_cursor_pos - 1, 0))
            case 'k' | 'key_up':
                if self.cursor > 0:
                    self.cursor -= 1
            case '\n':
                # log("Pressed enter.")
                if self.on_todos and len(self.uncompleted) > 0:
                    self.habit_tracker.complete(self.uncompleted[self.cursor])
                    if self.cursor > 0:
                        self.cursor -= 1
                self.getHabits()
            case '+' | '=':
                # log("Pressed +.")
                name = self.get_str("Name: ")
                while not self.habit_tracker.check_name_unique(name):
                    name = self.get_str("(Err: Not Unique) Name:")
                symbol = self.get_str("Symbol: ")
                period = self.get_period()
                self.habit_tracker.addHabit(name, symbol, period)
                self.getHabits()
            case '-' | '_':
                # log("Pressed -.")
                if self.on_todos and len(self.uncompleted) > 0:
                    if not self.confirm(f"Are you sure you want to delete '{self.uncompleted[self.cursor]}'"):
                        return
                    # log(f"Deleting {self.uncompleted[self.cursor]}...")
                    toDelete = self.uncompleted[self.cursor]
                elif not self.on_todos and len(self.completed) > 0:
                    if not self.confirm(f"Are you sure you want to delete '{self.completed[self.cursor]}'"):
                        return
                    # log(f"Deleting {self.completed[self.cursor]}...")
                    toDelete = self.uncompleted[self.cursor]
                self.habit_tracker.deleteHabit(toDelete)
                self.getHabits()
                if self.cursor > 0:
                    self.cursor -= 1
            case '\t':
                # log("Pressed Tab.")
                # Switch page.
                self.page = TuiPage.analytics
            case ' ':
                # log("Pressed space.")
                # Open Habits information
                self.page = TuiPage.info
            case 'f':
                # log("Pressed f.")
                if self.filter is None:
                    self.filter = PeriodLength.daily
                elif self.filter == PeriodLength.daily:
                    self.filter = PeriodLength.weekly
                else:
                    self.filter = None


    def infoInput(self, inp: str):
        """
        The inputs for the habit info page.
        """
        match inp:
            case 'q':
                self.quit = True
                self.habit_tracker.save()
            case 'o':
                log("Pressed 'o'")
                self.habit_tracker.read()
                self.getHabits()
            case 's':
                log("Pressed 's'")
                self.habit_tracker.save()
            case ' ' | '\t' | '\n':
                self.page = TuiPage.homepage

    def drawHeader(self):
        """
        Draws the header.
        """
        if self.page == TuiPage.homepage:
            print(self.term.clear() + self.term.home() + "[" + TuiPage.homepage + "] " + TuiPage.analytics)
        else:
            print(self.term.clear() + self.term.home() + ' ' + TuiPage.homepage + " [" + TuiPage.analytics + "]")

    def drawHomepage(self):
        """
        Draws the home page.
        """
        if self.filter is None:
            self.getHabits()
        else:
            get_habits = self.habit_tracker.get_daily
            if self.filter == PeriodLength.weekly:
                get_habits = self.habit_tracker.get_weekly
            self.uncompleted = [repr(h) for h in get_habits() if not h.completed]
            self.completed = [repr(h) for h in get_habits() if h.completed]

        with self.term.hidden_cursor():
            self.drawHeader()
            printTable(self.term, self.uncompleted, self.completed)
            self.warn(f"Filtering: {self.filter}")
        if self.on_todos: 
            cursor_x = 0
        else: 
            cursor_x = self.term.width // 2
        # log("cursor: " + repr(cursor_x) + ", " + repr(self.cursor))
        print(self.term.move_yx(self.cursor + 3, cursor_x), end='', flush=True)

    def drawAnalytics(self):
        """
        Draws the analytics page.
        """
        with self.term.hidden_cursor():
            self.drawHeader()
            print(f"Total number of habits: {len(self.habit_tracker.habits)}")
            print(f"Completed habits: {len(self.completed)}")
            print(f"Daily habits: {self.habit_tracker.nrDailyHabits()}")
            print(f"Weekly habits: {self.habit_tracker.nrWeeklyHabits()}")
            print("")

            print(f"Current longest streak: {self.habit_tracker.currentLongestStreak()}")
            print(f"Current longest daily habit streak: {self.habit_tracker.currentLongestDailyStreak()}")
            print(f"Current longest weekly habit streak: {self.habit_tracker.currentLongestWeeklyStreak()}")
            print("")

            print(f"Longest ever streak: {self.habit_tracker.longestEverStreak()}")
            print(f"Longest ever daily habit streak: {self.habit_tracker.longestEverDailyStreak()}")
            print(f"Longest ever weekly habit streak: {self.habit_tracker.longestEverWeeklyStreak()}")

    def drawInfopage(self):
        """
        Draws the habit info page.
        """
        if self.on_todos and self.cursor < len(self.uncompleted):
            h = self.habit_tracker.getHabit(self.uncompleted[self.cursor])
        elif not self.on_todos and self.cursor < len(self.completed):
            h = self.habit_tracker.getHabit(self.completed[self.cursor])
        else:
            self.page = TuiPage.homepage
            self.draw()
            return
        if h is None:
            sys.exit("Unreachable: Got None when trying to get habit for info page.")
        print(self.term.clear() + self.term.home() + "[" + self.page + "]")
        print()
        print(h)
        print("Completed at:")
        for ct in h.completed_times:
            print(f"- [{str(ct)}]")
