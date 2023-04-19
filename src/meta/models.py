import json
from enum import Enum
from pathlib import PurePosixPath

import attrs
import cattrs
from cattrs.preconf.json import configure_converter as configure_converter_json

from . import root


class Group(Enum):
    CALLABLE_COVE = "Callable Cove"
    MODULE_MESA = "Module Mesa"
    ASYNC_ISLE = "Async Isle"
    THE_NEST = "The Nest"
    FEATURE_REEF = "Feature Reef"
    SYSTEMS_SWAMP = "Systems Swamp"
    MOLTED_MEMORY_MT = "Molted Memory Mt (Python 2)"
    META_PLANE = "Meta Plane"
    LIBRARY_LAGOON = "Library Lagoon"
    CONTAINER_COAST = "Container Coast"
    MATH_LAND = "Math Land"
    C_CLIFF = "C Cliff"
    MIDDLE_EARTH = "Middle Earth"


src = PurePosixPath("src")
group_folder: dict[Group, PurePosixPath] = {
    Group.CALLABLE_COVE: src / "callable-cove",
    Group.MODULE_MESA: src / "module-mesa",
    Group.ASYNC_ISLE: src / "async-isle",
    Group.THE_NEST: src / "the-nest",
    Group.FEATURE_REEF: src / "feature-reef",
    Group.SYSTEMS_SWAMP: src / "systems-swamp",
    Group.MOLTED_MEMORY_MT: src / "molted-memory-mt",
    Group.META_PLANE: src / "meta-plane",
    Group.LIBRARY_LAGOON: src / "library-lagoon",
    Group.CONTAINER_COAST: src / "container-coast",
    Group.MATH_LAND: src / "math-land",
    Group.C_CLIFF: src / "c-cliff",
    Group.MIDDLE_EARTH: src / "middle-earth",
}


class Status(Enum):
    TO_DO = "Todo"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    DONE = "Done"


@attrs.define
class Dunder:
    name: str
    status: Status = Status.TO_DO
    group: Group | None = None
    description: str | None = None
    issue: int | None = None
    pr: int | None = None
    assignees: list[str] | None = None
    files: list[PurePosixPath] | None = None


c = cattrs.Converter()
configure_converter_json(c)
c.register_structure_hook(PurePosixPath, lambda v, t: t(v))  # type: ignore
c.register_unstructure_hook(PurePosixPath, lambda p: p.as_posix())

dunders_json = root / "dunders.json"


def load_dunders() -> list[Dunder]:
    with open(dunders_json) as file:
        return c.structure(json.load(file), list[Dunder])


def save_dunders(dunders: list[Dunder]) -> None:
    with open(dunders_json, "w") as file:
        json.dump(c.unstructure(dunders), file, indent=4)
