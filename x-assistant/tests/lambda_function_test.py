import unittest
from unittest.mock import MagicMock, patch
from lambda_function import AmazonShoppingIntentHandler, LaunchRequestHandler, CatchAllExceptionHandler

class TestAmazonShoppingSkill(unittest.TestCase):
    @patch("lambda_function.ai_assistant_with_memory")
    def test_amazon_shopping_intent_handler(self, mock_agent):
        # Mock AmazonShoppingAgent
        mock_agent.ask_question.return_value = ("Here are the best deals.", "DONE")

        # Mock handler input
        mock_input = MagicMock()
        mock_input.request_envelope.request.intent.slots = {"query": MagicMock(value="Find wireless headphones")}
        mock_input.attributes_manager.session_attributes = {}

        handler = AmazonShoppingIntentHandler()
        response = handler.handle(mock_input)

        self.assertIn("Here are the best deals.", response.output_speech.ssml)
        mock_agent.ask_question.assert_called_once()

    def test_launch_request_handler(self):
        mock_input = MagicMock()
        handler = LaunchRequestHandler()
        response = handler.handle(mock_input)

        self.assertIn("Hi, I'm your Amazon Shopping Assistant!", response.output_speech.ssml)

    def test_catch_all_exception_handler(self):
        mock_input = MagicMock()
        handler = CatchAllExceptionHandler()
        response = handler.handle(mock_input, Exception("Test Exception"))

        self.assertIn("Sorry, I had trouble doing what you asked.", response.output_speech.ssml)


if __name__ == "__main__":
    unittest.main()
