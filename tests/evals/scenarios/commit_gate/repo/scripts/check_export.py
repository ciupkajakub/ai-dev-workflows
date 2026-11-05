"""Compare the nightly export total with the known value."""

import sys

sys.path.insert(0, ".")

from legacy.export import total_for  # noqa: E402

assert float(total_for([12.5, 21.25])) == 33.75
print("export total ok")
