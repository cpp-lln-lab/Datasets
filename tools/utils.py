
"""Utility functions for tools."""

from typing import Any
import pandas as pd
from pathlib import Path
from warnings import warn


def new_dataset(name: str) -> dict[str, str | int | bool | list[str]]:
    return {
        "name": name,
        "nb_subjects": "n/a",
        "has_participant_tsv": "n/a",
        "has_participant_json": "n/a",
        "participant_columns": "n/a",
        "has_phenotype_dir": "n/a",
        "modalities": "n/a",
        "tasks": "n/a",
        # "raw": f"{URL_GIN}{name}",
        "fmriprep": "n/a",
        "freesurfer": "n/a",
        "mriqc": "n/a",
    }

def init_dataset() -> dict[str, list[Any]]:
    return {
        "name": [],
        "nb_subjects": [],  # usually the number of subjects folder in raw dataset
        "has_participant_tsv": [],
        "has_participant_json": [],
        "participant_columns": [],
        "has_phenotype_dir": [],
        "modalities": [],
        "sessions": [],  # list of sessions if exist
        "tasks": [],
        # "raw": [],  # link to raw dataset
        "fmriprep": [],  # link to fmriprep dataset if exists
        "freesurfer": [],  # link to freesurfer dataset if exists
        "mriqc": [],  # link to mriqc dataset if exists
    }
    
def is_known_bids_modality(modality: str) -> bool:
    KNOWN_MODALITIES = [
        "anat",
        "dwi",
        "func",
        "perf",
        "fmap",
        "beh",
        "meg",
        "eeg",
        "ieeg",
        "pet",
        "micr",
        "nirs",
        "motion",
    ]
    return modality in KNOWN_MODALITIES
    
def list_modalities(bids_pth: Path, sessions: list[str]) -> list[str]:
    pattern = "sub-*/ses-*/*" if sessions else "sub-*/*"
    sub_dirs = [v.name for v in bids_pth.glob(pattern) if v.is_dir()]
    modalities = [v for v in set(sub_dirs) if is_known_bids_modality(v)]
    return list(set(modalities))

def list_data_files(bids_pth: Path, sessions: list[str]) -> list[str]:
    """Return the list of files in BIDS raw."""
    pattern = "sub-*/ses-*/*/*" if sessions else "sub-*/*/*"
    return [v.name for v in bids_pth.glob(pattern) if "task-" in v.name]

def list_tasks(bids_pth: Path, sessions: list[str]) -> list[str]:
    files = list_data_files(bids_pth, sessions)
    tasks = [f.split("task-")[1].split("_")[0] for f in files]
    tasks = list(set(tasks))
    return tasks

def get_nb_subjects(pth: Path) -> int:
    return len(list_participants_in_dataset(pth))

def has_participant_tsv(pth: Path) -> tuple[bool, bool, str | list[str]]:
    tsv_status = bool((pth / "participants.tsv").exists())
    json_status = bool((pth / "participants.json").exists())
    if tsv_status:
        return tsv_status, json_status, list_participants_tsv_columns(pth / "participants.tsv")
    else:
        return tsv_status, json_status, "n/a"
    
def list_participants_tsv_columns(participant_tsv: Path) -> list[str]:
    """Return the list of columns in participants.tsv."""
    try:
        df = pd.read_csv(participant_tsv, sep="\t")
        return df.columns.tolist()
    except pd.errors.ParserError:
        warn(f"Could not parse: {participant_tsv}")
        return ["cannot be parsed"]

def list_datasets_in_dir(
    datasets: dict[str, list[Any]], path: Path, debug: bool
) -> dict[str, list[Any]]:
    print(f"Listing datasets in {path}")

    raw_datasets = sorted(list(path.glob("*raw")))

    # derivatives = known_derivatives()

    for i, dataset_pth in enumerate(raw_datasets):
        if debug and i > 10:
            break

        dataset_name = dataset_pth.name
        print(f" {dataset_name}")

        dataset = new_dataset(dataset_name)
        dataset["nb_subjects"] = get_nb_subjects(dataset_pth)

        if dataset["nb_subjects"] == 0:
            continue

        sessions = list_sessions(dataset_pth)
        dataset["sessions"] = sessions

        modalities = list_modalities(dataset_pth, sessions=sessions)
        if any(
            mod in modalities
            for mod in ["func", "eeg", "ieeg", "meg", "beh", "perf", "pet", "motion"]
        ):
            tasks = list_tasks(dataset_pth, sessions=sessions)
            check_task(tasks, modalities, sessions, dataset_pth)
            dataset["tasks"] = sorted(tasks)
        dataset["modalities"] = sorted(modalities)

        tsv_status, json_status, columns = has_participant_tsv(dataset_pth)
        dataset["has_participant_tsv"] = tsv_status
        dataset["has_participant_json"] = json_status
        dataset["participant_columns"] = columns
        dataset["has_phenotype_dir"] = bool((dataset_pth / "phenotype").exists())

        # dataset = add_derivatives(dataset, dataset_pth, derivatives)

        if dataset["name"] in datasets["name"]:
            raise ValueError(f"dataset {dataset['name']} already in datasets")

        for keys in datasets:
            datasets[keys].append(dataset[keys])

    return datasets

def list_sessions(dataset_pth: Path) -> list[str]:
    sessions = [v.name.replace("ses-", "") for v in dataset_pth.glob("sub-*/ses-*") if v.is_dir()]
    return sorted(list(set(sessions)))

def check_task(
    tasks: list[str], modalities: list[str], sessions: list[str], dataset_pth: Path
) -> None:
    """Check if tasks are present in dataset with modalities that can have tasks."""
    if (
        any(mod in modalities for mod in ["func", "eeg", "ieeg", "meg", "beh", "motion"])
        and not tasks
    ):
        warn(
            f"no tasks found in {dataset_pth} "
            f"with modalities {modalities} "
            f"and files {list_data_files(dataset_pth, sessions)}"
        )
        
def list_participants_in_dataset(data_pth: Path) -> list[str]:
    return [x.name for x in data_pth.iterdir() if x.is_dir() and x.name.startswith("sub-")]