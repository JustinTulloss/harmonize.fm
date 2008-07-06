# Pick a set implementation - sets.Set on Python 2.3, set on Python 2.4.
import sys
if sys.version_info[0] == 2 and sys.version_info[1] <= 3:
    import sets
    set = sets.Set
    frozenset = sets.ImmutableSet
else:
    # Leave the built-in implementations.
    pass
