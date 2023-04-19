import logging
import os
from pathlib import PurePosixPath
from time import sleep
from typing import TypedDict

from dotenv import load_dotenv
from github import Github
from github.Milestone import Milestone
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from .models import Group, group_folder, load_dunders, save_dunders

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
load_dotenv()

# Generate personal access token at
# https://github.com/settings/personal-access-tokens
# with " Read and Write access to administration, issues, and pull requests"
# for the repo
g = Github(os.environ["GITHUB_TOKEN"])
repo = g.get_repo("MicaelJarniac/mcoding-all-dunders")

delay: float | None = 1.0  # Seconds between each API call


def get_root_url() -> str:
    return f"{repo.html_url}/blob/{repo.default_branch}/"


class CreateMilestoneKwargs(TypedDict, total=False):
    title: str
    description: str


def format_path(path: PurePosixPath) -> str:
    return f"[`{str(path)}`]({get_root_url() + str(path)})"


def format_folder(group: Group) -> str | None:
    if (folder := group_folder.get(group)) is not None:
        return f"Folder: {format_path(folder)}"
    return None


def create_milestones() -> None:
    """Create milestones on repo. Run only once ever."""
    for group in tqdm(Group, desc="Creating milestones"):
        kwargs = CreateMilestoneKwargs(title=group.value)
        if formatted_folder := format_folder(group):
            kwargs["description"] = formatted_folder
        repo.create_milestone(**kwargs)
        if delay:
            sleep(delay)


def get_milestones() -> dict[Group, Milestone]:
    """Associate `Milestone` instances to repo milestones.
    `create_milestones()` must have been run once."""
    out: dict[Group, Milestone] = {}
    for milestone in tqdm(repo.get_milestones(), desc="Getting milestones"):
        try:
            group = Group(milestone.title)
        except Exception:
            pass
        else:
            out[group] = milestone
    assert all(m in out for m in Group), "Run `create_milestones()`"
    return out


def sync_dunders(ignore_populated_issues: bool = True) -> None:
    """Populate issue IDs on local dunders database."""
    dunders = load_dunders()
    dunders_map = {dunder.name: dunder for dunder in dunders}
    for issue in tqdm(repo.get_issues(), desc="Populating issues"):
        dunder = dunders_map.get(issue.title)
        if dunder is not None and (not ignore_populated_issues or dunder.issue is None):
            dunder.issue = issue.number
    save_dunders(dunders)


class CreateIssueKwargs(TypedDict, total=False):
    title: str
    body: str
    milestone: Milestone
    assignees: list[str]


def create_issues(update_existing: bool = False, auto_assign: bool = False) -> None:
    """Create issues for dunders.
    Make sure local dunders database is in sync
    (optionally run `sync_dunders()` to be sure).
    """
    with logging_redirect_tqdm():
        milestones = get_milestones()
        dunders = load_dunders()
        for dunder in tqdm(dunders, desc="Creating issues"):
            if not update_existing and dunder.issue is not None:
                continue

            kwargs = CreateIssueKwargs(title=dunder.name)

            desc_parts: list[str] = []

            if group := dunder.group:
                if milestone := milestones.get(group):
                    kwargs["milestone"] = milestone
                if formatted_folder := format_folder(group):
                    desc_parts.append(formatted_folder)

            if files := dunder.files:
                formatted_files = "\n".join(f"- {format_path(file)}" for file in files)
                desc_parts.append(f"Files:\n{formatted_files}")

            if dunder.description:
                desc_parts.append(dunder.description)

            if desc_parts:
                kwargs["body"] = "\n\n".join(desc_parts)

            if auto_assign and (assignees := dunder.assignees):
                kwargs["assignees"] = assignees

            try:
                if dunder.issue is None:
                    issue = repo.create_issue(**kwargs)
                    dunder.issue = issue.number
                    logger.info(f"Created issue {issue.number}")
                else:
                    issue = repo.get_issue(dunder.issue)
                    issue.edit(**kwargs)
                    logger.info(f"Edited issue {issue.number}")
            except Exception as e:
                logger.exception(e)
                break

            if delay:
                sleep(delay)

    save_dunders(dunders)


def associate_prs() -> None:
    """Associate PRs to issues."""
    for dunder in tqdm(load_dunders(), desc="Associating PRs"):
        if (pr_num := dunder.pr) is not None and (
            issue_num := dunder.issue
        ) is not None:
            pr = repo.get_pull(pr_num)
            # Maybe update description with it too
            pr.create_issue_comment(f"Closes #{issue_num}.")
            if delay:
                sleep(delay)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
