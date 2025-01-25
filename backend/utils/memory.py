# backend/utils/memory.py
class Memory:
    def __init__(self):
        self.user_messages = []
        self.ai_messages = []
        self.ai_thoughts = []
        self.message_explanation = []
        self.conversation_state = {
            'topic': 'general',
            'emotion': 'neutral',
        }

    def add_user_message(self, message):
        self.user_messages.append(message)
        if len(self.user_messages) > 10:
            self.user_messages.pop(0)

    def add_ai_message(self, message):
        self.ai_messages.append(message)
        if len(self.ai_messages) > 10:
            self.ai_messages.pop(0)

    def get_context(self):
        context = []
        for user_msg, ai_msg in zip(self.user_messages, self.ai_messages):
            context.append({"role": "user", "content": user_msg})
            context.append({"role": "assistant", "content": ai_msg})
        return context


    def set_conversation_state(self, key, value):
        self.conversation_state[key] = value

    def get_conversation_state(self):
        return self.conversation_state



    def add_ai_thoughts(self, message):
        self.ai_thoughts.append(message)
        if len(self.ai_thoughts) > 3:
            self.ai_thoughts.pop(0)

    def get_ai_thoughts(self):
        context = []
        for thought, in zip(self.ai_thoughts):
            context.append({"ai_ai_thoughts": thought})
        return context

    def add_explan_mgs(self, message):
        self.message_explanation.append(message)
        if len(self.message_explanation) > 3:
            self.message_explanation.pop(0)

    def get_explan_mgs(self):
        context = []
        for expl_msg, in zip(self.message_explanation):
            context.append({"message_explanation": expl_msg})
        return context


memory = Memory()
