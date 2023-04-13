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

    app = HabitTracker(StorageKind.org, "habits.org")

    app.save()

    Tui().run()
