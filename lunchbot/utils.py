"""
Utility functions.

:copyright: (c) 2017 by Serhii Shvorob.
:license: MIT, see LICENSE for more details.
"""
import datetime

DAYS_OF_WEEK_UKR = ("понеділок", "вівторок", "середа", "четвер", "п'ятниця", "субота", "неділя")


def day_of_week_ukr():
    """Returns current day of week in Ukrainian."""
    return DAYS_OF_WEEK_UKR[datetime.datetime.now().weekday()]
