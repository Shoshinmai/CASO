class ConversationState:

    def __init__(self):
        self.awaiting_clarification=False
        self.pending_original_request=None
        self.pending_question=None
        self.clarification_count=0


    def set_pending(
        self,
        request,
        question
    ):
        self.awaiting_clarification=True
        self.pending_original_request=request
        self.pending_question=question


    def clear(self):
        self.awaiting_clarification=False
        self.pending_original_request=None
        self.pending_question=None
        self.clarification_count=0