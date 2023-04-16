import pytest
from datetime import datetime, timedelta

from habit import PeriodLength, Habit

@pytest.fixture
def test_habit():
    dt = datetime(2023, 4, 6)
    return Habit("Test", "T", PeriodLength.daily, dt, 0, False, [], None)

@pytest.fixture
def completed_times():
    return [datetime(2023, 4, 6), datetime(2023, 4, 7), datetime(2023, 4, 8)]

def test_new(test_habit):
    name = "Test"
    symbol = "T"
    period_length = PeriodLength.daily
    assert test_habit.name == "Test"
    assert test_habit.symbol == "T"
    assert test_habit.period_length == PeriodLength.daily
    assert test_habit.creation_date == datetime(2023, 4, 6)
    assert test_habit.streak_length == 0
    assert test_habit.longest_streak == None
    assert test_habit.completed == False
    assert test_habit.completed_times == []

def test_str(test_habit):
    test_str = f"""[T] Test:
Period: Daily
Completed: False
Streak: 0
Longest Streak: None
Creation Date: 2023-04-06 00:00:00"""
    assert test_str == str(test_habit)

def test_repr(test_habit):
    name = "Test"
    symbol = "T"
    period_length = PeriodLength.daily
    h = Habit.new(name, symbol, period_length)
    assert "T Test: Daily, Streak: 0" == repr(h)

def test_lcd(test_habit, completed_times):
    assert test_habit.last_completed_date() == None
    
    test_habit.completed_times = completed_times

    assert test_habit.last_completed_date() == datetime(2023, 4, 8)

    completed_times.append(datetime(2023, 4, 5))
    test_habit = Habit("Test", "T", PeriodLength.daily, datetime(2023, 4, 6), 9, False, completed_times, None)
    assert test_habit.last_completed_date() == datetime(2023, 4, 8)

def test_complete_new(test_habit):
    test_habit.complete()
    assert test_habit.completed == True
    assert len(test_habit.completed_times) == 1
    assert test_habit.longest_streak.length == 1
    assert test_habit.longest_streak.begin == test_habit.longest_streak.end

def test_complete_interrupted_streak(test_habit, completed_times):
    test_habit.completed_times = completed_times
    test_habit.complete()
    assert test_habit.completed == True
    assert test_habit.longest_streak.length == 1
    assert test_habit.longest_streak.begin == test_habit.longest_streak.end

def test_complete_continue_streak(test_habit, completed_times):
    before = datetime.now() - timedelta(hours=12)

    test_habit.completed_times.append(before)
    test_habit.streak_length = 1
    test_habit.complete()

    assert test_habit.completed == True
    assert test_habit.streak_length == 2
    assert test_habit.longest_streak.begin != test_habit.longest_streak.end
