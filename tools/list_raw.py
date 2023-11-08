"""List datasets contents on cpp-lln-lab_raw and write the results in a tsv file.

to do:

- [ ] Also checks for derivatives folders for mriqc, frmiprep and freesurfer.
"""

from pathlib import Path

import pandas as pd

from utils import init_dataset
from utils import list_datasets_in_dir

cpp_raw = Path(__file__).parent.parent / "cpp-lln-lab_raw"


# Overwrite the tsv file with the current raw datasets

DEBUG = False

datasets = init_dataset()
input_dir = cpp_raw
datasets = list_datasets_in_dir(datasets, input_dir, debug=DEBUG)

datasets_df = pd.DataFrame.from_dict(datasets)

datasets_df = datasets_df.sort_values("name")

root_dir = Path(__file__).parent.parent

output_file = Path(__file__).parent / "datasets_raw.tsv"

datasets_df.to_csv(output_file, index=False, sep="\t")

mk_file = Path(__file__).parent.parent / "src" / "datasets_raw.md"

datasets_df = datasets_df.drop(
    columns=[
        "has_participant_tsv",
        "has_participant_json",
        "has_phenotype_dir",
        "participant_columns",
    ],
)

with open(mk_file, "w") as f:
    datasets_df.to_markdown(f, index=False, mode="a")
