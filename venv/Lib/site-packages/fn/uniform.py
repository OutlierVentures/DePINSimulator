from sys import version_info

# Syntax sugar to deal with Python 2/Python 3
# differences: this one will return generator
# even in Python 2.*
if version_info[0] == 2:
    from itertools import izip as zip, imap as map, ifilter as filter

filter = filter
map = map
zip = zip

if version_info[0] == 3:
    from functools import reduce

reduce = reduce
range = xrange if version_info[0] == 2 else range

if version_info[0] == 2:
    from itertools import ifilterfalse as filterfalse
    from itertools import izip_longest as zip_longest
else:
    from itertools import filterfalse
    from itertools import zip_longest

# Using or importing the ABCs from 'collections' instead of from
# 'collections.abc' is deprecated, and in 3.8 it will stop working.
if version_info[0] <= 3 and version_info[1] < 8:
    from collections import Iterable
else:
    from collections.abc import Iterable
