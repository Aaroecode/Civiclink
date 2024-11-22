# app/services/chat_flow.py
from utils.session_manager import SessionManager

class ChatFlow:
    steps = {}

    def __init__(self, session_manager: SessionManager):
        self.current_step = 'start'
        self.session_manager = session_manager
        self.steps = {}

    def step(self, step_name):
        """Decorator to register a function as a step in the flow."""
        def decorator(func):
            self.steps[step_name] = func
            print(step_name, "Registered")
            return func
        return decorator

    def next_step(self, user_id, user_input):
        """Call the function of the current step and move to the next."""
        
        current_step = self.session_manager.get_user_step(user_id)
        self.current_step = current_step
        step_func = self.steps.get(self.current_step)
        next_step_name = "start"
        if step_func:
            next_step_name = step_func(user_input)
            self.session_manager.set_user_step(user_id, next_step_name)
        return next_step_name

chat_flow = ChatFlow(SessionManager())

