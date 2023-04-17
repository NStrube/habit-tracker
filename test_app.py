import pytest
from datetime import timedelta, datetime
from habit import Habit, PeriodLength, StreakPeriod
from storage import StorageKind, OrgStorage
from app import HabitTracker

@pytest.fixture
def habits():
    now = datetime.now().replace(microsecond=0)
    return [\
            Habit("Test 1", "1", PeriodLength.daily, now, 0, False, [], None),\
            Habit("Test 2", "2", PeriodLength.weekly, now, 1, True, [now], StreakPeriod(1, now, now)),\
            Habit("Test 3", "3", PeriodLength.daily, now, 1, False, [now], StreakPeriod(1, now, now)),\
    ]

@pytest.fixture
def test_tracker(tmp_path, habits):
    tracker = HabitTracker(StorageKind.org, str(tmp_path) + ".org")
    tracker.storage.save(habits)
    tracker.habits = tracker.storage.read()
    return tracker

def test_new(tmp_path):
    test_tracker = HabitTracker(StorageKind.org, str(tmp_path) + ".org")
    assert test_tracker.habits == []
    assert type(test_tracker.storage) == OrgStorage

def test_update(habits, test_tracker):
    assert len(test_tracker.habits) == len(habits)
    test_tracker.habits[1].completed_times[0] = test_tracker.habits[1].completed_times[0] - timedelta(days=2)
    test_tracker.update()
    # Have to use strings, otherwise doesn't compare correctly??
    assert str(habits[0]) == str(test_tracker.habits[0])
    assert str(habits[1]) != str(test_tracker.habits[1])
    assert str(habits[2]) == str(test_tracker.habits[2])

def test_get_completed(test_tracker, habits):
    t = test_tracker.get_completed_str()
    h = [repr(h) for h in habits if h.completed == True]
    assert t == h

def test_get_uncompleted(test_tracker, habits):
    t = test_tracker.get_uncompleted_str()
    h = [repr(h) for h in habits if h.completed == False]
    assert t == h

def test_complete(habits, test_tracker):
    test_tracker.complete(repr(habits[0]))
    assert test_tracker.habits[0].completed == True
    assert len(test_tracker.habits[0].completed_times) > len(habits[0].completed_times)

def test_add_habit(test_tracker):
    test_tracker.addHabit("Test 4", "t", PeriodLength.daily)
    assert len(test_tracker.habits) == 4
    assert repr(test_tracker.habits[3]) == "t Test 4: Daily, Streak: 0"

def test_delete_habit(habits, test_tracker):
    test_tracker.deleteHabit(repr(habits[1]))
    assert str(habits[0]) == str(test_tracker.habits[0])
    assert str(habits[2]) == str(test_tracker.habits[1])

def test_get_habits(habits, test_tracker):
    h = test_tracker.getHabit(repr(habits[0]))
    assert h is not None
    assert str(habits[0]) == str(h)

def test_nr_daily_habits(test_tracker):
    assert test_tracker.nrDailyHabits() == 2

def test_nr_weekly_habits(test_tracker):
    assert test_tracker.nrWeeklyHabits() == 1

def test_current_longest_streak(habits, test_tracker):
    h = habits[1]
    assert test_tracker.currentLongestStreak() == f"{h.name}: {h.streak_length}"

def test_current_longest_daily_streak(habits, test_tracker):
    h = habits[2]
    assert test_tracker.currentLongestDailyStreak() == f"{h.name}: {h.streak_length}"

def test_current_longest_weekly_streak(habits, test_tracker):
    h = habits[1]
    assert test_tracker.currentLongestWeeklyStreak() == f"{h.name}: {h.streak_length}"

def test_longest_ever_streak(habits, test_tracker):
    h = habits[1]
    assert test_tracker.longestEverStreak() == f"{h.name}: {h.longest_streak}"

def test_longest_ever_daily_streak(habits, test_tracker):
    h = habits[2]
    assert test_tracker.longestEverDailyStreak() == f"{h.name}: {h.longest_streak}"

def test_longest_ever_weekly_streak(habits, test_tracker):
    h = habits[1]
    assert test_tracker.longestEverWeeklyStreak() == f"{h.name}: {h.longest_streak}"

def test_get_daily(habits, test_tracker):
    d = test_tracker.get_daily()
    assert len(d) == 2
    assert str(d[0]) == str(habits[0])
    assert str(d[1]) == str(habits[2])

def test_get_weekly(habits, test_tracker):
    d = test_tracker.get_weekly()
    assert len(d) == 1
    assert str(d[0]) == str(habits[1])

def test_name_unique(habits, test_tracker):
    assert test_tracker.check_name_unique("Test 1") == False
    assert test_tracker.check_name_unique("Test 2") == False
    assert test_tracker.check_name_unique("Test 3") == False
    assert test_tracker.check_name_unique("Test 4") == True

def test_names_unique(test_tracker):
    assert test_tracker.check_names_unique() == True
