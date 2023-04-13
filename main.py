from habit import Habit, PeriodLength
from storage import StorageKind
from app import HabitTracker
from tui import Tui

from storage import OrgStorage

# TODO:
# ╭―――――――――――――――――――――――――――╮
# │                           │
# │    Rewrite It in Rust     │
# │                           │
# ╰―――――――――――――――――――――――――――╯
#
# Or any sane language, really

# Mypy not recognizing Exception
if __name__ == "__main__":
    d = Habit.new("Daily", "D", PeriodLength.daily)
    print(d)

    w = Habit.new("Weakly", "W", PeriodLength.weakly)
    print(w)

    print()
    print()
    print()

    # TODO: Should this be disallowed?
    # Mypy doesn't allow it already, but works fine if just executing
    # t = Habit("Test", "T", "Test")
    # print(t)

    app = HabitTracker(StorageKind.org, "habits.org")

    app.save()

    Tui().run()
