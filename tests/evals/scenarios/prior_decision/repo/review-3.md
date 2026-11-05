# Code review 3

F1. hours.py is_active: "last 30 days" must cover 30 dates, but the code accepts 31. A log exactly 30 days ago should be inactive. Change the window.

F2. hours.py remaining_hours: remaining_hours(5, 8) returns 0, so an exceeded budget looks exactly exhausted.
