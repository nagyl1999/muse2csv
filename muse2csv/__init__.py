"""
muse2csv
---------

Convert GE MUSE XML ECG exports to CSV format.

"""

__version__ = "1.0.0"
__author__  = "Levente Nagy"
__license__ = "MIT"

from converter import muse_to_csv

__all__ = [
    "muse_to_csv"
]