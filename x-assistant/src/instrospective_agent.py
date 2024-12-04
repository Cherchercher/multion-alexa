from llama_index.agent.introspective import IntrospectiveAgentWorker
from llama_index.agent.introspective import (
    ToolInteractiveReflectionAgentWorker,
)

from llama_index.llms.openai import OpenAI
from llama_index.agent.openai import OpenAIAgentWorker
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core import ChatPromptTemplate

from llama_index.agent.introspective import SelfReflectionAgentWorker


def get_introspective_agent_with_self_reflection(
    verbose=False, with_main_worker=False
):
    """Helper function for building introspective agent using self reflection.

    Steps:

    1. Define the `SelfReflectionAgentWorker`
        1a. Construct `SelfReflectionAgentWorker` using .from_defaults()

    2. Construct `IntrospectiveAgent`
        3a. Construct `IntrospectiveAgentWorker` using .from_defaults()
        3b. Construct `IntrospectiveAgent` using .as_agent()
    """

    # 1a.
    self_reflection_agent_worker = SelfReflectionAgentWorker.from_defaults(
        llm=OpenAI("gpt-4-turbo-preview"),
        verbose=verbose,
    )

    if with_main_worker:
        main_agent_worker = OpenAIAgentWorker.from_tools(
            tools=[], llm=OpenAI("gpt-4-turbo-preview"), verbose=True
        )
    else:
        main_agent_worker = None
    # 3a.
    introspective_worker_agent = IntrospectiveAgentWorker.from_defaults(
        reflective_agent_worker=self_reflection_agent_worker,
        main_agent_worker=main_agent_worker,
        verbose=verbose,
    )

    chat_history = [
        ChatMessage(
            content="You are a social media manager excelled in copy wrtiting. Given a text, evaluate its potential to go viral. If it's good, return as it is, otherwise, return revised text.",
            role=MessageRole.SYSTEM,
        )
    ]

    # 3b.
    return introspective_worker_agent.as_agent(
        chat_history=chat_history, verbose=verbose
    )