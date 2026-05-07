from typing import TypedDict, Optional, Dict, Any, List

class AgentState(TypedDict):
    
    user_input: str
    system_state: Optional[Dict[str, Any]]

    plan: Optional[List[Dict[str, Any]]]
    validation_error: Optional[str]
    critic_decision: Optional[str]
    critic_feedback: Optional[str]
    # optional tracking
    revise_count: int