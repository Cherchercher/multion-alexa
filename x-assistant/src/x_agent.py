import os
import time
import requests

from multion.client import MultiOn
from prompts import GENERAL_PROMPT, CRITIQUE_NOTE
from openai import OpenAI
from instrospective_agent import get_introspective_agent_with_self_reflection

class XAgent:
    def __init__(self):
        """Initialize the X agent."""
        self.multion = MultiOn(
            api_key=os.environ["MULTION_API_KEY"]
        )
        self.done = False
        self.messages = []
        self.screenshot = ""
        self.idea = ""
        self.task = ""
        self.openAIClient = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.instrospectiveAgent = get_introspective_agent_with_self_reflection()

        # Create a session with MultiOn
        create_response = self.multion.sessions.create(
            url="https://x.com", mode="fast", local=True
        )
        self.session_id = create_response.session_id

    def close_session(self):
        self.multion.sessions.close(self.session_id)

    def get_gpt_response(self, user_input: str, use_history: str = False) -> str:
        print(self.messages)
        """Generate a GPT response."""
        messages = [{"role": "user", "content": GENERAL_PROMPT}]
        if not self.task:
            self.task = user_input
            self.messages.append({"role": "user", "content": f"The Task given to you is: {self.task}"})
        else:
            self.messages.append({"role": "user", "content": user_input})
            if self.idea:
                messages.append({"role": "user", "content": f"The current idea is: {self.idea}"})
            if self.screenshot:
                messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "This is the current state of the Programmer Intern.",
                                },
                                {"type": "image_url", "image_url": {"url": self.screenshot}},
                            ],
                        }
                    )

        # Add previous messages if valid
        if isinstance(self.messages, list):
            for message in self.messages:
                if isinstance(message, dict):
                    messages.append(message)
                else:
                    raise ValueError(f"Invalid message format: {message}")

        chat_completion = self.openAIClient.chat.completions.create(
                messages=messages,
                model="gpt-4o",
        )
        response = chat_completion.choices[0].message.content

        try:
            chat_completion = self.openAIClient.chat.completions.create(
                messages=messages,
                model="gpt-4o",
            )
            response = chat_completion.choices[0].message.content
            return response
        except Exception:
            return f"Error generating response: {e}"

    def validate_and_process_response(self, response):
        """
        Validates the format of the response string and processes it into components.
        Format: 
        - Action: <action> <actionDescription>
        - Explanation: <explanation>
        
        Returns:
            A dictionary with 'action_func', 'action_arg', and 'explanation' if valid.
            Raises a ValueError if the format is invalid.
        """
        try:
            # Split into action and explanation
            action, explanation = response.split("Explanation: ", 1)
            action = action.split("Action: ", 1)[1].strip()
            
            # Extract action_func and action_arg
            action_func, action_arg = action.split(" ", 1)
            
            # Return the parsed components
            return action_func, action_arg, explanation.strip()
        except (ValueError, IndexError) as e:
            raise ValueError("The response string does not satisfy the required format.") from e

    def ask_question(self, prompt: str):
        """Process a user query and execute the corresponding action."""
        response = self.get_gpt_response(prompt)
        try:
            action_func, action_arg, explanation = self.validate_and_process_response(response)
        except ValueError:
            response = self.get_gpt_response("Invalid response format. Expecting Action: <action> <actionDescriptions>\nExplanation: <explanation>. Please try again.")
        print("original response: {}".format(response))
        # # There's a bug in llamaIndex's instrospectiveAgent: local variable 'original_response' referenced before assignment
        revised_response = await self.instrospectiveAgent.achat(f"Here is the text to critique: {response}. Here is the criteria: {CRITIQUE_NOTE}")
        response = revised_response.response
        print("revised response: {}".format(response))

        if action_func == "submit":
            self.done = True
        elif action_func == "brainstorm":
            self.idea = action_arg
            print("Idea updated:", self.idea)
        elif action_func == "writing_assistant":
            step_response = self.multion.sessions.step(
                session_id=self.session_id, cmd=action_arg, include_screenshot=True
            )
            print(step_response.screenshot)
            self.messages.append(
                {"role": "user", "content": f"Assistant response: {step_response.message}"}
            )
        elif action_func == "clarify":
            print("needs clarification...", action, action_arg)
            self.messages.append(
                {"role": "assistant", "content": f"I need help in order to fullfill the request: {action_arg}"}
            )

        return explanation, self.done
