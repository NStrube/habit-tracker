from blessed import Terminal
from enum import StrEnum
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

def printTable(term: Terminal, lhs: list[str], rhs: list[str]):
    printRow(term, "TODO", "DONE")
    # divider
    print(term.ljust('', fillchar='-'))

    # If one list longer than other
    length = 0
    if len(lhs) >= len(rhs):
        length = len(lhs)
    else:
        length = len(rhs)

    for i in range(length):
        l = ""
        r = ""
        # If one list longer than other
        # Could also pad the other but eh
        if i < len(lhs):
            l = lhs[i]

        if i < len(rhs):
            r = rhs[i]

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

    habit_tracker: HabitTracker
    completed: list[str]
    uncompleted: list[str]

    def getHabits(self):
        self.uncompleted = self.habit_tracker.get_uncompleted_str()
        self.completed = self.habit_tracker.get_completed_str()

    def run(self):
        self.habit_tracker = HabitTracker(StorageKind.org, "habits.org")
        self.term = Terminal()
        self.getHabits()
        
        with self.term.fullscreen(), self.term.cbreak():
            self.draw()
            while not self.quit:
                # PERF: Potential improvement, only redraw if input warrants it
                self.input()
                self.draw()

    def draw(self):
        with self.term.hidden_cursor():
            # TODO: Make it print both page names and the current one in '[]'
            print(self.term.clear() + self.term.home() + "[" + self.page + "]")
            printTable(self.term, self.uncompleted, self.completed)
        if self.on_todos: 
            cursor_x = 0
        else: 
            cursor_x = self.term.width // 2
        log("cursor: " + repr(cursor_x) + ", " + repr(self.cursor))
        print(self.term.move_yx(self.cursor + 3, cursor_x), end='', flush=True)

    def input(self):
        inp = self.term.inkey().lower()
        log("input: " + inp)
        if self.page == TuiPage.analytics:
            self.analyticsInput(inp)
        else:
            self.homepageInput(inp)

    def analyticsInput(self, inp: str):
        pass

    def homepageInput(self, inp: str):
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
            case _:
                pass

    def get_str(self, prompt: str) -> str:
        s = ""
        log("Getting str.")
        while True:
            print(self.term.move_xy(0, self.term.height - 1) + self.term.clear_eol() + prompt + s, end='', flush=True)
            ch = self.term.getch()
            # Enter
            if ch == '\n':
                log(s)
                return s
            # Backspace
            elif ch == chr(263):
                s = s[:-1]
            elif ch in string.printable:
                s += ch

    def get_period(self) -> PeriodLength:
        while True:
            p = self.get_str("Period length [d/daily/w/weakly]:")
            match p.lower():
                case "d" | "daily":
                    return PeriodLength.daily
                case "w" | "weakly":
                    return PeriodLength.weakly

    def confirm(self, prompt: str) -> bool:
        log("Confirming...")
        while True:
            print(self.term.move_xy(0, self.term.height - 1) + self.term.clear_eol() + prompt + " [y/n] ", end='', flush=True)
            match self.term.getch().lower():
                case "y":
                    return True
                case "n":
                    return False

    def warn(self, warning: str):
        print(self.term.move_xy(0, self.term.height - 1) + self.term.clear_eol() + warning, end='', flush=True)
