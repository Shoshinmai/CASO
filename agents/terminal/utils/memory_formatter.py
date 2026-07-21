from agents.terminal.models import (
    ActiveTaskMemory,
    ExecutionMemory,
    ThreadMemory,
)


def format_runtime_memory(
    active_memory: ActiveTaskMemory,
    execution_memory: ExecutionMemory,
    thread_memory: ThreadMemory,
) -> str:
    """
    Convert runtime memory into a planner-friendly text block.
    """

    sections: list[str] = []

    # -----------------------------------------
    # Known Facts
    # -----------------------------------------

    if active_memory.known_facts:
        sections.append("## Known Facts")

        for fact in active_memory.known_facts:
            sections.append(f"- {fact.statement}")

    # -----------------------------------------
    # Resources
    # -----------------------------------------

    if active_memory.discovered_resources:
        sections.append("")
        sections.append("## Discovered Resources")

        for resource in active_memory.discovered_resources:
            sections.append(
                f"- [{resource.type.value}] {resource.identifier}"
            )

    # -----------------------------------------
    # Completed Work
    # -----------------------------------------

    if active_memory.completed_work:
        sections.append("")
        sections.append("## Completed Work")

        for item in active_memory.completed_work:
            sections.append(f"- {item}")

    # -----------------------------------------
    # Pending Work
    # -----------------------------------------

    if active_memory.unresolved_needs:
        sections.append("")
        sections.append("## Pending Work")

        for item in active_memory.unresolved_needs:
            sections.append(f"- {item}")

    # -----------------------------------------
    # Execution Summary
    # -----------------------------------------

    if execution_memory.tool_history:
        sections.append("")
        sections.append("## Tool History")

        for tool in execution_memory.tool_history[-5:]:
            sections.append(f"- {tool}")

    # -----------------------------------------
    # Thread Summary
    # -----------------------------------------

    if thread_memory.summary:
        sections.append("")
        sections.append("## Thread Summary")
        sections.append(thread_memory.summary)

    if not sections:
        return "No runtime memory available."

    return "\n".join(sections)

def format_active_memory(
    active_memory: ActiveTaskMemory
) -> str:
    sections: list[str] = []
    
    # -----------------------------------------
    # Known Facts
    # -----------------------------------------

    if active_memory.known_facts:
        sections.append("## Known Facts")

        for fact in active_memory.known_facts:
            sections.append(f"- {fact.statement}")

    # -----------------------------------------
    # Resources
    # -----------------------------------------

    if active_memory.discovered_resources:
        sections.append("")
        sections.append("## Discovered Resources")

        for resource in active_memory.discovered_resources:
            sections.append(
                f"- [{resource.type.value}] {resource.identifier}"
            )

    # -----------------------------------------
    # Completed Work
    # -----------------------------------------

    if active_memory.completed_work:
        sections.append("")
        sections.append("## Completed Work")

        for item in active_memory.completed_work:
            sections.append(f"- {item}")

    # -----------------------------------------
    # Pending Work
    # -----------------------------------------

    if active_memory.unresolved_needs:
        sections.append("")
        sections.append("## Pending Work")

        for item in active_memory.unresolved_needs:
            sections.append(f"- {item}")
    
    if not sections:
        return "No runtime memory available."

    return "\n".join(sections)