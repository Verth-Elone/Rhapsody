# Copyright (c) Peter Majko.

from rhapsody.core.data_formatting import pretty

def tst():
    return 'a'

test_dict = {
            'a': 0,
            1: 'b',
            pretty: [2, 3, (tst, )]
        }

print(pretty(test_dict))