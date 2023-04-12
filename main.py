from habit import Habit, PeriodLength
from storage import StorageKind
from app import HabitTracker

# Mypy not recognizing Exception
if __name__ == "__main__":
    d = Habit("Daily", "D", PeriodLength.daily)
    print(d)

    w = Habit("Weakly", "W", PeriodLength.weakly)
    print(w)

    # TODO: Should this be disallowed?
    # Mypy doesn't allow it already, but works fine if just executing
    # t = Habit("Test", "T", "Test")
    # print(t)

    app = HabitTracker(StorageKind.org, "habits.org")

    try:
        app.save()
    except:
        pass
