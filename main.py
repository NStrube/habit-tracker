"""This module is the entry point for the habit tracker."""
from tui import Tui

# TODO:
# ╭―――――――――――――――――――――――――――╮
# │                           │
# │    Rewrite It in Rust     │
# │                           │
# ╰―――――――――――――――――――――――――――╯
#
# Or any sane language, really

# Mypy not recognizing Exceptions
# TODO: Cleanup
# TODO: Json storage
# TODO: Use filter() method?

# Maybe at some point
# - Save as, read from
# - Use cLi args
# - Rename habits
# - Better naming
# - Exception (raising and handling?)
if __name__ == "__main__":
    t = Tui()
    t.run()

# NOTE: I do not know if how I document stuff is correct/good.
