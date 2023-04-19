import csv

import attrs
import requests
from tqdm import tqdm

from . import root
from .models import Dunder, Group, Status, save_dunders

group_map = {
    "CALLABLE COVE": Group.CALLABLE_COVE,
    "MODULE MESA": Group.MODULE_MESA,
    "ASYNC ISLE": Group.ASYNC_ISLE,
    "THE NEST": Group.THE_NEST,
    "FEATURE REEF": Group.FEATURE_REEF,
    "SYSTEMS SWAMP": Group.SYSTEMS_SWAMP,
    "MOLTED MEMORY MT (python2)": Group.MOLTED_MEMORY_MT,
    "META PLANE": Group.META_PLANE,
    "LIBRARY LAGOON": Group.LIBRARY_LAGOON,
    "CONTAINER COAST": Group.CONTAINER_COAST,
    "MATH LAND": Group.MATH_LAND,
    "C CLIFF": Group.C_CLIFF,
    "MIDDLE EARTH": Group.MIDDLE_EARTH,
}

status_map = {
    "TO DO": Status.TO_DO,
    "IN PROGRESS": Status.IN_PROGRESS,
    "UNDER REVIEW": Status.IN_REVIEW,
    "DONE": Status.DONE,
}


@attrs.define
class Row:
    name: str = ""
    desc: str = ""
    status: str = ""
    assignee: str = ""
    pr: str = ""


# dunders_path = root / "mCoding All Dunders Video - Sheet.csv"
dunders_path = root / "dunders.csv"
dunders_sheet = (
    "https://docs.google.com/spreadsheets/d/"
    "1-45UeKKMCePmTDLptT2zpI4L-jikmsCnve_lwOMyeuY/export?format=csv"
)


def download_csv() -> None:
    with requests.get(dunders_sheet) as r, open(dunders_path, "wb") as file:
        file.write(r.content)


def read_csv() -> list[Dunder]:
    # Download as "dunders.csv" to the root of this repo:
    # https://docs.google.com/spreadsheets/d/1-45UeKKMCePmTDLptT2zpI4L-jikmsCnve_lwOMyeuY
    dunders: list[Dunder] = []
    with open(dunders_path) as file:
        reader = csv.reader(file)
        skip = 2
        last: Row | None = None
        group: Group | None = None
        for read_row in tqdm(reader, desc="Reading CSV"):
            if skip:
                skip -= 1
                continue

            row = Row(*read_row)

            if not row.name:
                continue

            if not row.status:
                group = group_map[row.name]
                continue

            if group is None:
                raise ValueError

            if row.desc == "↑":
                if last is None:
                    raise ValueError
                row.desc = last.desc

            if row.assignee == "—":
                row.assignee = ""

            dunder = Dunder(
                name=f"`{row.name}`", status=status_map[row.status], group=group
            )

            if row.desc:
                dunder.description = row.desc

            if row.assignee:
                dunder.assignees = [row.assignee]

            if row.pr:
                dunder.pr = int(row.pr[1:])

            last = row
            dunders.append(dunder)

    return dunders


def main() -> None:
    # dunders = read_csv()
    # save_dunders(dunders)
    pass


if __name__ == "__main__":
    main()
