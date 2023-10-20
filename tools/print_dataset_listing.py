"""Take the listing of raw datasets
and turns it into a markdown document with a series of markdown tables."""

from pathlib import Path
import pandas as pd
from bids import BIDSLayout

column_order = [
    "name",
    "description",
    "datatypes",
    "suffixes",
    "link to full data",
    "maintained by",
]