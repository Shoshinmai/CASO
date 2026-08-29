from agents.terminal.runtime.events import RuntimeEvent
from agents.terminal.runtime.kernel import RuntimeKernel
from agents.terminal.runtime.modes import RuntimeMode
from agents.terminal.runtime.stages import RuntimeStage
from agents.terminal.runtime.models import RuntimeState


print("\n========== D.6.1 RUNTIME BOUNDARY TEST ==========\n")


runtime_state = RuntimeState(
    mode=RuntimeMode.EXECUTING,
)


print("BEFORE:")
print("MODE :", runtime_state.mode)
print("EVENT:", runtime_state.last_event)


stage = RuntimeKernel.handle_event(
    runtime_state=runtime_state,
    event=RuntimeEvent.EXECUTION_COMPLETED,
)


print("\nAFTER:")
print("MODE :", runtime_state.mode)
print("EVENT:", runtime_state.last_event)
print("ITER :", runtime_state.iteration)
print("STAGE:", stage)


# ==========================================================
# Assertions
# ==========================================================

assert runtime_state.mode == RuntimeMode.REVIEWING

assert (
    runtime_state.last_event
    == RuntimeEvent.EXECUTION_COMPLETED
)

assert runtime_state.iteration == 1

assert stage == RuntimeStage.CRITIC


print("\n========== D.6.1 PASS ==========")
print(
    "Concurrent execution completion correctly enters "
    "the REVIEWING → CRITIC boundary."
)