from collections.abc import Callable
from typing import TypeVar

from agents.terminal.result_processing.models import (
    Fact,
    MemoryUpdateProposal,
    Resource,
)
from agents.terminal.state import TerminalState

T = TypeVar("T")


def append_unique(
    target: list[T],
    incoming: list[T],
    key: Callable[[T], object],
) -> None:
    """
    Append only items whose key does not already exist.
    """

    existing = {
        key(item)
        for item in target
    }

    for item in incoming:
        identifier = key(item)

        if identifier not in existing:
            target.append(item)
            existing.add(identifier)


def mutate_state(
    state: TerminalState,
    proposal: MemoryUpdateProposal,
) -> None:
    """
    Apply a MemoryUpdateProposal to the current TerminalState.

    This function mutates the state in-place.

    Responsibilities
    ----------------
    - Update ActiveTaskMemory
    - Prevent duplicate entries
    - Leave all other memories untouched
    """

    active_memory = state.get("active_memory")
    
    # --------------------------------------------------
    # Completed Work
    # --------------------------------------------------

    append_unique(
        target=active_memory.completed_work,
        incoming=proposal.completed_work,
        key=lambda item: item,
    )

    # --------------------------------------------------
    # Unresolved Needs
    # --------------------------------------------------

    append_unique(
        target=active_memory.unresolved_needs,
        incoming=proposal.unresolved_needs,
        key=lambda item: item,
    )

    # --------------------------------------------------
    # Discovered Resources
    # --------------------------------------------------

    append_unique(
        target=active_memory.discovered_resources,
        incoming=proposal.discovered_resources,
        key=lambda resource: (
            resource.type,
            resource.identifier,
        ),
    )

    # --------------------------------------------------
    # Known Facts
    # --------------------------------------------------

    append_unique(
        target=active_memory.known_facts,
        incoming=proposal.known_facts,
        key=lambda fact: fact.statement,
    )