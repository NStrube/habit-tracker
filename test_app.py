import pytest
from datetime import timedelta, datetime
from habit import Habit, PeriodLength, StreakPeriod
from storage import StorageKind, OrgStorage
from app import HabitTracker

@pytest.fixture
def test_tracker(tmp_path):
    tracker = HabitTracker(StorageKind.org, str(tmp_path) + ".org")
    now = datetime.now().replace(microsecond=0)
    h = [\
            Habit("Test 1", "1", PeriodLength.daily, now, 0, False, [], None),\
            Habit("Test 2", "2", PeriodLength.weekly, now, 1, True, [now], StreakPeriod(1, now, now)),\
            Habit("Test 3", "3", PeriodLength.daily, now, 1, False, [now], StreakPeriod(1, now, now)),\
         ]
    tracker.storage.save(h)
    tracker.habits = tracker.storage.read()
    return tracker

def test_new(tmp_path):
    test_tracker = HabitTracker(StorageKind.org, str(tmp_path) + ".org")
    assert test_tracker.habits == []
    assert type(test_tracker.storage) == OrgStorage

def test_update(test_tracker):
    t = test_tracker
    assert len(test_tracker.habits) == 3
    test_tracker.habits[1].completed_times[0] = test_tracker.habits[1].completed_times[0] - timedelta(days=2)
    t = test_tracker
    t.update()
    assert t.habits[0] == test_tracker.habits[0]
    assert t.habits[1] != test_tracker.habits[1]
    assert t.habits[2] == test_tracker.habits[2]
