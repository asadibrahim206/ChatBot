class ConversationStore:
    def __init__(self):
        self._sessions = {}

    def add_message(self, session_id, role, text):
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({"role": role, "text": text})

    def get_history(self, session_id):
        return list(self._sessions.get(session_id, []))

