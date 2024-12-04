import os
import time
import requests

#looks like the env vars were not loading for mem0. It's trying to write to file system
os.environ["MEM0_DIR"] = "/tmp"
os.environ["MEM0_API_KEY"] = "REPLACE_WITH_KEY"

from mem0 import MemoryClient
from multion.client import MultiOn
from openai import OpenAI

from prompts import GENERAL_PROMPT

#TODO: should be unique to each user
USER_ID = "cher"

class OpenTableAgent:
    def __init__(self):
        """Initialize the OpenTable agent."""
        self.multion = MultiOn(
            api_key=os.environ["MULTION_API_KEY"]
        )
        self.done = False
        self.messages = []
        self.screenshot = ""
        self.task = ""
        self.openAIClient = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.memory = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
    
        # Create a session with MultiOn
        create_response = self.multion.sessions.create(
            url="https://opentable.com", mode="fast", local=True
        )
        self.session_id = create_response.session_id

    def close_session(self):
        self.multion.sessions.close(self.session_id)

    def get_gpt_response(self, user_input: str) -> str:
        print(self.messages)
        """Generate a GPT response."""
        messages = [{"role": "user", "content": GENERAL_PROMPT}]
        if not self.task:
            self.task = user_input
            self.messages.append({"role": "user", "content": f"The Task given to you is: {self.task}"})
        else:
            self.messages.append({"role": "user", "content": user_input})
            if self.screenshot:
                messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "This is the current state of the booking assistant.",
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

    def _get_relevant_memories(self, query: str) -> str:
        """Retrieve relevant memories based on the user's query."""
        memories = self.memory.search(query, user_id=USER_ID)
        return '\n'.join(mem['memory'] for mem in memories)

    def _create_prompt(self, question: str, relevant_memories: str) -> str:
        """Create a prompt to send to the MultiOn API."""
        if relevant_memories:
            return f"Question: {question}\nMy preferences: {relevant_memories}"
        else:
            return f"Question: {question}"

    def ask_question(self, question: str):
        """Process a user query and execute the corresponding action."""
        relevant_memories = self._get_relevant_memories(question)
        prompt = self._create_prompt(question, relevant_memories)
        response = self.get_gpt_response(prompt)
        is_valid_response = False
        while is_valid_response == False:
            try:
                action_func, action_arg, explanation = self.validate_and_process_response(response)
                print(f"""
                    Action Details:
                    ---------------
                    Function   : {action_func}
                    Argument   : {action_arg}
                    Explanation: {explanation}
                """)
                is_valid_response = True
            except ValueError:
                response = self.get_gpt_response("Invalid response format. Expecting Action: <action> <actionDescriptions>\nExplanation: <explanation>. Please try again.")

        if action_func == "submit":
            self.done = True
        elif action_func == "booking_assistant":
            step_response = self.multion.sessions.step(
                session_id=self.session_id, cmd=action_arg, include_screenshot=True
            )
            print(step_response.screenshot)
            self.messages.append(
                {"role": "user", "content": f"Assistant response: {step_response.message}"}
            )
        elif action_func == "clarify":
            self.messages.append(
                {"role": "assistant", "content": f"I need help in order to fullfill the request: {action_arg}"}
            )
        elif action_func == "save_preference":
            self.memory.add([{"role": "user", "content": action_arg}], user_id=USER_ID)

        return explanation, self.done
