# app/services/chat_flow.py
from utils.session_manager import SessionManager
from utils.logging import global_logger
from utils import errors

session = SessionManager()

class ChatFlow:

    def __init__(self, session_manager: SessionManager):
        self.current_step = 'start'
        self.session_manager = session_manager
        self.steps = {}

    def step(self, step_name):
        """Decorator to register a function as a step in the flow."""
        def decorator(func):
            self.steps[step_name] = func
            global_logger.info(f"Step: {step_name} Registered Successfully")
            return func
        return decorator

    def next_step(self, user_id, user_input):
        """Call the function of the current step and move to the next."""
        
        current_step = self.session_manager.get_user_step(user_id)
        step_func = self.steps.get(current_step)
        if step_func:
            next_step_name = step_func(user_input)
            self.session_manager.set_user_step(user_id, next_step_name)
            return next_step_name
        else:
            raise errors.MissingStep(f"Step for user {user_id} not found")


chat_flow = ChatFlow(session)