import pytest
from datetime import datetime

from storage import OrgStorage
from habit import Habit, PeriodLength, StreakPeriod

@pytest.fixture
def test_org(tmp_path):
    return OrgStorage(str(tmp_path.with_suffix(".org")))

def test_not_org_file():
    # TODO: When implemented exceptions
    pass

def test_read_nofile(test_org):
    assert test_org.read() == []

def test_read_empty(test_org):
    open(test_org.file, "x") 
    assert test_org.read() == []

def test_save_and_read(test_org):
    now = datetime.now().replace(microsecond=0)
    h = [\
            Habit("Test 1", "1", PeriodLength.daily, now, 0, False, [], None),\
            Habit("Test 2", "2", PeriodLength.weekly, now, 1, True, [now], StreakPeriod(1, now, now)),\
            Habit("Test 3", "3", PeriodLength.daily, now, 1, False, [now], StreakPeriod(1, now, now)),\
         ]
    test_org.save(h)
    t = test_org.read()
    assert len(h) == len(t)
    for idx in range(len(h)):
        a = h[idx]
        b = t[idx]
        assert a.name == b.name
        assert a.symbol == b.symbol
        assert a.completed == b.completed
        assert a.completed_times == b.completed_times

        # Why does this pass but the else branch only doesn't???
        if a.longest_streak is not None:
            assert a.longest_streak.length == b.longest_streak.length
            assert a.longest_streak.begin == b.longest_streak.begin
            assert a.longest_streak.end == b.longest_streak.end
        else:
            assert a.longest_streak == b.longest_streak

        assert a.streak_length == b.streak_length
        assert a.period_length == b.period_length
        assert a.creation_date == b.creation_date
    # assert h == test_org.read()

# TODO: Probably more complex unit tests needed but eh
