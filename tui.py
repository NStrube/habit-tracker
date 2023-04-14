from blessed import Terminal
from enum import StrEnum
from typing import Optional
from itertools import zip_longest
import string

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
    """
    homepage = "Home Page"
    analytics = "Analytics"
    info = "Habit Information"

def printTable(term: Terminal, lhs: list[str], rhs: list[str]):
    printRow(term, "TODO", "DONE")
    # divider
    print(term.ljust('', fillchar='-'))
    for l, r in zip_longest(lhs, rhs, fillvalue=""):
        printRow(term, l, r)

# Why print rows instead of columns?
# Terminal draws from top to bottom, left ro right,
# thus better to go left to right, than down.
# With columns have to go to middle for every rhs with isn't great..
def printRow(term: Terminal, lhs: str, rhs: str):
    w = term.width // 2
    print(term.move_x(0) + term.ljust(term.truncate(lhs, width=w - 3), width=w - 3) + " | "\
           + term.ljust(term.truncate(rhs, width=w), width=w))

class Tui:
    """
    The class for drawing the Tui for my Habit Tracker.

    Atttributes
    -----------
    page: TuiPage
    habit_tracker: HabitTracker
    term: Terminal
    quit: bool

    Methods
    -------
    run():
    draw():
    input():
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
        log("input: " + inp)
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
        log("Getting str.")
        while True:
            print(self.term.move_xy(0, self.term.height - 1) + self.term.clear_eol() + prompt + s, end='', flush=True)
            ch = self.term.getch()
            # Enter
            if ch == '\n':
                log(s)
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
            p = self.get_str("Period length [d/daily/w/weakly]:")
            match p.lower():
                case "d" | "daily":
                    return PeriodLength.daily
                case "w" | "weakly":
                    return PeriodLength.weakly

    def confirm(self, prompt: str) -> bool:
        """
        Helper method to prompt user to confirm their choice.
        """
        log("Confirming...")
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
            case ' ' | '\t' | '\n':
                self.page = TuiPage.homepage

    def homepageInput(self, inp: str):
        """
        The inputs for the home page.
        """
        match inp:
            case 'q':
                self.quit = True
            case 'h' | 'l' | 'key_right' | 'key_left':
                self.on_todos = not self.on_todos
                log("On Todo: " + repr(self.on_todos))
                if self.on_todos and self.cursor > len(self.uncompleted) - 1:
                    self.cursor = len(self.uncompleted) - 1
                elif not self.on_todos and self.cursor > len(self.completed) - 1:
                    self.cursor = len(self.completed) - 1
                if self.cursor < 0:
                    self.cursor = 0
            case 'j' | 'key_down':
                log(f"Press j: on todo: {self.on_todos}; cursor: {self.cursor}; len: {len(self.uncompleted)}")
                if self.on_todos and self.cursor < len(self.uncompleted) - 1\
                        or not self.on_todos and self.cursor < len(self.completed) - 1:
                    self.cursor += 1
            case 'k' | 'key_up':
                if self.cursor > 0:
                    self.cursor -= 1
            case '\n':
                log("Pressed enter.")
                if self.on_todos and len(self.uncompleted) > 0:
                    self.habit_tracker.complete(self.uncompleted[self.cursor])
                    if self.cursor > 0:
                        self.cursor -= 1
                self.getHabits()
            case '+' | '=':
                log("Pressed +.")
                name = self.get_str("Name: ")
                while not self.habit_tracker.check_name_unique(name):
                    name = self.get_str("(Err: Not Unique) Name:")
                symbol = self.get_str("Symbol: ")
                period = self.get_period()
                self.habit_tracker.addHabit(name, symbol, period)
                self.getHabits()
            case '-' | '_':
                log("Pressed -.")
                if self.on_todos and len(self.uncompleted) > 0:
                    if not self.confirm(f"Are you sure you want to delete '{self.uncompleted[self.cursor]}'"):
                        return
                    log(f"Deleting {self.uncompleted[self.cursor]}...")
                    self.habit_tracker.deleteHabit(self.uncompleted[self.cursor])
                elif not self.on_todos and len(self.completed):
                    if not self.confirm(f"Are you sure you want to delete '{self.completed[self.cursor]}'"):
                        return
                    log(f"Deleting {self.completed[self.cursor]}...")
                    self.habit_tracker.deleteHabit(self.completed[self.cursor])
                self.getHabits()
                if self.cursor > 0:
                    self.cursor -= 1
            case '\t':
                log("Pressed Tab.")
                # Switch page.
                self.page = TuiPage.analytics
            case ' ':
                log("Pressed space.")
                # Open Habits information
                # TODO: If filter, doesn't work correctly
                self.page = TuiPage.info
            case 'f':
                log("Pressed f.")
                if self.filter == None:
                    self.filter = PeriodLength.daily
                elif self.filter == PeriodLength.daily:
                    self.filter = PeriodLength.weakly
                else:
                    self.filter = None


    def infoInput(self, inp: str):
        """
        The inputs for the habit info page.
        """
        match inp:
            case 'q':
                self.quit = True
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
        todo, done = self.apply_filter()

        with self.term.hidden_cursor():
            self.drawHeader()
            printTable(self.term, todo, done)
            self.warn(f"Filtering: {self.filter}")
        if self.on_todos: 
            cursor_x = 0
        else: 
            cursor_x = self.term.width // 2
        log("cursor: " + repr(cursor_x) + ", " + repr(self.cursor))
        print(self.term.move_yx(self.cursor + 3, cursor_x), end='', flush=True)

    def drawAnalytics(self):
        """
        Draws the analytics page.
        """
        with self.term.hidden_cursor():
            self.drawHeader()
            print(f"Total number of habits: {len(self.habit_tracker.habits)}")
            # TODO: better way of saying this?
            print(f"Completed habits: {len(self.completed)}")
            print(f"Daily habits: {self.habit_tracker.nrDailyHabits()}")
            print(f"Weakly habits: {self.habit_tracker.nrWeaklyHabits()}")
            print("")

            print(f"Current longest streak: {self.habit_tracker.currentLongestStreak()}")
            print(f"Current longest daily habit streak: {self.habit_tracker.currentLongestDailyStreak()}")
            print(f"Current longest weakly habit streak: {self.habit_tracker.currentLongestWeaklyStreak()}")
            print("")

            print(f"Longest ever streak: {self.habit_tracker.longestEverStreak()}")
            print(f"Longest ever daily habit streak: {self.habit_tracker.longestEverDailyStreak()}")
            print(f"Longest ever weakly habit streak: {self.habit_tracker.longestEverWeaklyStreak()}")

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
            # self.draw()
            return
        print(self.term.clear() + self.term.home() + "[" + self.page + "]")
        print()
        print(h)

    def apply_filter(self) -> tuple[list[str], list[str]]:
        """
        Applies the filter for periodicity.
        """
        log(f"Filter: {self.filter}")
        if self.filter is None:
            return [self.uncompleted, self.completed]
        elif self.filter == PeriodLength.daily:
            daily = self.habit_tracker.get_daily()
            return [[repr(d) for d in daily if not d.completed],\
                    [repr(d) for d in daily if d.completed]]
        else:
            weakly = self.habit_tracker.get_weakly()
            return [[repr(w) for w in weakly if not w.completed],\
                    [repr(w) for w in weakly if w.completed]]
