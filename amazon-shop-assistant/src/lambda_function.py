import os
import logging
import json
import requests
from ask_sdk_core.dispatch_components import AbstractExceptionHandler, AbstractRequestHandler
from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.services.directive import SendDirectiveRequest, Header, SpeakDirective
from ask_sdk_model import Response
import ask_sdk_core.utils as ask_utils
from amazon_shopping_agent import AmazonShoppingAgent

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize Amazon Shopping Agent
ai_assistant = AmazonShoppingAgent()

# Request Handlers
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = (
            "Hi, I'm your Amazon Shopping Assistant! "
            "I can help you with your Amazon orders. Just say something like, "
            "add an iPhone 13 charger to my shopping cart, and I'll take care of it for you!"
        )
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["chat_history"] = []
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class AmazonShoppingIntentHandler(AbstractRequestHandler):
    """Handler for Amazon Shopping Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AmazonShoppingIntent")(handler_input)

    def handle(self, handler_input):
        # Extract user query
        query = handler_input.request_envelope.request.intent.slots["query"].value
        session_attr = handler_input.attributes_manager.session_attributes
        
        # Play step-by-step instructions
        # Ideally we'd be able to complete the browse action within timeout, or stepping without user acknowledgement.
        if "step_instruction_played" not in session_attr:
            session_attr["step_instruction_played"] = True
            get_progressive_response(
                handler_input,
                "I'll address your request step by step. Please let me know if any adjustments are needed, otherwise, say ok."
            )
        
        # Process query with AmazonShoppingAgent
        message, done = ai_assistant.ask_question(query)
        
        session_attr["chat_history"].append((query, message))
        return (
            handler_input.response_builder
                .speak(message)
                .ask(message if done == False else "Do you need help with anything else?")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handler."""
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print(exception)
        logger.error(exception, exc_info=True)
        speak_output = "Sorry, I had trouble doing what you asked. Please try again."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        return (
            ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
            ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)
        )

    def handle(self, handler_input):
        ai_assistant.close_session()
        speak_output = "Goodbye! Thank you for using Amazon Shopping Assistant."
        return handler_input.response_builder.set_should_end_session(True).speak(speak_output).response


# Helper Functions
def get_progressive_response(handler_input, speech):
    """Send a progressive response to the user."""
    request_id_holder = handler_input.request_envelope.request.request_id
    directive_header = Header(request_id=request_id_holder)
    directive_request = SendDirectiveRequest(
        header=directive_header,
        directive=SpeakDirective(speech=speech)
    )
    handler_input.service_client_factory.get_directive_service().enqueue(directive_request)

# Skill Builder
sb = StandardSkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AmazonShoppingIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
lambda_handler = sb.lambda_handler()
